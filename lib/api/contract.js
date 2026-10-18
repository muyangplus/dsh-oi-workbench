/**
 * Shared wire contract between the OI Workbench host API and the Web panel.
 *
 * This module is imported by BOTH halves, so it must stay dependency-free:
 * no Node built-ins, no Cordis, no React. The client bundle inlines the
 * constants and erases the types; the host imports the types only.
 *
 * @module @muyangplus/dsh-oi-workbench/api/contract
 */
/** Prefix of every host HTTP route this plugin owns. */
export const API_PREFIX = '/oi-workbench/api';
/** Plugin package name, echoed by `/state`. */
export const PLUGIN_NAME = '@muyangplus/dsh-oi-workbench';
//# sourceMappingURL=contract.js.map