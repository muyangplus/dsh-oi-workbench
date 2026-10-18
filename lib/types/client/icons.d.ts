/**
 * Inline SVG glyphs for the OI workbench panel.
 *
 * The sidebar row glyph is the only DOM this plugin owns inside the
 * shell-owned row, so it carries `data-dsh-panel-entry="oi-workbench"` (the
 * semantic anchor skins resolve panel rows through). Every glyph strokes
 * `currentColor` and inherits the shell's text color, so light, dark and skinned
 * themes all render correctly.
 *
 * @module @muyangplus/dsh-oi-workbench/client/icons
 */
import type { ReactElement } from 'react';
/** The shell's icon share: square edge and selection state. */
export interface WorkbenchIconProps {
    readonly size: number;
    readonly active: boolean;
}
/** Props every small panel glyph accepts. */
export interface GlyphProps {
    readonly size?: number;
}
/**
 * The sidebar row glyph: a small terminal/box hybrid standing for the
 * problem-setting workbench.
 * @param props - the shell's icon share.
 * @returns the decorative workbench glyph.
 */
export declare function WorkbenchIcon({ size, active }: WorkbenchIconProps): ReactElement;
/** Refresh / reload snapshot. */
export declare function RefreshIcon(props: GlyphProps): ReactElement;
/** Check / validate. */
export declare function CheckIcon(props: GlyphProps): ReactElement;
/** Package / build. */
export declare function BoxIcon(props: GlyphProps): ReactElement;
/** Run / local judge. */
export declare function PlayIcon(props: GlyphProps): ReactElement;
/** Open the problem directory. */
export declare function FolderIcon(props: GlyphProps): ReactElement;
/** Add / create. */
export declare function PlusIcon(props: GlyphProps): ReactElement;
/** Delete. */
export declare function TrashIcon(props: GlyphProps): ReactElement;
/** OJ connection test. */
export declare function PlugIcon(props: GlyphProps): ReactElement;
/** Dismiss. */
export declare function CloseIcon(props: GlyphProps): ReactElement;
/** Terminal output / command log. */
export declare function TerminalIcon(props: GlyphProps): ReactElement;
/** Help / documentation. */
export declare function HelpIcon(props: GlyphProps): ReactElement;
/** Contest / trophy. */
export declare function TrophyIcon(props: GlyphProps): ReactElement;
/** Stats tile glyph: grid of small panels. */
export declare function DashboardIcon(props: GlyphProps): ReactElement;
/** Stats tile glyph: problem list. */
export declare function ListIcon(props: GlyphProps): ReactElement;
