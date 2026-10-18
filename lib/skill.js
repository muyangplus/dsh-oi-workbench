/**
 * `oi-workbench` skill provider.
 *
 * The skill body ships as plain Markdown inside this package, so the provider
 * reads the file on every `list()` / `get()` instead of caching: editing
 * `skills/oi-workbench/SKILL.md` takes effect on the next request.
 *
 * @module @muyangplus/dsh-oi-workbench/skill
 */
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { BUNDLED_SKILL_RANK, } from '@deepseek-ai/dsh-skill';
import { parseSkillMarkdown } from './api/service.js';
/** Public skill id served by this plugin. */
export const SKILL_NAME = 'oi-workbench';
/** Provider label / registry name for the bundled provider. */
const PROVIDER_NAME = 'oi-workbench';
/** Absolute path of the bundled `skills/oi-workbench` directory. */
export const SKILL_DIRECTORY = fileURLToPath(new URL('../skills/oi-workbench/', import.meta.url));
/** Absolute path of the bundled `SKILL.md`. */
export const SKILL_FILE = join(SKILL_DIRECTORY, 'SKILL.md');
/** Description used when `SKILL.md` has no usable frontmatter description. */
const FALLBACK_DESCRIPTION = 'OI 出题工作台：知识点锁定、数据构造、本地评测、打包与 Hydro/HOJ 发布';
/**
 * Read and parse the bundled `SKILL.md` fresh from disk.
 * @returns parsed facts, or `undefined` when the file is missing, unreadable, or empty.
 */
async function readSkillFacts() {
    let text;
    try {
        text = await readFile(SKILL_FILE, 'utf8');
    }
    catch {
        return undefined;
    }
    const parsed = parseSkillMarkdown(text);
    if (parsed.body.trim() === '')
        return undefined;
    const description = parsed.description !== undefined && parsed.description !== '' ? parsed.description : FALLBACK_DESCRIPTION;
    return { body: parsed.body, description, metadata: parsed.metadata };
}
/**
 * Build the discovery candidate for the bundled skill.
 * @param facts - parsed skill facts.
 * @returns a complete provider candidate.
 */
function candidateOf(facts) {
    return {
        name: SKILL_NAME,
        description: facts.description,
        provider: PROVIDER_NAME,
        source: 'bundled',
        resourceBase: { kind: 'directory', path: SKILL_DIRECTORY },
        rank: BUNDLED_SKILL_RANK,
        locator: { kind: 'bundled-skill-file', file: SKILL_FILE },
        invocation: { modelInvocable: true, userInvocable: true },
        path: SKILL_FILE,
        metadata: facts.metadata,
    };
}
/**
 * Create the `oi-workbench` provider. `list()` re-reads the file so a changed
 * `SKILL.md` is visible immediately.
 * @returns the provider object passed to `ctx.skills.registerProvider`.
 */
export function createWorkbenchSkillProvider() {
    return {
        name: PROVIDER_NAME,
        async list(options) {
            if (options.signal?.aborted === true)
                return [];
            const facts = await readSkillFacts();
            return facts === undefined ? [] : [candidateOf(facts)];
        },
        async get(candidate, options) {
            if (options.signal?.aborted === true)
                return undefined;
            if (candidate.name !== SKILL_NAME)
                return undefined;
            const facts = await readSkillFacts();
            if (facts === undefined)
                return undefined;
            return {
                name: SKILL_NAME,
                description: facts.description,
                provider: PROVIDER_NAME,
                source: 'bundled',
                resourceBase: { kind: 'directory', path: SKILL_DIRECTORY },
                invocation: { modelInvocable: true, userInvocable: true },
                path: SKILL_FILE,
                metadata: facts.metadata,
                content: facts.body,
            };
        },
    };
}
/**
 * Register the bundled skill provider on the calling context.
 * @param ctx - host plugin context carrying the `skills` registry.
 * @returns the exact disposer that unregisters the provider.
 */
export function registerWorkbenchSkill(ctx) {
    return ctx.skills.registerProvider(() => createWorkbenchSkillProvider());
}
//# sourceMappingURL=skill.js.map