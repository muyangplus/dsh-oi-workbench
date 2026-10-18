/**
 * OI workbench — browser half of the DSH plugin.
 *
 * The workbench is a native main-column panel, not a DOM takeover: the sidebar
 * shell owns the row button and the active highlight (`sidebar.panellist`), the
 * layout owns the center column and mounts this page only while the row is
 * selected (`main`, keyed by the same id). Both contributions go through
 * `ctx.slots.inject`, which fires once the owning shell entry declares the seat,
 * so plugin load order does not matter and a shell without that seat simply
 * leaves the workbench absent instead of failing boot.
 *
 * Failure policy: registration problems are logged, never thrown — the web
 * shell fails the whole boot when a client plugin's `apply` throws, and a render
 * crash is contained by the panel's own error boundary.
 *
 * @module @muyangplus/dsh-oi-workbench/client
 */
import type { Context as CordisContext } from '@deepseek-ai/cordis';
import { WORKBENCH_PANEL_ID } from './panel.js';
/** The panel id shared by the sidebar row and the main-slot occupant. */
export { WORKBENCH_PANEL_ID };
/**
 * The slice of the slot registry service this plugin consumes.
 *
 * The renderer package that augments `Context` with a typed `ctx.slots` is not
 * a dependency of this package, so the service is described structurally at the
 * boundary (same approach as the shipped third-party native panels).
 */
interface SlotsService {
    inject(key: string, callback: () => () => void): () => void;
    register(options: SlotRegistration, component: unknown): () => void;
}
/** Registration options for the two seats this plugin contributes to. */
interface SlotRegistration {
    name: string;
    readonly id?: string;
    readonly key?: string;
    readonly order?: number;
    readonly label?: string | (() => string);
}
/** Client root context with the slot registry service present. */
type ClientContext = CordisContext & {
    slots: SlotsService;
};
/** Services that must be up before this plugin's `apply` runs. */
export declare const inject: string[];
/**
 * Client plugin body.
 * @param ctx - client root context (services: slots).
 */
export declare function apply(ctx: ClientContext): void;
