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
export declare const API_PREFIX = "/oi-workbench/api";
/** Plugin package name, echoed by `/state`. */
export declare const PLUGIN_NAME = "@muyangplus/dsh-oi-workbench";
/** Build target for one problem package. */
export type BuildTarget = 'hydro' | 'hoj' | 'both';
/** Read-only facts about one discovered problem directory. */
export interface ProblemBadges {
    /** `problem.md` exists. */
    readonly hasProblemMd: boolean;
    /** `solution/solution.md` exists. */
    readonly hasSolution: boolean;
    /** `std/std.cpp` exists. */
    readonly hasStd: boolean;
    /** `spec.json` exists (every discovered problem has it). */
    readonly hasSpec: boolean;
    /** Number of declared test cases (`spec.cases` length, or 0). */
    readonly caseCount: number;
    /** `data/` holds at least one `.in` file. */
    readonly hasData: boolean;
}
/** One problem directory discovered under the workbench root. */
export interface ProblemEntry {
    /** Slash-separated path relative to the workbench root. */
    readonly name: string;
    /** Absolute directory path. */
    readonly path: string;
    readonly badges: ProblemBadges;
}
/** Online-judge kind the profile addresses. */
export type OjKind = 'hydro' | 'hoj';
/**
 * One stored OJ connection profile. Secrets never live here: only the NAME of
 * the environment variable that carries the password/token.
 */
export interface OjProfile {
    /** Stable local id (`hydro-main`, `hoj-test`, ...). */
    readonly id: string;
    readonly kind: OjKind;
    /** Display name shown by the panel. */
    readonly name: string;
    /** Instance base URL, for example `https://hydro.example.com`. */
    readonly base: string;
    /** Login user name, or empty when only a cookie/token is used. */
    readonly user: string;
    /** Environment variable holding the password or session cookie. */
    readonly credentialEnv: string;
}
/** Persisted OJ configuration. */
export interface OjConfig {
    readonly profiles: readonly OjProfile[];
    /** `id` of the profile the panel treats as default, or empty. */
    readonly activeProfileId: string;
}
/** One saved contest plan (a manifest draft the panel can rebuild). */
export interface ContestEntry {
    readonly id: string;
    readonly title: string;
    /** Problem directory paths, relative to the root. */
    readonly problems: readonly string[];
    /** ISO timestamp of the last save. */
    readonly updatedAt: string;
}
/** Full snapshot the panel renders. */
export interface WorkbenchState {
    readonly root: string;
    /** Plugin package version. */
    readonly version: string;
    /** Skill id this plugin serves. */
    readonly skill: string;
    /** Whether the `oi-workbench` skill catalog entry is live. */
    readonly skillRegistered: boolean;
    readonly problems: readonly ProblemEntry[];
    readonly oj: OjConfig;
    readonly contests: readonly ContestEntry[];
}
/** Result of one spawned Python tool run. */
export interface CommandResult {
    readonly ok: boolean;
    readonly exitCode: number;
    readonly stdout: string;
    readonly stderr: string;
    readonly durationMs: number;
    /** argv the host executed, for the panel log. */
    readonly argv: readonly string[];
}
/** One action the panel may ask the host to perform. */
export type WorkbenchAction = {
    readonly kind: 'check';
    readonly dir: string;
} | {
    readonly kind: 'build';
    readonly dir: string;
    readonly target: BuildTarget;
} | {
    readonly kind: 'judge';
    readonly dir: string;
    readonly source: string;
    readonly timeLimitMs: number;
} | {
    readonly kind: 'open';
    readonly dir: string;
} | {
    readonly kind: 'oj-save';
    readonly profile: OjProfile;
} | {
    readonly kind: 'oj-delete';
    readonly id: string;
} | {
    readonly kind: 'oj-set-active';
    readonly id: string;
} | {
    readonly kind: 'oj-test';
    readonly id: string;
} | {
    readonly kind: 'contest-save';
    readonly contest: {
        readonly id: string;
        readonly title: string;
        readonly problems: readonly string[];
    };
} | {
    readonly kind: 'contest-delete';
    readonly id: string;
} | {
    readonly kind: 'contest-build';
    readonly id: string;
};
/** Payload of a successful `/action` response. */
export interface ActionOutcome {
    readonly ok: boolean;
    /** Human-facing one-line summary. */
    readonly message: string;
    /** Command output when the action ran a Python tool. */
    readonly command?: CommandResult;
    /** Refreshed state after a mutating action; omitted for read-only actions. */
    readonly state?: WorkbenchState;
}
/** Envelope of every JSON response; `ok: false` carries a readable `error`. */
export type ApiEnvelope<T> = {
    readonly ok: true;
    readonly value: T;
} | {
    readonly ok: false;
    readonly error: string;
};
