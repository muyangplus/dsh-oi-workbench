import type { ActionOutcome, ProblemEntry, WorkbenchAction, WorkbenchState } from './contract.js';
/** Raised for a request the panel got wrong; the route layer maps it to HTTP 400. */
export declare class BadRequestError extends Error {
    constructor(message: string);
}
/** Construction options for {@link WorkbenchService}. */
export interface WorkbenchServiceOptions {
    /** Workbench root the plugin scans for problem packages. */
    readonly rootDir: string;
    /** Directory holding `oj.json` / `contests.json`; defaults to `~/.dsh-oi-workbench` (env `OIWB_HOME` wins). */
    readonly homeDir?: string;
    /** Bundled skill resource directory; defaults to `<package>/skills/oi-workbench`. */
    readonly skillsDir?: string;
    /** Python executable used to run the bundled tool scripts. */
    readonly python?: string;
    /** Override the command that reveals a directory (`explorer` / `open` / `xdg-open` by platform). */
    readonly openDir?: string;
}
/** Outcome of skill frontmatter parsing. */
interface ParsedSkillFile {
    /** Frontmatter `name`, when it matches the public kebab-case grammar. */
    readonly name?: string;
    /** Frontmatter `description`, flattened to one line. */
    readonly description?: string;
    /** Markdown body after the frontmatter block. */
    readonly body: string;
    /** Every frontmatter key/value pair. */
    readonly metadata: Readonly<Record<string, string>>;
}
/**
 * Split a Markdown `---` frontmatter block from its body.
 * @param text - complete `SKILL.md` text.
 * @returns parsed frontmatter plus body.
 */
export declare function parseSkillMarkdown(text: string): ParsedSkillFile;
/**
 * Host-side workbench operations shared by every route and tool.
 */
export declare class WorkbenchService {
    /** Absolute workbench root. */
    readonly rootDir: string;
    /** Directory holding persisted OJ/contest configuration. */
    readonly homeDir: string;
    /** Bundled skill resource directory. */
    readonly skillsDir: string;
    /** Python executable used for the bundled tools. */
    readonly python: string;
    /** Command override used to reveal a directory. */
    readonly openDir: string | undefined;
    constructor(options: WorkbenchServiceOptions);
    /**
     * Full panel snapshot: problems, OJ profiles, contests, and version facts.
     * @returns the current workbench state.
     */
    state(): Promise<WorkbenchState>;
    /**
     * Discover problem packages under the root.
     * @returns one entry per directory holding `spec.json`, ordered by name.
     */
    problems(): Promise<ProblemEntry[]>;
    /**
     * Read the plugin version from the package manifest.
     * @returns the version string, or `''` when unreadable.
     */
    version(): Promise<string>;
    /**
     * Execute one panel action.
     * @param action - the action payload from the panel.
     * @returns the action outcome; failures are reported as `ok: false` unless the request itself is invalid.
     * @throws {BadRequestError} for an unknown action or a malformed field.
     */
    act(action: WorkbenchAction): Promise<ActionOutcome>;
    /** Run `tools/check_problem.py` against one problem directory. */
    private check;
    /** Build the Hydro and/or HOJ package zips next to the problem directory. */
    private build;
    /** Run `generator/local_judge.py` against one source file. */
    private judge;
    /** Reveal one directory in the platform file manager. */
    private open;
    /** Upsert one OJ connection profile (secrets are never persisted). */
    private ojSave;
    /** Delete one OJ profile by id. */
    private ojDelete;
    /** Mark one OJ profile as the default; an empty id clears the selection. */
    private ojSetActive;
    /** Probe one OJ profile with an unauthenticated GET; only the HTTP status is reported. */
    private ojTest;
    /** Upsert one saved contest plan. */
    private contestSave;
    /** Delete one saved contest plan by id. */
    private contestDelete;
    /** Build every deliverable of one saved contest with `generator/build_contest.py`. */
    private contestBuild;
    /**
     * Walk the root for directories holding `spec.json`.
     * @returns absolute paths, ordered by relative name.
     */
    private scanProblemDirs;
    /**
     * Read the four file-presence and two counting badges of one problem.
     * @param dir - absolute problem directory.
     * @returns the badge set.
     */
    private badgesOf;
    /**
     * Resolve a panel-supplied path and require it to be an existing directory inside the root.
     * @param input - absolute path or path relative to the root.
     * @returns the canonical absolute path.
     * @throws {BadRequestError} when the path escapes the root or does not exist.
     */
    private requireInsideDir;
    /**
     * Resolve a directory that must also be a problem package.
     * @param input - absolute path or path relative to the root.
     * @returns the canonical absolute path.
     * @throws {BadRequestError} when it is outside the root or holds no `spec.json`.
     */
    private requireProblemDir;
    /**
     * Canonicalize a path and prove it stays inside the workbench root.
     * @param input - absolute path or path relative to the root.
     * @returns the real absolute path.
     * @throws {BadRequestError} when outside the root, missing, or not a directory.
     */
    private canonicalInside;
    /**
     * Lexically convert a path to root-relative form without requiring it to exist.
     * @param input - absolute path or path relative to the root.
     * @returns slash-separated path relative to the root.
     * @throws {BadRequestError} when it escapes the root.
     */
    private toRootRelative;
    /**
     * Whether an absolute path is lexically inside the root (no existence check).
     * @param candidate - absolute candidate path.
     * @returns whether it is the root or below it.
     */
    private lexicallyInsideRoot;
    /**
     * Whether a canonical path is inside the canonical root.
     * @param candidate - real absolute path.
     * @returns whether it is the root or below it.
     */
    private isInsideRoot;
    /**
     * Locate a bundled Python script and require it to exist.
     * @param script - absolute script path.
     * @returns the same path.
     * @throws {Error} when the packaged skill resources are incomplete.
     */
    private requireScript;
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
    private runPython;
    /**
     * Reveal one directory in the platform file manager, detached from the host.
     * @param target - canonical absolute directory path.
     */
    private reveal;
    /** Absolute path of the OJ configuration file. */
    private get ojFile();
    /** Absolute path of the contest configuration file. */
    private get contestsFile();
    /**
     * Read the persisted OJ configuration, tolerating a missing or corrupt file.
     * @returns the normalized configuration.
     */
    private readOjConfig;
    /**
     * Persist the OJ configuration atomically.
     * @param config - the complete configuration to store.
     */
    private writeOjConfig;
    /**
     * Read the persisted contest list, tolerating a missing or corrupt file.
     * @returns the normalized contest list.
     */
    private readContests;
    /**
     * Persist the contest list atomically.
     * @param contests - the complete list to store.
     */
    private writeContests;
    /**
     * Write JSON through a sibling temporary file plus rename, so a crash cannot
     * leave a half-written configuration behind.
     * @param file - destination path.
     * @param value - JSON-serializable value.
     */
    private writeJsonAtomic;
}
export {};
