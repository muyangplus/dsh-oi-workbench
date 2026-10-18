/**
 * dsh-oi-workbench — OI 出题工作台（DSH 原生 UI 版本）。
 *
 * host 侧：注册 `/oi-workbench/api` 路由、`oi-workbench` skill provider 与
 * `oiwb_status` 状态工具；client 侧：DSH Web 面板（`src/client`，由
 * package.json 的 `dsh.client` 声明加载）。
 *
 * 配置：`rootDir`（题目工作台根目录，默认进程 cwd）、`python`（解释器名）。
 */
import type { Context } from '@deepseek-ai/cordis';
import z from '@deepseek-ai/schemastery';
export declare const name = "dsh-oi-workbench";
/** Services the plugin needs before it may activate. */
export declare const inject: string[];
export interface Config {
    /** Workbench root scanned for problem packages; empty means `process.cwd()`. */
    rootDir: string;
    /** Python executable used for the bundled tool scripts. */
    python: string;
}
export declare const Config: z<Schemastery.ObjectS<NoInfer<{
    rootDir: z<string, string, "defined">;
    python: z<string, string, "defined">;
}>>, Schemastery.ObjectT<NoInfer<{
    rootDir: z<string, string, "defined">;
    python: z<string, string, "defined">;
}>>, "plain">;
/**
 * Activate the host half of the plugin.
 * @param ctx - host plugin context (webServer, tools, and skills are injected).
 * @param config - validated plugin configuration.
 */
export declare function apply(ctx: Context, config: Config): void;
