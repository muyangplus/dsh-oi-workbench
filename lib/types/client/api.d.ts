/**
 * Typed browser-side client for the OI workbench host API.
 *
 * Every call resolves to an {@link ApiResult} — network failures, non-JSON
 * bodies, malformed envelopes and `ok: false` envelopes all become readable
 * Chinese error strings. Nothing in this module throws, because an uncaught
 * rejection inside a panel render would otherwise escape into the shell.
 *
 * Wire types are imported type-only from the frozen contract; the module is
 * erased at bundle time, so the client never depends on host code.
 *
 * @module @muyangplus/dsh-oi-workbench/client/api
 */
import type { ActionOutcome, WorkbenchAction, WorkbenchState } from '../api/contract.ts';
/** Readable success/failure result; never throws. */
export type ApiResult<T> = {
    readonly ok: true;
    readonly value: T;
} | {
    readonly ok: false;
    readonly error: string;
};
/**
 * Read the current workbench snapshot.
 * @returns the state, or a readable error string.
 */
export declare function fetchState(): Promise<ApiResult<WorkbenchState>>;
/**
 * Ask the host to perform one action.
 * @param action - contract action payload.
 * @returns the outcome (which may itself carry `ok: false`), or a transport error.
 */
export declare function runAction(action: WorkbenchAction): Promise<ApiResult<ActionOutcome>>;
