/**
 * dsh-oi-workbench — client 面板（sidebar.footer.action）。
 * 在侧边栏底部、设置上方显示入口，点击打开 OI 工作台面板。
 */
import type { SlotsService } from '@deepseek-ai/dsh-client-ui-slots';
type ClientContext = {
    slots: SlotsService;
};
export declare const inject: string[];
export declare function apply(ctx: ClientContext): void;
export {};
