/**
 * dsh-oi-workbench — OI 出题工作台（DSH 原生 UI 版本）。
 *
 * host 侧：提供 webServer API 与状态工具。
 * client 侧：settings.section 面板（见 src/client/index.ts）。
 */
import { Context } from 'cordis';
import z from 'schemastery';
export declare const name = "dsh-oi-workbench";
export declare const inject: string[];
export interface Config {
    rootDir: string;
}
export declare const Config: z<Schemastery.ObjectS<{
    rootDir: z<string, string>;
}>, Schemastery.ObjectT<{
    rootDir: z<string, string>;
}>>;
type AppContext = Context & {
    webServer: any;
    tools: any;
};
export declare function apply(ctx: AppContext, config: Config): void;
export {};
