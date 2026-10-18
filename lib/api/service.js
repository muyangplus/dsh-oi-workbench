/**
 * Workbench host service: problem discovery, Python tool execution, and local
 * OJ/contest persistence.
 *
 * The service owns every effectful operation behind the `/oi-workbench/api`
 * routes. It never stores credentials: an OJ profile keeps only the NAME of the
 * environment variable that carries the password or session cookie.
 *
 * @module @muyangplus/dsh-oi-workbench/api/service
 */
import { execFile, spawn } from 'node:child_process';
import { closeSync, existsSync, openSync } from 'node:fs';
import { mkdir, readFile, readdir, realpath, rename, stat, unlink, writeFile } from 'node:fs/promises';
import { homedir, tmpdir } from 'node:os';
import { basename, dirname, isAbsolute, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
/** Package root, resolved from `lib/api/service.js`. */
const PACKAGE_ROOT = fileURLToPath(new URL('../../', import.meta.url));
/** Default location of the bundled skill resources. */
const DEFAULT_SKILLS_DIR = join(PACKAGE_ROOT, 'skills', 'oi-workbench');
/** Skill id this plugin serves. */
const SKILL_NAME = 'oi-workbench';
/** Timeout of every spawned Python tool, in milliseconds. */
const COMMAND_TIMEOUT_MS = 120_000;
/** Kept tail length of each captured stream, to bound host memory. */
const MAX_OUTPUT_CHARS = 200_000;
/** Timeout of one OJ reachability probe, in milliseconds. */
const OJ_TEST_TIMEOUT_MS = 8_000;
/** Deepest directory level scanned for problem packages, relative to the root. */
const MAX_SCAN_DEPTH = 4;
/** Description used when `SKILL.md` carries no usable frontmatter description. */
const FALLBACK_SKILL_DESCRIPTION = 'OI 出题工作台：知识点锁定、数据构造、本地评测、打包与 Hydro/HOJ 发布';
/** Raised for a request the panel got wrong; the route layer maps it to HTTP 400. */
export class BadRequestError extends Error {
    constructor(message) {
        super(message);
        this.name = 'BadRequestError';
    }
}
/**
 * Return whether a value is a plain object record.
 * @param value - candidate value.
 * @returns whether it is a non-null, non-array object.
 */
function isRecord(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
}
/**
 * Read a required non-empty string field.
 * @param value - candidate value.
 * @param field - field name used in the error message.
 * @returns the trimmed string.
 * @throws {BadRequestError} when the value is absent or empty.
 */
function requireString(value, field) {
    if (typeof value !== 'string' || value.trim() === '') {
        throw new BadRequestError(`缺少字段或类型错误: ${field}`);
    }
    return value;
}
/**
 * Keep the tail of an oversized captured stream and mark the elision.
 * @param text - captured output.
 * @returns text no longer than {@link MAX_OUTPUT_CHARS}.
 */
function truncate(text) {
    if (text.length <= MAX_OUTPUT_CHARS)
        return text;
    return `…(输出过长，已截断前 ${text.length - MAX_OUTPUT_CHARS} 字符)\n${text.slice(-MAX_OUTPUT_CHARS)}`;
}
/**
 * Read one JSON file, treating a missing or corrupt file as absent.
 * @param file - absolute path.
 * @returns parsed JSON, or `undefined`.
 */
async function readJsonFile(file) {
    try {
        return JSON.parse(await readFile(file, 'utf8'));
    }
    catch {
        return undefined;
    }
}
/**
 * Assemble one {@link CommandResult} from an execFile-shaped outcome.
 * @param command - executable name or path.
 * @param args - argv after the executable.
 * @param startedAt - epoch milliseconds when the run started.
 * @param timeout - enforced timeout, reported on a timeout failure.
 * @param error - execFile error, or `null` on success.
 * @param stdout - captured standard output.
 * @param stderr - captured standard error.
 * @returns the normalized command result.
 */
function commandResult(command, args, startedAt, timeout, error, stdout, stderr) {
    const timedOut = error !== null
        && (error.killed === true
            || error.signal !== undefined);
    const rawCode = error?.code;
    const exitCode = error === null ? 0 : typeof rawCode === 'number' ? rawCode : -1;
    let errText = stderr;
    if (timedOut)
        errText += `\n[timeout] 命令超过 ${timeout}ms 被终止`;
    else if (error !== null && errText.trim() === '')
        errText = error.message;
    return {
        ok: error === null,
        exitCode,
        stdout: truncate(stdout),
        stderr: truncate(errText),
        durationMs: Date.now() - startedAt,
        argv: [command, ...args],
    };
}
/**
 * Whether a spawn failure means the host forbids piped stdio.
 *
 * The DSH Windows sandbox denies pipe creation for child processes, so
 * `execFile` — which always pipes — fails with `EPERM` before the program ever
 * starts. That is the documented sandbox boundary, not a tool failure, so the
 * capture moves to regular files instead.
 * @param error - the spawn/execFile failure.
 * @returns whether the fallback capture should be attempted.
 */
function isPipeDenial(error) {
    const code = error?.code;
    return code === 'EPERM' || code === 'EACCES';
}
/**
 * Run one command with regular-file capture instead of pipes.
 *
 * Identical contract to the `execFile` path (argv, timeout, truncation), but the
 * child writes standard output and standard error into session temp files that
 * are read back and removed afterwards.
 * @param command - executable name or path.
 * @param args - argv after the executable.
 * @param options - working directory and timeout.
 * @param startedAt - epoch milliseconds when the run started.
 * @returns the captured result.
 */
function runCommandWithFiles(command, args, options, startedAt) {
    const timeout = options.timeoutMs ?? COMMAND_TIMEOUT_MS;
    const token = `${process.pid}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const stdoutFile = join(tmpdir(), `oiwb-${token}.out`);
    const stderrFile = join(tmpdir(), `oiwb-${token}.err`);
    return (async () => {
        let stdoutFd;
        let stderrFd;
        try {
            stdoutFd = openSync(stdoutFile, 'w');
            stderrFd = openSync(stderrFile, 'w');
        }
        catch (error) {
            return commandResult(command, args, startedAt, timeout, error instanceof Error ? error : new Error(String(error)), '', '');
        }
        return await new Promise((resolveResult) => {
            let settled = false;
            let timedOut = false;
            let spawnError = null;
            const releaseFiles = async () => {
                try {
                    closeSync(stdoutFd);
                }
                catch { /* already closed */ }
                try {
                    closeSync(stderrFd);
                }
                catch { /* already closed */ }
                const stdoutText = await readFile(stdoutFile, 'utf8').catch(() => '');
                const stderrText = await readFile(stderrFile, 'utf8').catch(() => '');
                await unlink(stdoutFile).catch(() => undefined);
                await unlink(stderrFile).catch(() => undefined);
                return [stdoutText, stderrText];
            };
            let child;
            try {
                child = spawn(command, [...args], {
                    ...(options.cwd === undefined ? {} : { cwd: options.cwd }),
                    env: options.env ?? process.env,
                    stdio: ['ignore', stdoutFd, stderrFd],
                    windowsHide: true,
                });
            }
            catch (error) {
                const spawnFailure = error instanceof Error ? error : new Error(String(error));
                void releaseFiles().then(([stdoutText, stderrText]) => {
                    resolveResult(commandResult(command, args, startedAt, timeout, spawnFailure, stdoutText, stderrText));
                });
                return;
            }
            const timer = setTimeout(() => {
                timedOut = true;
                child.kill();
            }, timeout);
            const finish = async (exitCode) => {
                if (settled)
                    return;
                settled = true;
                clearTimeout(timer);
                const [stdoutText, stderrText] = await releaseFiles();
                if (timedOut) {
                    const timeoutError = Object.assign(new Error(`命令超过 ${timeout}ms`), { killed: true });
                    resolveResult(commandResult(command, args, startedAt, timeout, timeoutError, stdoutText, stderrText));
                    return;
                }
                if (spawnError !== null) {
                    resolveResult(commandResult(command, args, startedAt, timeout, spawnError, stdoutText, stderrText));
                    return;
                }
                if (exitCode !== null && exitCode !== 0) {
                    const exitError = Object.assign(new Error(`命令退出码 ${exitCode}`), { code: exitCode });
                    resolveResult(commandResult(command, args, startedAt, timeout, exitError, stdoutText, stderrText));
                    return;
                }
                resolveResult(commandResult(command, args, startedAt, timeout, null, stdoutText, stderrText));
            };
            child.once('error', (error) => {
                spawnError = error;
                void finish(null);
            });
            child.once('close', (code) => {
                void finish(code);
            });
        });
    })();
}
/**
 * Run one command asynchronously and capture its bounded output.
 *
 * Prefers `execFile`; when the host denies piped stdio (see
 * {@link isPipeDenial}) the same command is captured through temp files, so the
 * panel keeps working inside a confined sandbox.
 * @param command - executable name or path.
 * @param args - argv after the executable.
 * @param options - working directory and timeout.
 * @returns the captured result; never rejects for a non-zero exit or a timeout.
 */
function runCommand(command, args, options = {}) {
    const timeout = options.timeoutMs ?? COMMAND_TIMEOUT_MS;
    const startedAt = Date.now();
    return new Promise((resolveResult) => {
        const fallback = () => {
            void runCommandWithFiles(command, args, options, startedAt).then(resolveResult);
        };
        const finish = (error, stdout, stderr) => {
            resolveResult(commandResult(command, args, startedAt, timeout, error, stdout, stderr));
        };
        try {
            execFile(command, [...args], {
                ...(options.cwd === undefined ? {} : { cwd: options.cwd }),
                env: options.env ?? process.env,
                timeout,
                maxBuffer: 8 * 1024 * 1024,
                encoding: 'utf8',
                windowsHide: true,
            }, (error, stdout, stderr) => {
                if (error !== null && isPipeDenial(error)) {
                    fallback();
                    return;
                }
                finish(error, String(stdout ?? ''), String(stderr ?? ''));
            });
        }
        catch (error) {
            if (isPipeDenial(error)) {
                fallback();
                return;
            }
            finish(error instanceof Error ? error : new Error(String(error)), '', '');
        }
    });
}
/**
 * Split a Markdown `---` frontmatter block from its body.
 * @param text - complete `SKILL.md` text.
 * @returns parsed frontmatter plus body.
 */
export function parseSkillMarkdown(text) {
    const normalized = text.replace(/\r\n/g, '\n');
    if (!normalized.startsWith('---\n'))
        return { body: text, metadata: {} };
    const end = normalized.indexOf('\n---', 4);
    if (end < 0)
        return { body: text, metadata: {} };
    const block = normalized.slice(4, end);
    const bodyStart = normalized.indexOf('\n', end + 4);
    const body = bodyStart < 0 ? '' : normalized.slice(bodyStart + 1);
    const metadata = {};
    for (const line of block.split('\n')) {
        const match = /^([A-Za-z0-9_-]+)\s*:\s*(.*)$/.exec(line);
        if (match === null)
            continue;
        let value = match[2].trim();
        if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
            value = value.slice(1, -1);
        }
        metadata[match[1]] = value;
    }
    const name = metadata.name;
    const description = metadata.description?.replace(/\s+/g, ' ').trim();
    return {
        ...(name !== undefined && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name) ? { name } : {}),
        ...(description !== undefined && description !== '' ? { description } : {}),
        body,
        metadata,
    };
}
/**
 * Host-side workbench operations shared by every route and tool.
 */
export class WorkbenchService {
    /** Absolute workbench root. */
    rootDir;
    /** Directory holding persisted OJ/contest configuration. */
    homeDir;
    /** Bundled skill resource directory. */
    skillsDir;
    /** Python executable used for the bundled tools. */
    python;
    /** Command override used to reveal a directory. */
    openDir;
    constructor(options) {
        this.rootDir = resolve(options.rootDir);
        const home = options.homeDir ?? process.env.OIWB_HOME ?? join(homedir(), '.dsh-oi-workbench');
        this.homeDir = resolve(home);
        this.skillsDir = resolve(options.skillsDir ?? DEFAULT_SKILLS_DIR);
        this.python = options.python ?? 'python';
        this.openDir = options.openDir;
    }
    /**
     * Full panel snapshot: problems, OJ profiles, contests, and version facts.
     * @returns the current workbench state.
     */
    async state() {
        return {
            root: this.rootDir,
            version: await this.version(),
            skill: SKILL_NAME,
            skillRegistered: existsSync(join(this.skillsDir, 'SKILL.md')),
            problems: await this.problems(),
            oj: await this.readOjConfig(),
            contests: await this.readContests(),
        };
    }
    /**
     * Discover problem packages under the root.
     * @returns one entry per directory holding `spec.json`, ordered by name.
     */
    async problems() {
        const directories = await this.scanProblemDirs();
        return Promise.all(directories.map(async (path) => ({
            name: relative(this.rootDir, path).split(sep).join('/'),
            path,
            badges: await this.badgesOf(path),
        })));
    }
    /**
     * Read the plugin version from the package manifest.
     * @returns the version string, or `''` when unreadable.
     */
    async version() {
        const manifest = await readJsonFile(join(PACKAGE_ROOT, 'package.json'));
        return isRecord(manifest) && typeof manifest.version === 'string' ? manifest.version : '';
    }
    /**
     * Execute one panel action.
     * @param action - the action payload from the panel.
     * @returns the action outcome; failures are reported as `ok: false` unless the request itself is invalid.
     * @throws {BadRequestError} for an unknown action or a malformed field.
     */
    async act(action) {
        if (!isRecord(action))
            throw new BadRequestError('action 必须是 JSON 对象');
        switch (action.kind) {
            case 'check': return this.check(action);
            case 'build': return this.build(action);
            case 'judge': return this.judge(action);
            case 'open': return this.open(action);
            case 'oj-save': return this.ojSave(action);
            case 'oj-delete': return this.ojDelete(action);
            case 'oj-set-active': return this.ojSetActive(action);
            case 'oj-test': return this.ojTest(action);
            case 'contest-save': return this.contestSave(action);
            case 'contest-delete': return this.contestDelete(action);
            case 'contest-build': return this.contestBuild(action);
            default:
                throw new BadRequestError(`未知的 action kind: ${String(action.kind)}`);
        }
    }
    // ── actions ───────────────────────────────────────────────────────────────
    /** Run `tools/check_problem.py` against one problem directory. */
    async check(action) {
        const dir = await this.requireProblemDir(action.dir);
        const script = this.requireScript(join(this.skillsDir, 'tools', 'check_problem.py'));
        const command = await this.runPython(script, [dir]);
        const label = basename(dir);
        return {
            ok: command.ok,
            message: command.ok ? `题目检查通过：${label}` : `题目检查失败：${label}（exit ${command.exitCode}）`,
            command,
        };
    }
    /** Build the Hydro and/or HOJ package zips next to the problem directory. */
    async build(action) {
        const dir = await this.requireProblemDir(action.dir);
        const target = action.target;
        if (target !== 'hydro' && target !== 'hoj' && target !== 'both') {
            throw new BadRequestError(`未知的构建目标: ${String(target)}`);
        }
        const parent = dirname(dir);
        const name = basename(dir);
        const results = [];
        const produced = [];
        if (target === 'hydro' || target === 'both') {
            const script = this.requireScript(join(this.skillsDir, 'generator', 'build_package.py'));
            const out = join(parent, `${name}.zip`);
            const result = await this.runPython(script, [dir, '--out', out]);
            results.push(result);
            if (result.ok)
                produced.push(out);
        }
        if (target === 'hoj' || target === 'both') {
            const script = this.requireScript(join(this.skillsDir, 'generator', 'build_hoj_package.py'));
            const out = join(parent, `${name}-hoj.zip`);
            const result = await this.runPython(script, [dir, '--out', out]);
            results.push(result);
            if (result.ok)
                produced.push(out);
        }
        const failed = results.filter((result) => !result.ok);
        const command = failed[0] ?? results[results.length - 1];
        return {
            ok: failed.length === 0,
            message: failed.length === 0
                ? `构建完成：${produced.join('、')}`
                : `构建失败（exit ${failed.map((result) => result.exitCode).join('/')}）：${name}`,
            command,
        };
    }
    /** Run `generator/local_judge.py` against one source file. */
    async judge(action) {
        const dir = await this.requireProblemDir(action.dir);
        const script = this.requireScript(join(this.skillsDir, 'generator', 'local_judge.py'));
        const source = typeof action.source === 'string' && action.source.trim() !== '' ? action.source.trim() : 'std/std.cpp';
        const args = [dir, '--source', source];
        const limit = Number(action.timeLimitMs);
        if (Number.isFinite(limit) && limit > 0)
            args.push('--time', String(Math.round(limit)));
        const command = await this.runPython(script, args);
        const score = /\[result\]\s*([0-9]+\s*\/\s*\d+)/.exec(command.stdout);
        const label = basename(dir);
        return {
            ok: command.ok,
            message: command.ok
                ? `本地评测完成：${label}${score === null ? '' : `，得分 ${score[1].replace(/\s+/g, '')}`}`
                : `本地评测失败：${label}（exit ${command.exitCode}）`,
            command,
        };
    }
    /** Reveal one directory in the platform file manager. */
    async open(action) {
        const dir = await this.requireInsideDir(action.dir);
        await this.reveal(dir);
        return { ok: true, message: `已打开：${dir}` };
    }
    /** Upsert one OJ connection profile (secrets are never persisted). */
    async ojSave(action) {
        const profile = normalizeOjProfile(action.profile);
        const oj = await this.readOjConfig();
        const profiles = [...oj.profiles];
        const index = profiles.findIndex((entry) => entry.id === profile.id);
        if (index >= 0)
            profiles[index] = profile;
        else
            profiles.push(profile);
        await this.writeOjConfig({ profiles, activeProfileId: oj.activeProfileId === '' ? profile.id : oj.activeProfileId });
        return {
            ok: true,
            message: `已保存 OJ 配置：${profile.name || profile.id}`,
            state: await this.state(),
        };
    }
    /** Delete one OJ profile by id. */
    async ojDelete(action) {
        const id = requireString(action.id, 'id');
        const oj = await this.readOjConfig();
        const profiles = oj.profiles.filter((entry) => entry.id !== id);
        if (profiles.length === oj.profiles.length)
            throw new BadRequestError(`未找到 OJ 配置: ${id}`);
        const activeProfileId = oj.activeProfileId === id ? (profiles[0]?.id ?? '') : oj.activeProfileId;
        await this.writeOjConfig({ profiles, activeProfileId });
        return { ok: true, message: `已删除 OJ 配置：${id}`, state: await this.state() };
    }
    /** Mark one OJ profile as the default; an empty id clears the selection. */
    async ojSetActive(action) {
        const id = typeof action.id === 'string' ? action.id.trim() : '';
        const oj = await this.readOjConfig();
        if (id !== '' && !oj.profiles.some((entry) => entry.id === id)) {
            throw new BadRequestError(`未找到 OJ 配置: ${id}`);
        }
        await this.writeOjConfig({ profiles: oj.profiles, activeProfileId: id });
        return { ok: true, message: id === '' ? '已清除默认 OJ 配置' : `默认 OJ 配置：${id}`, state: await this.state() };
    }
    /** Probe one OJ profile with an unauthenticated GET; only the HTTP status is reported. */
    async ojTest(action) {
        const id = requireString(action.id, 'id');
        const oj = await this.readOjConfig();
        const profile = oj.profiles.find((entry) => entry.id === id);
        if (profile === undefined)
            throw new BadRequestError(`未找到 OJ 配置: ${id}`);
        if (profile.base.trim() === '')
            throw new BadRequestError(`OJ 配置缺少 base URL: ${id}`);
        let url;
        try {
            url = new URL(profile.base);
        }
        catch {
            throw new BadRequestError(`OJ 配置的 base URL 无效: ${profile.base}`);
        }
        if (url.protocol !== 'http:' && url.protocol !== 'https:') {
            throw new BadRequestError(`OJ 配置的 base URL 必须是 http(s): ${profile.base}`);
        }
        const startedAt = Date.now();
        try {
            const response = await fetch(url, {
                method: 'GET',
                redirect: 'follow',
                signal: AbortSignal.timeout(OJ_TEST_TIMEOUT_MS),
            });
            void response.body?.cancel().catch(() => undefined);
            return {
                ok: true,
                message: `${profile.name || profile.id} 可达：HTTP ${response.status}（${Date.now() - startedAt}ms）`,
            };
        }
        catch (error) {
            return {
                ok: false,
                message: `${profile.name || profile.id} 连接失败：${error instanceof Error ? error.message : String(error)}`,
            };
        }
    }
    /** Upsert one saved contest plan. */
    async contestSave(action) {
        const raw = action.contest;
        if (!isRecord(raw))
            throw new BadRequestError('contest 必须是 JSON 对象');
        const id = requireString(raw.id, 'contest.id');
        const title = requireString(raw.title, 'contest.title');
        if (!Array.isArray(raw.problems))
            throw new BadRequestError('contest.problems 必须是字符串数组');
        const problems = raw.problems.map((entry) => this.toRootRelative(requireString(entry, 'contest.problems[]')));
        const contests = [...await this.readContests()];
        const entry = { id, title, problems, updatedAt: new Date().toISOString() };
        const index = contests.findIndex((candidate) => candidate.id === id);
        if (index >= 0)
            contests[index] = entry;
        else
            contests.push(entry);
        await this.writeContests(contests);
        return { ok: true, message: `已保存比赛：${title}`, state: await this.state() };
    }
    /** Delete one saved contest plan by id. */
    async contestDelete(action) {
        const id = requireString(action.id, 'id');
        const contests = await this.readContests();
        const kept = contests.filter((candidate) => candidate.id !== id);
        if (kept.length === contests.length)
            throw new BadRequestError(`未找到比赛: ${id}`);
        await this.writeContests(kept);
        return { ok: true, message: `已删除比赛：${id}`, state: await this.state() };
    }
    /** Build every deliverable of one saved contest with `generator/build_contest.py`. */
    async contestBuild(action) {
        const id = requireString(action.id, 'id');
        const contests = await this.readContests();
        const contest = contests.find((candidate) => candidate.id === id);
        if (contest === undefined)
            throw new BadRequestError(`未找到比赛: ${id}`);
        if (contest.problems.length === 0)
            throw new BadRequestError(`比赛没有关联题目: ${id}`);
        const dirs = [];
        for (const problem of contest.problems) {
            dirs.push(await this.requireProblemDir(problem));
        }
        const script = this.requireScript(join(this.skillsDir, 'generator', 'build_contest.py'));
        const out = join(this.rootDir, 'dist', sanitizeSegment(contest.id));
        const command = await this.runPython(script, ['--contest', contest.title, '--problems', ...dirs, '--out', out]);
        return {
            ok: command.ok,
            message: command.ok ? `比赛构建完成：${contest.title}（${out}）` : `比赛构建失败：${contest.title}（exit ${command.exitCode}）`,
            command,
        };
    }
    // ── discovery ─────────────────────────────────────────────────────────────
    /**
     * Walk the root for directories holding `spec.json`.
     * @returns absolute paths, ordered by relative name.
     */
    async scanProblemDirs() {
        const found = [];
        const walk = async (dir, depth) => {
            if (depth > MAX_SCAN_DEPTH)
                return;
            let entries;
            try {
                entries = await readdir(dir, { withFileTypes: true });
            }
            catch {
                return;
            }
            entries.sort((left, right) => left.name.localeCompare(right.name));
            for (const entry of entries) {
                if (!entry.isDirectory())
                    continue;
                const full = join(dir, entry.name);
                if (existsSync(join(full, 'spec.json')))
                    found.push(full);
                else
                    await walk(full, depth + 1);
            }
        };
        await walk(this.rootDir, 1);
        return found;
    }
    /**
     * Read the four file-presence and two counting badges of one problem.
     * @param dir - absolute problem directory.
     * @returns the badge set.
     */
    async badgesOf(dir) {
        const spec = await readJsonFile(join(dir, 'spec.json'));
        const cases = isRecord(spec) && Array.isArray(spec.cases) ? spec.cases : [];
        let hasData = false;
        try {
            const entries = await readdir(join(dir, 'data'));
            hasData = entries.some((entry) => entry.endsWith('.in'));
        }
        catch {
            hasData = false;
        }
        return {
            hasProblemMd: existsSync(join(dir, 'problem.md')),
            hasSolution: existsSync(join(dir, 'solution', 'solution.md')),
            hasStd: existsSync(join(dir, 'std', 'std.cpp')),
            hasSpec: true,
            caseCount: cases.length,
            hasData,
        };
    }
    // ── path validation ───────────────────────────────────────────────────────
    /**
     * Resolve a panel-supplied path and require it to be an existing directory inside the root.
     * @param input - absolute path or path relative to the root.
     * @returns the canonical absolute path.
     * @throws {BadRequestError} when the path escapes the root or does not exist.
     */
    async requireInsideDir(input) {
        const raw = requireString(input, 'dir');
        return this.canonicalInside(raw);
    }
    /**
     * Resolve a directory that must also be a problem package.
     * @param input - absolute path or path relative to the root.
     * @returns the canonical absolute path.
     * @throws {BadRequestError} when it is outside the root or holds no `spec.json`.
     */
    async requireProblemDir(input) {
        const dir = await this.requireInsideDir(input);
        if (!existsSync(join(dir, 'spec.json'))) {
            throw new BadRequestError(`不是题目目录（缺少 spec.json）: ${dir}`);
        }
        return dir;
    }
    /**
     * Canonicalize a path and prove it stays inside the workbench root.
     * @param input - absolute path or path relative to the root.
     * @returns the real absolute path.
     * @throws {BadRequestError} when outside the root, missing, or not a directory.
     */
    async canonicalInside(input) {
        const candidate = isAbsolute(input) ? resolve(input) : resolve(this.rootDir, input);
        let real;
        try {
            real = await realpath(candidate);
        }
        catch {
            throw new BadRequestError(`路径不存在: ${input}`);
        }
        if (!await this.isInsideRoot(real)) {
            throw new BadRequestError(`路径不在工作台根目录内: ${input}`);
        }
        if (!(await stat(real)).isDirectory())
            throw new BadRequestError(`不是目录: ${input}`);
        return real;
    }
    /**
     * Lexically convert a path to root-relative form without requiring it to exist.
     * @param input - absolute path or path relative to the root.
     * @returns slash-separated path relative to the root.
     * @throws {BadRequestError} when it escapes the root.
     */
    toRootRelative(input) {
        const candidate = isAbsolute(input) ? resolve(input) : resolve(this.rootDir, input);
        if (!this.lexicallyInsideRoot(candidate)) {
            throw new BadRequestError(`路径不在工作台根目录内: ${input}`);
        }
        const rel = relative(this.rootDir, candidate);
        return rel === '' ? '.' : rel.split(sep).join('/');
    }
    /**
     * Whether an absolute path is lexically inside the root (no existence check).
     * @param candidate - absolute candidate path.
     * @returns whether it is the root or below it.
     */
    lexicallyInsideRoot(candidate) {
        return isInside(this.rootDir, candidate);
    }
    /**
     * Whether a canonical path is inside the canonical root.
     * @param candidate - real absolute path.
     * @returns whether it is the root or below it.
     */
    async isInsideRoot(candidate) {
        let rootReal;
        try {
            rootReal = await realpath(this.rootDir);
        }
        catch {
            rootReal = this.rootDir;
        }
        return isInside(rootReal, candidate);
    }
    /**
     * Locate a bundled Python script and require it to exist.
     * @param script - absolute script path.
     * @returns the same path.
     * @throws {Error} when the packaged skill resources are incomplete.
     */
    requireScript(script) {
        if (!existsSync(script))
            throw new Error(`缺少内置脚本: ${script}`);
        return script;
    }
    // ── command execution ─────────────────────────────────────────────────────
    /**
     * Run one bundled Python script from the workbench root.
     *
     * The child environment forces UTF-8 stdio: the bundled tools print Chinese
     * progress text, and a redirected Windows console would otherwise emit the
     * ANSI code page and garble the panel log.
     * @param script - absolute script path.
     * @param args - argv after the script path.
     * @returns the captured command result.
     */
    runPython(script, args) {
        const cwd = existsSync(this.rootDir) ? this.rootDir : process.cwd();
        const env = {
            ...process.env,
            PYTHONIOENCODING: 'utf-8',
            PYTHONUTF8: '1',
            PYTHONUNBUFFERED: '1',
        };
        return runCommand(this.python, [script, ...args], { cwd, timeoutMs: COMMAND_TIMEOUT_MS, env });
    }
    /**
     * Reveal one directory in the platform file manager, detached from the host.
     * @param target - canonical absolute directory path.
     */
    async reveal(target) {
        const command = this.openDir
            ?? (process.platform === 'win32' ? 'explorer' : process.platform === 'darwin' ? 'open' : 'xdg-open');
        await new Promise((resolveReveal, rejectReveal) => {
            const child = spawn(command, [target], { detached: true, stdio: 'ignore', windowsHide: false });
            child.once('error', (error) => {
                rejectReveal(new Error(`无法打开目录（${command}）: ${error.message}`));
            });
            child.once('spawn', () => {
                child.unref();
                resolveReveal();
            });
        });
    }
    // ── persistence ───────────────────────────────────────────────────────────
    /** Absolute path of the OJ configuration file. */
    get ojFile() {
        return join(this.homeDir, 'oj.json');
    }
    /** Absolute path of the contest configuration file. */
    get contestsFile() {
        return join(this.homeDir, 'contests.json');
    }
    /**
     * Read the persisted OJ configuration, tolerating a missing or corrupt file.
     * @returns the normalized configuration.
     */
    async readOjConfig() {
        const raw = await readJsonFile(this.ojFile);
        if (!isRecord(raw))
            return { profiles: [], activeProfileId: '' };
        const profiles = [];
        if (Array.isArray(raw.profiles)) {
            for (const entry of raw.profiles) {
                const profile = coerceOjProfile(entry);
                if (profile !== undefined)
                    profiles.push(profile);
            }
        }
        const active = typeof raw.activeProfileId === 'string' ? raw.activeProfileId : '';
        return { profiles, activeProfileId: profiles.some((profile) => profile.id === active) ? active : '' };
    }
    /**
     * Persist the OJ configuration atomically.
     * @param config - the complete configuration to store.
     */
    async writeOjConfig(config) {
        await this.writeJsonAtomic(this.ojFile, config);
    }
    /**
     * Read the persisted contest list, tolerating a missing or corrupt file.
     * @returns the normalized contest list.
     */
    async readContests() {
        const raw = await readJsonFile(this.contestsFile);
        const list = Array.isArray(raw) ? raw : isRecord(raw) && Array.isArray(raw.contests) ? raw.contests : [];
        const contests = [];
        for (const entry of list) {
            const contest = coerceContestEntry(entry);
            if (contest !== undefined)
                contests.push(contest);
        }
        return contests;
    }
    /**
     * Persist the contest list atomically.
     * @param contests - the complete list to store.
     */
    async writeContests(contests) {
        await this.writeJsonAtomic(this.contestsFile, contests);
    }
    /**
     * Write JSON through a sibling temporary file plus rename, so a crash cannot
     * leave a half-written configuration behind.
     * @param file - destination path.
     * @param value - JSON-serializable value.
     */
    async writeJsonAtomic(file, value) {
        await mkdir(this.homeDir, { recursive: true });
        const tmp = `${file}.${process.pid}.${Date.now()}.tmp`;
        await writeFile(tmp, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
        try {
            await rename(tmp, file);
        }
        catch (error) {
            await unlink(tmp).catch(() => undefined);
            throw error;
        }
    }
}
/**
 * Whether `candidate` is the root itself or lies under it.
 * @param root - absolute root path.
 * @param candidate - absolute candidate path.
 * @returns whether the candidate is contained.
 */
function isInside(root, candidate) {
    const rel = relative(root, candidate);
    if (rel === '')
        return true;
    return !rel.startsWith('..') && !isAbsolute(rel);
}
/**
 * Replace characters that are unsafe in a single path segment.
 * @param value - raw segment.
 * @returns a filesystem-safe segment.
 */
function sanitizeSegment(value) {
    const safe = value.replace(/[^A-Za-z0-9._-]+/g, '-').replace(/^-+|-+$/g, '');
    return safe === '' ? 'contest' : safe;
}
/**
 * Validate and normalize one panel-supplied OJ profile.
 * Unknown fields are dropped, so a secret accidentally sent by the panel never
 * reaches disk.
 * @param value - candidate profile.
 * @returns the normalized profile.
 * @throws {BadRequestError} when a required field is missing or invalid.
 */
function normalizeOjProfile(value) {
    if (!isRecord(value))
        throw new BadRequestError('profile 必须是 JSON 对象');
    const id = requireString(value.id, 'profile.id');
    const kind = value.kind;
    if (kind !== 'hydro' && kind !== 'hoj')
        throw new BadRequestError(`profile.kind 必须是 hydro 或 hoj: ${String(kind)}`);
    const base = typeof value.base === 'string' ? value.base.trim() : '';
    if (base !== '') {
        let url;
        try {
            url = new URL(base);
        }
        catch {
            throw new BadRequestError(`profile.base 不是有效 URL: ${base}`);
        }
        if (url.protocol !== 'http:' && url.protocol !== 'https:') {
            throw new BadRequestError(`profile.base 必须是 http(s) URL: ${base}`);
        }
    }
    const credentialEnv = typeof value.credentialEnv === 'string' ? value.credentialEnv.trim() : '';
    if (credentialEnv !== '' && !/^[A-Za-z_][A-Za-z0-9_]*$/.test(credentialEnv)) {
        throw new BadRequestError(`profile.credentialEnv 必须是环境变量名: ${credentialEnv}`);
    }
    return {
        id,
        kind: kind,
        name: typeof value.name === 'string' ? value.name.trim() : '',
        base,
        user: typeof value.user === 'string' ? value.user.trim() : '',
        credentialEnv,
    };
}
/**
 * Coerce one persisted profile, ignoring corrupt rows.
 * @param value - candidate value from disk.
 * @returns the profile, or `undefined` when unusable.
 */
function coerceOjProfile(value) {
    if (!isRecord(value))
        return undefined;
    if (typeof value.id !== 'string' || value.id === '')
        return undefined;
    const kind = value.kind === 'hoj' ? 'hoj' : 'hydro';
    return {
        id: value.id,
        kind,
        name: typeof value.name === 'string' ? value.name : '',
        base: typeof value.base === 'string' ? value.base : '',
        user: typeof value.user === 'string' ? value.user : '',
        credentialEnv: typeof value.credentialEnv === 'string' ? value.credentialEnv : '',
    };
}
/**
 * Coerce one persisted contest entry, ignoring corrupt rows.
 * @param value - candidate value from disk.
 * @returns the entry, or `undefined` when unusable.
 */
function coerceContestEntry(value) {
    if (!isRecord(value))
        return undefined;
    if (typeof value.id !== 'string' || value.id === '')
        return undefined;
    if (typeof value.title !== 'string')
        return undefined;
    const problems = Array.isArray(value.problems)
        ? value.problems.filter((entry) => typeof entry === 'string')
        : [];
    return {
        id: value.id,
        title: value.title,
        problems,
        updatedAt: typeof value.updatedAt === 'string' ? value.updatedAt : '',
    };
}
//# sourceMappingURL=service.js.map