import { defineTool } from '@deepseek-ai/dsh-tools';
import z from 'schemastery';
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
export const name = 'dsh-oi-workbench';
export const inject = ['webServer', 'tools'];
export const Config = z.object({
    rootDir: z.string().default(''),
});
function findProblemDirs(root, maxDepth = 4) {
    const results = [];
    if (!existsSync(root))
        return results;
    const walk = (dir, depth) => {
        if (depth > maxDepth)
            return;
        let entries;
        try {
            entries = readdirSync(dir, { withFileTypes: true });
        }
        catch {
            return;
        }
        for (const entry of entries) {
            if (!entry.isDirectory())
                continue;
            const full = join(dir, entry.name);
            if (existsSync(join(full, 'spec.json'))) {
                results.push({
                    name: relative(root, full).split(sep).join('/'),
                    path: full,
                    hasProblemMd: existsSync(join(full, 'problem.md')),
                    hasSolution: existsSync(join(full, 'solution', 'solution.md')),
                });
            }
            else {
                walk(full, depth + 1);
            }
        }
    };
    walk(root, 1);
    return results;
}
function runPython(script, args, cwd) {
    try {
        const stdout = execFileSync('python', [script, ...args], { cwd, encoding: 'utf8', timeout: 120000 });
        return { ok: true, stdout };
    }
    catch (e) {
        return { ok: false, stderr: String(e?.stderr || e?.message || e) };
    }
}
export function apply(ctx, config) {
    const root = config.rootDir || process.cwd();
    // ── Host API ──
    ctx.effect(() => ctx.webServer.register({
        kind: 'prefix',
        path: '/oi-workbench/api',
        handler: async (req, res) => {
            const url = new URL(req.url ?? '/', 'http://localhost');
            const pathname = url.pathname.replace(/^\/oi-workbench\/api/, '') || '/';
            const send = (obj, status = 200) => {
                const text = JSON.stringify(obj, null, 2);
                res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' });
                res.end(text);
            };
            if (req.method === 'GET' && pathname === '/problems') {
                send({ root, problems: findProblemDirs(root) });
                return;
            }
            if (req.method === 'POST' && pathname === '/problems/check') {
                let body = {};
                try {
                    body = JSON.parse(await readBody(req));
                }
                catch { /* ignore */ }
                const dir = body.dir;
                if (!dir || !existsSync(dir))
                    return send({ error: 'dir not found' }, 400);
                const script = join(root, 'skills', 'oi-workbench', 'tools', 'check_problem.py');
                send(runPython(script, [dir], root));
                return;
            }
            if (req.method === 'POST' && pathname === '/problems/build') {
                let body = {};
                try {
                    body = JSON.parse(await readBody(req));
                }
                catch { /* ignore */ }
                const dir = body.dir;
                if (!dir || !existsSync(dir))
                    return send({ error: 'dir not found' }, 400);
                const gen = join(root, 'skills', 'oi-workbench', 'generator');
                const name = dir.split(sep).pop();
                const r1 = runPython(join(gen, 'build_package.py'), [dir, '--out', join(dir, '..', name + '.zip')], root);
                const r2 = runPython(join(gen, 'build_hoj_package.py'), [dir, '--out', join(dir, '..', name + '-hoj.zip')], root);
                send({ hydro: r1, hoj: r2 });
                return;
            }
            if (req.method === 'POST' && pathname === '/oj/test') {
                send({ ok: true, message: 'OJ 连接测试接口待接入真实实例' });
                return;
            }
            send({ error: 'not found' }, 404);
        },
    }), 'dsh-oi-workbench: api');
    // ── Status tool ──
    ctx.effect(() => ctx.tools.register(defineTool({
        name: 'oiwb_status',
        description: 'OI 工作台状态：返回 root 与题目数量',
        parameters: {},
        output: {
            schema: { type: 'string' },
            render: (_args, value) => [{ type: 'text', text: String(value) }],
        },
        async execute() {
            return JSON.stringify({ root, problemCount: findProblemDirs(root).length });
        },
    })), 'dsh-oi-workbench: status tool');
}
function readBody(req) {
    return new Promise((resolve, reject) => {
        let data = '';
        req.on('data', (chunk) => { data += chunk.toString('utf8'); });
        req.on('end', () => resolve(data));
        req.on('error', reject);
    });
}
//# sourceMappingURL=index.js.map