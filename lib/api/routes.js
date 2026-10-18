import { API_PREFIX } from './contract.js';
import { BadRequestError } from './service.js';
/** Largest accepted `/action` request body, in bytes. */
const ACTION_BODY_LIMIT = 256 * 1024;
/** Raised internally when a request body crosses {@link ACTION_BODY_LIMIT}. */
class BodyTooLargeError extends Error {
    constructor() {
        super('request body too large');
        this.name = 'BodyTooLargeError';
    }
}
/**
 * Write one JSON response with the cache headers the panel expects.
 * @param res - the response being owned by this handler.
 * @param status - HTTP status code.
 * @param value - JSON-serializable payload.
 */
function writeJson(res, status, value) {
    const text = JSON.stringify(value);
    res.writeHead(status, {
        'content-type': 'application/json; charset=utf-8',
        'cache-control': 'no-store',
    });
    res.end(text);
}
/**
 * Send one envelope failure.
 * @param res - the response.
 * @param status - HTTP status code.
 * @param error - readable, stack-free failure reason.
 */
function writeError(res, status, error) {
    writeJson(res, status, { ok: false, error });
}
/**
 * Read the complete request body, enforcing one byte limit.
 * @param req - the incoming request.
 * @param limit - maximum accepted body size in bytes.
 * @returns the UTF-8 body text.
 * @throws {BodyTooLargeError} when the limit is exceeded.
 */
async function readBody(req, limit) {
    const chunks = [];
    let size = 0;
    for await (const chunk of req) {
        const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
        size += buffer.length;
        if (size > limit)
            throw new BodyTooLargeError();
        chunks.push(buffer);
    }
    return Buffer.concat(chunks).toString('utf8');
}
/**
 * Parse and validate an action request body.
 * @param text - raw body text.
 * @returns the action payload.
 * @throws {BadRequestError} when the JSON or its `kind` discriminator is invalid.
 */
function parseAction(text) {
    let value;
    try {
        value = text.trim() === '' ? undefined : JSON.parse(text);
    }
    catch {
        throw new BadRequestError('请求体不是合法 JSON');
    }
    if (value === null || typeof value !== 'object' || Array.isArray(value)) {
        throw new BadRequestError('请求体必须是 JSON 对象');
    }
    const kind = value.kind;
    if (typeof kind !== 'string' || kind === '') {
        throw new BadRequestError('请求体缺少 kind');
    }
    const known = [
        'check',
        'build',
        'judge',
        'open',
        'oj-save',
        'oj-delete',
        'oj-set-active',
        'oj-test',
        'contest-save',
        'contest-delete',
        'contest-build',
    ];
    if (!known.includes(kind))
        throw new BadRequestError(`未知的 action kind: ${kind}`);
    return value;
}
/**
 * Build the panel API routes.
 * @param service - the workbench host service the routes drive.
 * @returns one exact-match route per endpoint.
 */
export function createRoutes(service) {
    const state = {
        kind: 'exact',
        path: `${API_PREFIX}/state`,
        handler: async (req, res) => {
            if (req.method !== 'GET') {
                writeError(res, 405, 'method-not-allowed');
                return;
            }
            try {
                const value = await service.state();
                writeJson(res, 200, { ok: true, value });
            }
            catch (error) {
                console.error('[oi-workbench] state failed', error);
                writeError(res, 500, '读取工作台状态失败');
            }
        },
    };
    const problems = {
        kind: 'exact',
        path: `${API_PREFIX}/problems`,
        handler: async (req, res) => {
            if (req.method !== 'GET') {
                writeError(res, 405, 'method-not-allowed');
                return;
            }
            try {
                // Legacy shape kept for older panel builds: `{ ok, root, problems }`.
                writeJson(res, 200, { ok: true, root: service.rootDir, problems: await service.problems() });
            }
            catch (error) {
                console.error('[oi-workbench] problems failed', error);
                writeError(res, 500, '扫描题目目录失败');
            }
        },
    };
    const action = {
        kind: 'exact',
        path: `${API_PREFIX}/action`,
        handler: async (req, res) => {
            if (req.method !== 'POST') {
                writeError(res, 405, 'method-not-allowed');
                return;
            }
            let token;
            try {
                token = parseAction(await readBody(req, ACTION_BODY_LIMIT));
            }
            catch (error) {
                if (error instanceof BodyTooLargeError) {
                    writeError(res, 413, `请求体超过 ${ACTION_BODY_LIMIT} 字节`);
                    return;
                }
                if (error instanceof BadRequestError) {
                    writeError(res, 400, error.message);
                    return;
                }
                console.error('[oi-workbench] action body failed', error);
                writeError(res, 400, '无法读取请求体');
                return;
            }
            try {
                const value = await service.act(token);
                writeJson(res, 200, { ok: true, value });
            }
            catch (error) {
                if (error instanceof BadRequestError) {
                    writeError(res, 400, error.message);
                    return;
                }
                console.error(`[oi-workbench] action ${token.kind} failed`, error);
                writeError(res, 500, `执行 ${token.kind} 失败：${error instanceof Error ? error.message : String(error)}`);
            }
        },
    };
    return [state, problems, action];
}
//# sourceMappingURL=routes.js.map