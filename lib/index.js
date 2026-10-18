import { defineTool } from '@deepseek-ai/dsh-tools';
import z from '@deepseek-ai/schemastery';
import { createRoutes } from './api/routes.js';
import { WorkbenchService } from './api/service.js';
import { registerWorkbenchSkill, SKILL_DIRECTORY } from './skill.js';
export const name = 'dsh-oi-workbench';
/** Services the plugin needs before it may activate. */
export const inject = ['webServer', 'tools', 'skills'];
export const Config = z.object({
    rootDir: z.string().default(''),
    python: z.string().default('python'),
});
/**
 * Activate the host half of the plugin.
 * @param ctx - host plugin context (webServer, tools, and skills are injected).
 * @param config - validated plugin configuration.
 */
export function apply(ctx, config) {
    const root = config.rootDir || process.cwd();
    const service = new WorkbenchService({
        rootDir: root,
        skillsDir: SKILL_DIRECTORY,
        python: config.python || 'python',
    });
    // ── Panel API ──
    ctx.effect(() => {
        const disposers = createRoutes(service).map((route) => ctx.webServer.register(route));
        return () => {
            for (const dispose of disposers)
                dispose();
        };
    }, 'oi-workbench: api');
    // ── Skill provider ──
    ctx.effect(() => registerWorkbenchSkill(ctx), 'oi-workbench: skill');
    // ── Status tool ──
    ctx.effect(() => ctx.tools.register(defineTool({
        name: 'oiwb_status',
        description: 'OI 工作台状态：根目录、题目数量、skills 是否注册',
        parameters: {},
        output: {
            schema: { type: 'string' },
            render: (_args, value) => [{ type: 'text', text: String(value) }],
        },
        async execute() {
            const state = await service.state();
            return JSON.stringify({
                root: state.root,
                version: state.version,
                skill: state.skill,
                skillRegistered: state.skillRegistered,
                problemCount: state.problems.length,
                ojProfiles: state.oj.profiles.length,
                contests: state.contests.length,
            });
        },
    })), 'oi-workbench: status tool');
}
//# sourceMappingURL=index.js.map