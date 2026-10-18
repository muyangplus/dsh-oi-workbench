import type { Context } from '@deepseek-ai/cordis';
import { type SkillProvider } from '@deepseek-ai/dsh-skill';
/** Public skill id served by this plugin. */
export declare const SKILL_NAME = "oi-workbench";
/** Absolute path of the bundled `skills/oi-workbench` directory. */
export declare const SKILL_DIRECTORY: string;
/** Absolute path of the bundled `SKILL.md`. */
export declare const SKILL_FILE: string;
/**
 * Create the `oi-workbench` provider. `list()` re-reads the file so a changed
 * `SKILL.md` is visible immediately.
 * @returns the provider object passed to `ctx.skills.registerProvider`.
 */
export declare function createWorkbenchSkillProvider(): SkillProvider;
/**
 * Register the bundled skill provider on the calling context.
 * @param ctx - host plugin context carrying the `skills` registry.
 * @returns the exact disposer that unregisters the provider.
 */
export declare function registerWorkbenchSkill(ctx: Context): () => void;
