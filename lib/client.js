window.__ModuleLoader__.load({
	id: "@muyangplus/dsh-oi-workbench",
	factory: (require) => {
		var module = { exports: {} };
		var exports = module.exports;
		Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
		let react_jsx_runtime = require("react/jsx-runtime");
		let react = require("react");
		//#region src/client/icons.tsx
		/** Shared drawing attributes for the 16px glyph grid. */
		const GLYPH = {
			viewBox: "0 0 16 16",
			fill: "none",
			stroke: "currentColor",
			strokeLinecap: "round",
			strokeLinejoin: "round",
			"aria-hidden": true
		};
		/** Shared drawing attributes for larger area glyphs (stat tiles). */
		const TILE_GLYPH = {
			...GLYPH,
			strokeWidth: 1.2
		};
		/**
		* The sidebar row glyph: a small terminal/box hybrid standing for the
		* problem-setting workbench.
		* @param props - the shell's icon share.
		* @returns the decorative workbench glyph.
		*/
		function WorkbenchIcon({ size, active }) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("svg", {
				...GLYPH,
				"data-dsh-panel-entry": "oi-workbench",
				width: size,
				height: size,
				strokeWidth: active ? 1.55 : 1.3,
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("rect", {
						x: "1.9",
						y: "2.6",
						width: "12.2",
						height: "10.8",
						rx: "2.2"
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M4.7 6.2 6.6 8l-1.9 1.8" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M8.6 9.8h2.7" })
				]
			});
		}
		/** Wrap one small glyph body in the shared 16px SVG frame. */
		function Glyph({ size = 14, children }) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsx)("svg", {
				...GLYPH,
				width: size,
				height: size,
				strokeWidth: "1.4",
				children
			});
		}
		/** Refresh / reload snapshot. */
		function RefreshIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)(Glyph, {
				...props,
				children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M13.4 8a5.4 5.4 0 1 1-1.6-3.8" }), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M13.4 2.6v2.5h-2.5" })]
			});
		}
		/** Check / validate. */
		function CheckIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsx)(Glyph, {
				...props,
				children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M3.2 8.4 6.4 11.6 12.8 4.6" })
			});
		}
		/** Package / build. */
		function BoxIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)(Glyph, {
				...props,
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M8 1.9 14 5.2v6.2L8 14.7 2 11.4V5.2z" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M2 5.2 8 8.5l6-3.3" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M8 8.5v6.2" })
				]
			});
		}
		/** Run / local judge. */
		function PlayIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsx)(Glyph, {
				...props,
				children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M4.8 3.2 12.6 8l-7.8 4.8z" })
			});
		}
		/** Open the problem directory. */
		function FolderIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)(Glyph, {
				...props,
				children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M2 3.6h4l1.5 1.6h6.5v7.2H2z" }), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M2 6.2h12" })]
			});
		}
		/** Add / create. */
		function PlusIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsx)(Glyph, {
				...props,
				children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M8 3v10M3 8h10" })
			});
		}
		/** Delete. */
		function TrashIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)(Glyph, {
				...props,
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M2.8 4.7h10.4" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M6 4.7V3.1h4v1.6" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M4.2 4.7l.6 8.2h6.4l.6-8.2" })
				]
			});
		}
		/** OJ connection test. */
		function PlugIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)(Glyph, {
				...props,
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M5.6 2.2v3.1M10.4 2.2v3.1" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M3.4 5.3h9.2v1.9a4.6 4.6 0 0 1-9.2 0z" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M8 12.1v1.9" })
				]
			});
		}
		/** Dismiss. */
		function CloseIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsx)(Glyph, {
				...props,
				children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M4.2 4.2l7.6 7.6M11.8 4.2l-7.6 7.6" })
			});
		}
		/** Terminal output / command log. */
		function TerminalIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)(Glyph, {
				...props,
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("rect", {
						x: "1.9",
						y: "2.6",
						width: "12.2",
						height: "10.8",
						rx: "1.8"
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M4.4 6.2 6.4 8l-2 1.8" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M8.2 9.8h3.2" })
				]
			});
		}
		/** Help / documentation. */
		function HelpIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)(Glyph, {
				...props,
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("circle", {
						cx: "8",
						cy: "8",
						r: "6.1"
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M6.2 6.1a1.85 1.85 0 1 1 2.7 1.65c-.55.32-.9.85-.9 1.6" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M8 11.9h.01" })
				]
			});
		}
		/** Contest / trophy. */
		function TrophyIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)(Glyph, {
				...props,
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M5 2.6h6v3.3a3 3 0 0 1-6 0z" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M5 3.8H3.2v1.1a3 3 0 0 0 1.9 2.7M11 3.8h1.8v1.1a3 3 0 0 1-1.9 2.7" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M8 8.9v2.4M5.8 13.4h4.4" })
				]
			});
		}
		/** Stats tile glyph: grid of small panels. */
		function DashboardIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("svg", {
				...TILE_GLYPH,
				width: props.size ?? 16,
				height: props.size ?? 16,
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("rect", {
						x: "2",
						y: "2",
						width: "5",
						height: "5",
						rx: "1.1"
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("rect", {
						x: "9",
						y: "2",
						width: "5",
						height: "5",
						rx: "1.1"
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("rect", {
						x: "2",
						y: "9",
						width: "5",
						height: "5",
						rx: "1.1"
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("rect", {
						x: "9",
						y: "9",
						width: "5",
						height: "5",
						rx: "1.1"
					})
				]
			});
		}
		/** Stats tile glyph: problem list. */
		function ListIcon(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsx)("svg", {
				...TILE_GLYPH,
				width: props.size ?? 16,
				height: props.size ?? 16,
				children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)("path", { d: "M3 4.5h2M6.5 4.5h6.5M3 8h2M6.5 8h6.5M3 11.5h2M6.5 11.5h6.5" })
			});
		}
		//#endregion
		//#region src/client/api.ts
		/** Prefix of every host route; mirrors `API_PREFIX` in the frozen contract. */
		const API_PREFIX = "/oi-workbench/api";
		/** Timeout for one state snapshot read. */
		const STATE_TIMEOUT_MS = 15e3;
		/** Timeout for one mutating action (the host may run a Python tool for it). */
		const ACTION_TIMEOUT_MS = 18e4;
		/** Turn an unknown thrown value into one readable line. */
		function describeError(error) {
			if (error instanceof Error) {
				if (error.name === "AbortError") return "请求超时或已取消";
				return error.message || error.name;
			}
			return typeof error === "string" ? error : "未知网络错误";
		}
		function isRecord(value) {
			return typeof value === "object" && value !== null;
		}
		/**
		* Narrow one parsed response body to the wire envelope.
		* @param payload - parsed JSON value, or undefined when the body was empty.
		* @returns the narrowed envelope, or undefined when the body breaks the contract.
		*/
		function envelopeOf(payload) {
			if (!isRecord(payload) || typeof payload.ok !== "boolean") return void 0;
			if (payload.ok === false) return typeof payload.error === "string" ? {
				ok: false,
				error: payload.error
			} : void 0;
			if (!("value" in payload)) return void 0;
			return {
				ok: true,
				value: payload.value
			};
		}
		/** One fetch round-trip that never throws and normalizes every failure mode. */
		async function request(path, init, timeoutMs) {
			const controller = typeof AbortController === "function" ? new AbortController() : void 0;
			const timer = controller === void 0 ? void 0 : setTimeout(() => controller.abort(), timeoutMs);
			try {
				const response = await fetch(API_PREFIX + path, {
					cache: "no-store",
					headers: { accept: "application/json" },
					...init,
					...controller === void 0 ? {} : { signal: controller.signal }
				});
				const text = await response.text();
				let payload;
				try {
					payload = text.length > 0 ? JSON.parse(text) : void 0;
				} catch {
					payload = void 0;
				}
				const envelope = envelopeOf(payload);
				if (envelope === void 0) {
					const snippet = text.trim().slice(0, 240);
					const reason = snippet.length > 0 ? `：${snippet}` : "";
					return {
						ok: false,
						error: `宿主返回了无法识别的响应（HTTP ${response.status}）${reason}`
					};
				}
				if (!envelope.ok) return {
					ok: false,
					error: envelope.error
				};
				if (!response.ok) return {
					ok: false,
					error: `宿主返回 HTTP ${response.status} ${response.statusText}`.trim()
				};
				return {
					ok: true,
					value: envelope.value
				};
			} catch (error) {
				return {
					ok: false,
					error: describeError(error)
				};
			} finally {
				if (timer !== void 0) clearTimeout(timer);
			}
		}
		/**
		* Read the current workbench snapshot.
		* @returns the state, or a readable error string.
		*/
		function fetchState() {
			return request("/state", { method: "GET" }, STATE_TIMEOUT_MS);
		}
		/**
		* Ask the host to perform one action.
		* @param action - contract action payload.
		* @returns the outcome (which may itself carry `ok: false`), or a transport error.
		*/
		function runAction(action) {
			return request("/action", {
				method: "POST",
				headers: { "content-type": "application/json" },
				body: JSON.stringify(action)
			}, ACTION_TIMEOUT_MS);
		}
		//#endregion
		//#region src/client/panel.tsx
		/**
		* The OI workbench native main-column panel (React).
		*
		* The shell mounts this page as the keyed `main` occupant selected by the
		* sidebar row, so it owns only its content: the column geometry, the row
		* button and the active highlight stay with the shell. All copy is Chinese and
		* every failure — transport, host envelope, or a render crash — is shown inside
		* the panel, never thrown into the GUI boot path.
		*
		* @module @muyangplus/dsh-oi-workbench/client/panel
		*/
		/** Panel identity shared with the sidebar row key. */
		const WORKBENCH_PANEL_ID = "oi-workbench";
		/** Tab order shown in the page header. */
		const TABS = [
			{
				key: "overview",
				label: "总览"
			},
			{
				key: "problems",
				label: "题目"
			},
			{
				key: "oj",
				label: "OJ"
			},
			{
				key: "contests",
				label: "比赛"
			},
			{
				key: "help",
				label: "帮助"
			}
		];
		/** Human-readable text for any thrown value. */
		function toMessage(error) {
			if (error instanceof Error) return error.message || error.name;
			return String(error);
		}
		/** Format an ISO timestamp for display; invalid input is shown verbatim. */
		function formatTime(iso) {
			const date = new Date(iso);
			return Number.isNaN(date.getTime()) ? iso : date.toLocaleString("zh-CN", { hour12: false });
		}
		/** `OjKind` → display label. */
		function kindLabel(kind) {
			return kind === "hydro" ? "Hydro" : "HOJ";
		}
		/** `BuildTarget` → display label. */
		function targetLabel(target) {
			if (target === "hydro") return "Hydro";
			if (target === "hoj") return "HOJ";
			return "两者";
		}
		/** Render the workbench page with its own crash boundary. */
		function WorkbenchPanel() {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsx)(PanelErrorBoundary, { children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)(Workbench, {}) });
		}
		/** One contained crash of the panel body: show it in place, keep the GUI alive. */
		var PanelErrorBoundary = class extends react.Component {
			state = { error: null };
			static getDerivedStateFromError(error) {
				return { error: toMessage(error) };
			}
			componentDidCatch(error, info) {
				console.error("[oi-workbench] 面板渲染失败", error, info.componentStack);
			}
			reset = () => {
				this.setState({ error: null });
			};
			render() {
				if (this.state.error !== null) return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("section", {
					className: "oiwb",
					"data-dsh-oiwb-view": "",
					children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("style", { children: STYLES }), /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
						className: "oiwb-fatal",
						children: [
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", { children: "面板渲染出错" }),
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("p", {
								className: "oiwb-fatal-msg",
								children: this.state.error
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
								type: "button",
								className: "oiwb-btn primary",
								onClick: this.reset,
								children: "重试渲染"
							})
						]
					})]
				});
				return this.props.children;
			}
		};
		/** The workbench page state machine. */
		function Workbench() {
			const alive = (0, react.useRef)(true);
			(0, react.useEffect)(() => () => {
				alive.current = false;
			}, []);
			const [state, setState] = (0, react.useState)(null);
			const [loadError, setLoadError] = (0, react.useState)(null);
			const [loading, setLoading] = (0, react.useState)(true);
			const [tab, setTab] = (0, react.useState)("overview");
			const [busy, setBusy] = (0, react.useState)(null);
			const [log, setLog] = (0, react.useState)(null);
			const refresh = (0, react.useCallback)(async () => {
				setLoading(true);
				try {
					const result = await fetchState();
					if (!alive.current) return;
					if (result.ok) {
						setState(result.value);
						setLoadError(null);
					} else setLoadError(result.error);
				} catch (error) {
					if (alive.current) setLoadError(toMessage(error));
				} finally {
					if (alive.current) setLoading(false);
				}
			}, []);
			(0, react.useEffect)(() => {
				refresh();
			}, [refresh]);
			const run = (0, react.useCallback)(async (key, title, action) => {
				setBusy(key);
				setLog({
					title,
					tone: "running"
				});
				try {
					const result = await runAction(action);
					if (!alive.current) return false;
					if (!result.ok) {
						setLog({
							title,
							tone: "error",
							message: result.error
						});
						return false;
					}
					const outcome = result.value;
					setLog({
						title,
						tone: outcome.ok ? "ok" : "error",
						message: outcome.message,
						command: outcome.command
					});
					if (outcome.state !== void 0) {
						setState(outcome.state);
						setLoadError(null);
					}
					return outcome.ok;
				} catch (error) {
					if (alive.current) setLog({
						title,
						tone: "error",
						message: toMessage(error)
					});
					return false;
				} finally {
					if (alive.current) setBusy(null);
				}
			}, []);
			const counts = (0, react.useMemo)(() => ({
				problems: state?.problems?.length ?? 0,
				oj: state?.oj?.profiles?.length ?? 0,
				contests: state?.contests?.length ?? 0
			}), [state]);
			let body;
			if (state === null) body = /* @__PURE__ */ (0, react_jsx_runtime.jsx)(StatePlaceholder, {
				loading,
				error: loadError,
				onRetry: () => void refresh()
			});
			else if (tab === "problems") body = /* @__PURE__ */ (0, react_jsx_runtime.jsx)(ProblemsTab, {
				state,
				busy,
				run
			});
			else if (tab === "oj") body = /* @__PURE__ */ (0, react_jsx_runtime.jsx)(OjTab, {
				state,
				busy,
				run
			});
			else if (tab === "contests") body = /* @__PURE__ */ (0, react_jsx_runtime.jsx)(ContestsTab, {
				state,
				busy,
				run
			});
			else if (tab === "help") body = /* @__PURE__ */ (0, react_jsx_runtime.jsx)(HelpTab, { state });
			else body = /* @__PURE__ */ (0, react_jsx_runtime.jsx)(OverviewTab, {
				state,
				counts,
				onNavigate: setTab,
				onRefresh: () => void refresh()
			});
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("section", {
				className: "oiwb",
				"data-dsh-oiwb-view": "",
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("style", { children: STYLES }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("header", {
						className: "oiwb-head",
						children: [/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
							className: "oiwb-head-main",
							children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h1", {
								className: "oiwb-title",
								children: "OI 出题工作台"
							}), /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
								className: "oiwb-meta",
								children: [
									state !== null ? /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("span", {
										className: "oiwb-chip",
										children: ["v", state.version]
									}) : null,
									state !== null ? /* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
										className: state.skillRegistered ? "oiwb-chip is-ok" : "oiwb-chip is-warn",
										children: state.skillRegistered ? "skill 已注册" : "skill 未注册"
									}) : null,
									state !== null && state.root !== "" ? /* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
										className: "oiwb-meta-path",
										title: state.root,
										children: state.root
									}) : null
								]
							})]
						}), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
							className: "oiwb-head-actions",
							children: /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
								type: "button",
								className: "oiwb-btn",
								onClick: () => void refresh(),
								disabled: loading,
								children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(RefreshIcon, { size: 13 }), loading ? "刷新中…" : "刷新"]
							})
						})]
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("nav", {
						className: "oiwb-tabs",
						"aria-label": "OI 工作台导航",
						children: TABS.map((entry) => {
							const badge = state === null ? void 0 : tabBadge(entry.key, counts);
							return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
								type: "button",
								className: entry.key === tab ? "oiwb-tab is-active" : "oiwb-tab",
								onClick: () => setTab(entry.key),
								"aria-current": entry.key === tab ? "page" : void 0,
								children: [entry.label, badge === void 0 ? null : /* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
									className: "oiwb-tab-count",
									children: badge
								})]
							}, entry.key);
						})
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
						className: "oiwb-body",
						children: [loadError !== null ? /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
							className: "oiwb-banner is-error",
							role: "alert",
							children: [/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("span", { children: ["刷新失败：", loadError] }), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
								type: "button",
								className: "oiwb-btn",
								onClick: () => void refresh(),
								children: "重试"
							})]
						}) : null, body]
					}),
					log !== null ? /* @__PURE__ */ (0, react_jsx_runtime.jsx)(LogDrawer, {
						log,
						onDismiss: () => setLog(null)
					}) : null
				]
			});
		}
		/** Tab badge for the data tabs. */
		function tabBadge(key, counts) {
			if (key === "problems") return counts.problems;
			if (key === "oj") return counts.oj;
			if (key === "contests") return counts.contests;
		}
		/** First-load / hard-failure placeholder. */
		function StatePlaceholder(props) {
			if (props.loading) return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
				className: "oiwb-placeholder",
				children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { className: "oiwb-spinner" }), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", { children: "正在读取工作台状态…" })]
			});
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
				className: "oiwb-placeholder",
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", { children: props.error === null ? "无法读取工作台状态" : "读取工作台状态失败" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("p", { children: props.error ?? "宿主没有返回状态。请确认 DSH Web 由当前插件版本启动。" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
						type: "button",
						className: "oiwb-btn primary",
						onClick: props.onRetry,
						children: "重试"
					})
				]
			});
		}
		/** Overview tab: root, version, counts, skill registration. */
		function OverviewTab(props) {
			const { state, counts } = props;
			const active = (state.oj?.profiles ?? []).find((profile) => profile.id === state.oj.activeProfileId);
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
				className: "oiwb-stack",
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
						className: "oiwb-grid",
						children: [
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)(StatCard, {
								icon: /* @__PURE__ */ (0, react_jsx_runtime.jsx)(ListIcon, { size: 16 }),
								value: String(counts.problems),
								label: "题目包",
								hint: "已发现的题目目录"
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)(StatCard, {
								icon: /* @__PURE__ */ (0, react_jsx_runtime.jsx)(PlugIcon, { size: 16 }),
								value: String(counts.oj),
								label: "OJ 连接",
								hint: active === void 0 ? "未设置默认连接" : `默认：${active.name}`
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)(StatCard, {
								icon: /* @__PURE__ */ (0, react_jsx_runtime.jsx)(TrophyIcon, { size: 16 }),
								value: String(counts.contests),
								label: "比赛方案",
								hint: "已保存的可重建方案"
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)(StatCard, {
								icon: /* @__PURE__ */ (0, react_jsx_runtime.jsx)(DashboardIcon, { size: 16 }),
								value: state.skillRegistered ? "已注册" : "未注册",
								label: "skill",
								hint: "技能目录中的 oi-workbench",
								warn: !state.skillRegistered
							})
						]
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("section", {
						className: "oiwb-card",
						children: [
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", {
								className: "oiwb-card-title",
								children: "工作台"
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("dl", {
								className: "oiwb-kv",
								children: [
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dt", { children: "根目录" }),
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dd", { children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)("code", {
										className: "oiwb-code",
										children: state.root === "" ? "（未配置）" : state.root
									}) }),
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dt", { children: "插件版本" }),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("dd", { children: ["v", state.version] }),
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dt", { children: "技能名" }),
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dd", { children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)("code", {
										className: "oiwb-code",
										children: state.skill
									}) }),
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dt", { children: "默认 OJ" }),
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dd", { children: active === void 0 ? "未设置" : `${active.name}（${kindLabel(active.kind)}）` })
								]
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
								className: "oiwb-row",
								children: [
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
										type: "button",
										className: "oiwb-btn",
										onClick: props.onRefresh,
										children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(RefreshIcon, { size: 13 }), "刷新状态"]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
										type: "button",
										className: "oiwb-btn ghost",
										onClick: () => props.onNavigate("problems"),
										children: "查看题目"
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
										type: "button",
										className: "oiwb-btn ghost",
										onClick: () => props.onNavigate("help"),
										children: "使用帮助"
									})
								]
							})
						]
					}),
					state.skillRegistered ? null : /* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
						className: "oiwb-banner is-warn",
						children: /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("span", { children: [
							"skill 尚未注册：Agent 在对话中可能找不到 ",
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("code", {
								className: "oiwb-code",
								children: "oi-workbench"
							}),
							"。 请确认插件已安装并重启 DSH Web。"
						] })
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("section", {
						className: "oiwb-card",
						children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", {
							className: "oiwb-card-title",
							children: "推荐工作流"
						}), /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("ol", {
							className: "oiwb-steps",
							children: [
								/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("strong", { children: "检查" }), "：确认题面、题解、std、数据与 spec.json 齐全"] }),
								/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("strong", { children: "构建" }), "：生成 Hydro / HOJ 原生题目包"] }),
								/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("strong", { children: "评测" }), "：本地跑 std，确认数据强度和时限"] }),
								/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("strong", { children: "发布" }), "：把题目包导入目标 OJ"] })
							]
						})]
					})
				]
			});
		}
		/** One overview stat tile. */
		function StatCard(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
				className: props.warn === true ? "oiwb-stat is-warn" : "oiwb-stat",
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
						className: "oiwb-stat-icon",
						children: props.icon
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
						className: "oiwb-stat-value",
						children: props.value
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
						className: "oiwb-stat-label",
						children: props.label
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
						className: "oiwb-stat-hint",
						children: props.hint
					})
				]
			});
		}
		/** Problems tab: list, badges, per-problem actions, inline judge form. */
		function ProblemsTab(props) {
			const problems = props.state.problems ?? [];
			const [targets, setTargets] = (0, react.useState)({});
			const [judgeDir, setJudgeDir] = (0, react.useState)(null);
			const [judgeSource, setJudgeSource] = (0, react.useState)("std/std.cpp");
			const [judgeLimit, setJudgeLimit] = (0, react.useState)("1000");
			const [judgeError, setJudgeError] = (0, react.useState)(null);
			const disabled = props.busy !== null;
			const openJudge = (problem) => {
				setJudgeDir((current) => current === problem.path ? null : problem.path);
				setJudgeSource("std/std.cpp");
				setJudgeLimit("1000");
				setJudgeError(null);
			};
			const submitJudge = (problem) => {
				const source = judgeSource.trim();
				const limit = Number.parseInt(judgeLimit.trim(), 10);
				if (source === "") {
					setJudgeError("请填写评测源码路径（相对题目目录）");
					return;
				}
				if (!Number.isFinite(limit) || limit < 1 || limit > 6e5) {
					setJudgeError("时限需为 1–600000 之间的整数（毫秒）");
					return;
				}
				setJudgeError(null);
				setJudgeDir(null);
				props.run(`judge:${problem.path}`, `本地评测 ${problem.name}`, {
					kind: "judge",
					dir: problem.path,
					source,
					timeLimitMs: limit
				});
			};
			if (problems.length === 0) return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
				className: "oiwb-placeholder",
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", { children: "还没有发现题目包" }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("p", { children: [
						"在工作台根目录下创建题目目录（含 ",
						/* @__PURE__ */ (0, react_jsx_runtime.jsx)("code", {
							className: "oiwb-code",
							children: "spec.json"
						}),
						"）后点击「刷新」。"
					] }),
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("p", {
						className: "oiwb-hint",
						children: ["当前根目录：", /* @__PURE__ */ (0, react_jsx_runtime.jsx)("code", {
							className: "oiwb-code",
							children: props.state.root
						})]
					})
				]
			});
			return /* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
				className: "oiwb-stack",
				children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
					className: "oiwb-problems",
					children: problems.map((problem) => {
						const target = targets[problem.name] ?? "both";
						return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("article", {
							className: "oiwb-problem",
							children: [/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
								className: "oiwb-problem-row",
								children: [
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
										className: "oiwb-problem-name",
										title: problem.name,
										children: problem.name
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
										className: "oiwb-badges",
										children: [
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)(Badge, {
												ok: problem.badges.hasProblemMd,
												label: "题面"
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)(Badge, {
												ok: problem.badges.hasSolution,
												label: "题解"
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)(Badge, {
												ok: problem.badges.hasStd,
												label: "std"
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)(Badge, {
												ok: problem.badges.hasData,
												label: "数据"
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("span", {
												className: "oiwb-badge is-count",
												children: ["测试点 ", problem.badges.caseCount]
											})
										]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
										className: "oiwb-problem-actions",
										children: [
											/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
												type: "button",
												className: "oiwb-btn",
												disabled,
												onClick: () => void props.run(`check:${problem.path}`, `检查 ${problem.name}`, {
													kind: "check",
													dir: problem.path
												}),
												children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(CheckIcon, { size: 13 }), "检查"]
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("select", {
												className: "oiwb-select",
												"aria-label": `${problem.name} 构建目标`,
												value: target,
												disabled,
												onChange: (event) => {
													const value = event.target.value;
													setTargets((current) => ({
														...current,
														[problem.name]: value === "hydro" || value === "hoj" ? value : "both"
													}));
												},
												children: [
													/* @__PURE__ */ (0, react_jsx_runtime.jsx)("option", {
														value: "both",
														children: "两者"
													}),
													/* @__PURE__ */ (0, react_jsx_runtime.jsx)("option", {
														value: "hydro",
														children: "Hydro"
													}),
													/* @__PURE__ */ (0, react_jsx_runtime.jsx)("option", {
														value: "hoj",
														children: "HOJ"
													})
												]
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
												type: "button",
												className: "oiwb-btn",
												disabled,
												onClick: () => void props.run(`build:${problem.path}`, `构建 ${problem.name}（${targetLabel(target)}）`, {
													kind: "build",
													dir: problem.path,
													target
												}),
												children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(BoxIcon, { size: 13 }), "构建"]
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
												type: "button",
												className: judgeDir === problem.path ? "oiwb-btn is-active" : "oiwb-btn",
												disabled,
												onClick: () => openJudge(problem),
												children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(PlayIcon, { size: 13 }), "评测"]
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
												type: "button",
												className: "oiwb-btn ghost",
												disabled,
												onClick: () => void props.run(`open:${problem.path}`, `打开目录 ${problem.name}`, {
													kind: "open",
													dir: problem.path
												}),
												children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(FolderIcon, { size: 13 }), "打开目录"]
											})
										]
									})
								]
							}), judgeDir === problem.path ? /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
								className: "oiwb-judge",
								children: [
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("label", {
										className: "oiwb-field",
										children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { children: "源码路径（相对题目目录）" }), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("input", {
											className: "oiwb-input",
											value: judgeSource,
											onChange: (event) => setJudgeSource(event.target.value),
											placeholder: "std/std.cpp"
										})]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("label", {
										className: "oiwb-field oiwb-judge-limit",
										children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { children: "时限（毫秒）" }), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("input", {
											className: "oiwb-input",
											inputMode: "numeric",
											value: judgeLimit,
											onChange: (event) => setJudgeLimit(event.target.value),
											placeholder: "1000"
										})]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
										type: "button",
										className: "oiwb-btn primary",
										disabled,
										onClick: () => submitJudge(problem),
										children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(PlayIcon, { size: 13 }), "开始评测"]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
										type: "button",
										className: "oiwb-btn ghost",
										onClick: () => setJudgeDir(null),
										children: "取消"
									}),
									judgeError === null ? null : /* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
										className: "oiwb-form-error",
										children: judgeError
									})
								]
							}) : null]
						}, problem.name);
					})
				})
			});
		}
		/** One presence badge. */
		function Badge(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
				className: props.ok ? "oiwb-badge is-on" : "oiwb-badge is-off",
				children: props.label
			});
		}
		/** First free generated profile id. */
		function nextProfileId(profiles) {
			const taken = new Set(profiles.map((profile) => profile.id));
			for (let index = 1; index < 1e3; index += 1) {
				const candidate = `hydro-${index}`;
				if (!taken.has(candidate)) return candidate;
			}
			return "hydro-new";
		}
		/** OJ tab: profiles, credential-env note, add/edit form. */
		function OjTab(props) {
			const profiles = props.state.oj?.profiles ?? [];
			const [draft, setDraft] = (0, react.useState)(null);
			const [editing, setEditing] = (0, react.useState)(false);
			const [formError, setFormError] = (0, react.useState)(null);
			const [pendingDelete, setPendingDelete] = (0, react.useState)(null);
			const disabled = props.busy !== null;
			(0, react.useEffect)(() => {
				if (pendingDelete === null) return void 0;
				const timer = setTimeout(() => setPendingDelete(null), 5e3);
				return () => clearTimeout(timer);
			}, [pendingDelete]);
			const openNew = () => {
				setDraft({
					id: nextProfileId(profiles),
					kind: "hydro",
					name: "",
					base: "",
					user: "",
					credentialEnv: ""
				});
				setEditing(false);
				setFormError(null);
				setPendingDelete(null);
			};
			const openEdit = (profile) => {
				setDraft({
					id: profile.id,
					kind: profile.kind,
					name: profile.name,
					base: profile.base,
					user: profile.user,
					credentialEnv: profile.credentialEnv
				});
				setEditing(true);
				setFormError(null);
				setPendingDelete(null);
			};
			const submit = () => {
				if (draft === null) return;
				const id = draft.id.trim();
				const base = draft.base.trim();
				const name = draft.name.trim() === "" ? id : draft.name.trim();
				if (id === "") {
					setFormError("请填写连接 id");
					return;
				}
				if (/\s/.test(id)) {
					setFormError("连接 id 不能包含空白字符");
					return;
				}
				if (base === "") {
					setFormError("请填写实例地址（base）");
					return;
				}
				if (!/^https?:\/\//i.test(base)) {
					setFormError("实例地址需以 http:// 或 https:// 开头");
					return;
				}
				if (draft.credentialEnv.trim() === "") {
					setFormError("请填写凭据环境变量名（例如 HYDRO_PASSWORD）");
					return;
				}
				const profile = {
					id,
					kind: draft.kind,
					name,
					base,
					user: draft.user.trim(),
					credentialEnv: draft.credentialEnv.trim()
				};
				setFormError(null);
				props.run(`oj-save:${id}`, `保存 OJ 连接 ${name}`, {
					kind: "oj-save",
					profile
				}).then((ok) => {
					if (ok) {
						setDraft(null);
						setEditing(false);
					}
				});
			};
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
				className: "oiwb-stack",
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
						className: "oiwb-banner",
						children: [
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)(PlugIcon, { size: 14 }),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("span", { children: [
								"密码 / Token 不写进面板：这里只保存",
								/* @__PURE__ */ (0, react_jsx_runtime.jsx)("strong", { children: "环境变量名" }),
								"，真实凭据由 DSH 进程的环境提供。"
							] }),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
								type: "button",
								className: "oiwb-btn primary",
								onClick: openNew,
								disabled,
								children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(PlusIcon, { size: 13 }), "新增连接"]
							})
						]
					}),
					draft !== null ? /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("section", {
						className: "oiwb-form",
						children: [
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", {
								className: "oiwb-card-title",
								children: editing ? `编辑连接 ${draft.id}` : "新增 OJ 连接"
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
								className: "oiwb-form-grid",
								children: [
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("label", {
										className: "oiwb-field",
										children: [
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { children: "id" }),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("input", {
												className: "oiwb-input",
												value: draft.id,
												disabled: editing,
												onChange: (event) => setDraft({
													...draft,
													id: event.target.value
												}),
												placeholder: "hydro-main"
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
												className: "oiwb-hint",
												children: editing ? "id 是稳定的本地标识，编辑时不可修改" : "稳定本地标识，建议小写短横线"
											})
										]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("label", {
										className: "oiwb-field",
										children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { children: "OJ 类型" }), /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("select", {
											className: "oiwb-select",
											value: draft.kind,
											onChange: (event) => setDraft({
												...draft,
												kind: event.target.value === "hoj" ? "hoj" : "hydro"
											}),
											children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("option", {
												value: "hydro",
												children: "Hydro"
											}), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("option", {
												value: "hoj",
												children: "HOJ"
											})]
										})]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("label", {
										className: "oiwb-field",
										children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { children: "显示名称" }), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("input", {
											className: "oiwb-input",
											value: draft.name,
											onChange: (event) => setDraft({
												...draft,
												name: event.target.value
											}),
											placeholder: "例如 主站 Hydro"
										})]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("label", {
										className: "oiwb-field",
										children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { children: "实例地址（base）" }), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("input", {
											className: "oiwb-input",
											value: draft.base,
											onChange: (event) => setDraft({
												...draft,
												base: event.target.value
											}),
											placeholder: "https://hydro.example.com"
										})]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("label", {
										className: "oiwb-field",
										children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { children: "用户名" }), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("input", {
											className: "oiwb-input",
											value: draft.user,
											onChange: (event) => setDraft({
												...draft,
												user: event.target.value
											}),
											placeholder: "可留空（仅用 Cookie / Token 时）"
										})]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("label", {
										className: "oiwb-field",
										children: [
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { children: "凭据环境变量名" }),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("input", {
												className: "oiwb-input",
												value: draft.credentialEnv,
												onChange: (event) => setDraft({
													...draft,
													credentialEnv: event.target.value
												}),
												placeholder: "HYDRO_PASSWORD"
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
												className: "oiwb-hint",
												children: "只填变量名，不填明文密码"
											})
										]
									})
								]
							}),
							formError === null ? null : /* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
								className: "oiwb-form-error",
								children: formError
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
								className: "oiwb-form-actions",
								children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
									type: "button",
									className: "oiwb-btn ghost",
									onClick: () => setDraft(null),
									children: "取消"
								}), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
									type: "button",
									className: "oiwb-btn primary",
									disabled,
									onClick: submit,
									children: editing ? "保存修改" : "保存连接"
								})]
							})
						]
					}) : null,
					profiles.length === 0 ? /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
						className: "oiwb-placeholder",
						children: [
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", { children: "还没有 OJ 连接" }),
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("p", { children: "新增一个 Hydro 或 HOJ 连接后，就可以在发布流程中引用它。" }),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
								type: "button",
								className: "oiwb-btn primary",
								onClick: openNew,
								children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(PlusIcon, { size: 13 }), "新增连接"]
							})
						]
					}) : /* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
						className: "oiwb-oj-list",
						children: profiles.map((profile) => {
							const isActive = profile.id === props.state.oj.activeProfileId;
							return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("article", {
								className: "oiwb-oj-card",
								children: [
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
										className: "oiwb-oj-head",
										children: [
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
												className: profile.kind === "hydro" ? "oiwb-kind is-hydro" : "oiwb-kind is-hoj",
												children: kindLabel(profile.kind)
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
												className: "oiwb-oj-name",
												children: profile.name
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("code", {
												className: "oiwb-code",
												children: profile.id
											}),
											isActive ? /* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
												className: "oiwb-tag",
												children: "默认"
											}) : null
										]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("dl", {
										className: "oiwb-kv",
										children: [
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dt", { children: "地址" }),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dd", { children: profile.base }),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dt", { children: "用户名" }),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dd", { children: profile.user === "" ? "（未设置）" : profile.user }),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dt", { children: "凭据环境变量" }),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dd", { children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)("code", {
												className: "oiwb-code",
												children: profile.credentialEnv === "" ? "（未设置）" : profile.credentialEnv
											}) })
										]
									}),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
										className: "oiwb-oj-actions",
										children: [
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
												type: "button",
												className: "oiwb-btn",
												disabled: disabled || isActive,
												onClick: () => void props.run(`oj-active:${profile.id}`, `设为默认连接 ${profile.name}`, {
													kind: "oj-set-active",
													id: profile.id
												}),
												children: "设为默认"
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
												type: "button",
												className: "oiwb-btn",
												disabled,
												onClick: () => void props.run(`oj-test:${profile.id}`, `连接测试 ${profile.name}`, {
													kind: "oj-test",
													id: profile.id
												}),
												children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(PlugIcon, { size: 13 }), "连接测试"]
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
												type: "button",
												className: "oiwb-btn ghost",
												disabled,
												onClick: () => openEdit(profile),
												children: "编辑"
											}),
											/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
												type: "button",
												className: pendingDelete === profile.id ? "oiwb-btn danger is-confirm" : "oiwb-btn danger",
												disabled,
												onClick: () => {
													if (pendingDelete !== profile.id) {
														setPendingDelete(profile.id);
														return;
													}
													setPendingDelete(null);
													props.run(`oj-delete:${profile.id}`, `删除连接 ${profile.name}`, {
														kind: "oj-delete",
														id: profile.id
													});
												},
												children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(TrashIcon, { size: 13 }), pendingDelete === profile.id ? "确认删除？" : "删除"]
											})
										]
									})
								]
							}, profile.id);
						})
					})
				]
			});
		}
		/** First free generated contest id. */
		function nextContestId(contests) {
			const taken = new Set(contests.map((contest) => contest.id));
			for (let index = 1; index < 1e3; index += 1) {
				const candidate = `contest-${index}`;
				if (!taken.has(candidate)) return candidate;
			}
			return "contest-new";
		}
		/** Contests tab: saved plans, new plan form, build. */
		function ContestsTab(props) {
			const contests = props.state.contests ?? [];
			const problems = props.state.problems ?? [];
			const [draft, setDraft] = (0, react.useState)(null);
			const [formError, setFormError] = (0, react.useState)(null);
			const [pendingDelete, setPendingDelete] = (0, react.useState)(null);
			const disabled = props.busy !== null;
			(0, react.useEffect)(() => {
				if (pendingDelete === null) return void 0;
				const timer = setTimeout(() => setPendingDelete(null), 5e3);
				return () => clearTimeout(timer);
			}, [pendingDelete]);
			const openNew = () => {
				setDraft({
					id: nextContestId(contests),
					title: "",
					problems: []
				});
				setFormError(null);
				setPendingDelete(null);
			};
			const toggleProblem = (name) => {
				setDraft((current) => {
					if (current === null) return current;
					const selected = current.problems.includes(name) ? current.problems.filter((entry) => entry !== name) : [...current.problems, name];
					return {
						...current,
						problems: selected
					};
				});
			};
			const submit = () => {
				if (draft === null) return;
				const id = draft.id.trim();
				const title = draft.title.trim();
				if (id === "") {
					setFormError("请填写比赛 id");
					return;
				}
				if (/\s/.test(id)) {
					setFormError("比赛 id 不能包含空白字符");
					return;
				}
				if (title === "") {
					setFormError("请填写比赛标题");
					return;
				}
				if (draft.problems.length === 0) {
					setFormError("请至少选择一个题目");
					return;
				}
				setFormError(null);
				props.run(`contest-save:${id}`, `保存比赛方案 ${title}`, {
					kind: "contest-save",
					contest: {
						id,
						title,
						problems: draft.problems
					}
				}).then((ok) => {
					if (ok) setDraft(null);
				});
			};
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
				className: "oiwb-stack",
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
						className: "oiwb-row",
						children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
							className: "oiwb-hint",
							children: "比赛方案保存题目列表，可随时用当前工具链重新构建。"
						}), /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
							type: "button",
							className: "oiwb-btn primary",
							onClick: openNew,
							disabled,
							children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(PlusIcon, { size: 13 }), "新建比赛"]
						})]
					}),
					draft !== null ? /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("section", {
						className: "oiwb-form",
						children: [
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", {
								className: "oiwb-card-title",
								children: "新建比赛方案"
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
								className: "oiwb-form-grid",
								children: [/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("label", {
									className: "oiwb-field",
									children: [
										/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { children: "比赛 id" }),
										/* @__PURE__ */ (0, react_jsx_runtime.jsx)("input", {
											className: "oiwb-input",
											value: draft.id,
											onChange: (event) => setDraft({
												...draft,
												id: event.target.value
											}),
											placeholder: "contest-1"
										}),
										/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
											className: "oiwb-hint",
											children: "本地标识，建议小写短横线"
										})
									]
								}), /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("label", {
									className: "oiwb-field",
									children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { children: "比赛标题" }), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("input", {
										className: "oiwb-input",
										value: draft.title,
										onChange: (event) => setDraft({
											...draft,
											title: event.target.value
										}),
										placeholder: "例如 2026 春季训练赛 Round 1"
									})]
								})]
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
								className: "oiwb-field",
								children: [/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("span", { children: [
									"题目（已选 ",
									draft.problems.length,
									"）"
								] }), problems.length === 0 ? /* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
									className: "oiwb-hint",
									children: "工作台里还没有题目，先到「题目」页刷新。"
								}) : /* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
									className: "oiwb-picker",
									children: problems.map((problem) => /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("label", {
										className: "oiwb-pick",
										children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("input", {
											type: "checkbox",
											checked: draft.problems.includes(problem.name),
											onChange: () => toggleProblem(problem.name)
										}), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { children: problem.name })]
									}, problem.name))
								})]
							}),
							formError === null ? null : /* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
								className: "oiwb-form-error",
								children: formError
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
								className: "oiwb-form-actions",
								children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
									type: "button",
									className: "oiwb-btn ghost",
									onClick: () => setDraft(null),
									children: "取消"
								}), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
									type: "button",
									className: "oiwb-btn primary",
									disabled,
									onClick: submit,
									children: "保存方案"
								})]
							})
						]
					}) : null,
					contests.length === 0 ? /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
						className: "oiwb-placeholder",
						children: [
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", { children: "还没有比赛方案" }),
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("p", { children: "把若干题目组合成一个方案，之后可以一键重新构建。" }),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
								type: "button",
								className: "oiwb-btn primary",
								onClick: openNew,
								children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(PlusIcon, { size: 13 }), "新建比赛"]
							})
						]
					}) : /* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
						className: "oiwb-contests",
						children: contests.map((contest) => /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("article", {
							className: "oiwb-contest-card",
							children: [
								/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
									className: "oiwb-oj-head",
									children: [
										/* @__PURE__ */ (0, react_jsx_runtime.jsx)(TrophyIcon, { size: 14 }),
										/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
											className: "oiwb-contest-title",
											children: contest.title
										}),
										/* @__PURE__ */ (0, react_jsx_runtime.jsx)("code", {
											className: "oiwb-code",
											children: contest.id
										}),
										/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("span", {
											className: "oiwb-hint",
											children: ["更新于 ", formatTime(contest.updatedAt)]
										})
									]
								}),
								/* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
									className: "oiwb-contest-problems",
									children: (contest.problems ?? []).length === 0 ? /* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
										className: "oiwb-hint",
										children: "（未包含题目）"
									}) : (contest.problems ?? []).map((name) => /* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
										className: "oiwb-chip",
										children: name
									}, name))
								}),
								/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
									className: "oiwb-oj-actions",
									children: [/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
										type: "button",
										className: "oiwb-btn",
										disabled,
										onClick: () => void props.run(`contest-build:${contest.id}`, `构建比赛 ${contest.title}`, {
											kind: "contest-build",
											id: contest.id
										}),
										children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(BoxIcon, { size: 13 }), "构建"]
									}), /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("button", {
										type: "button",
										className: pendingDelete === contest.id ? "oiwb-btn danger is-confirm" : "oiwb-btn danger",
										disabled,
										onClick: () => {
											if (pendingDelete !== contest.id) {
												setPendingDelete(contest.id);
												return;
											}
											setPendingDelete(null);
											props.run(`contest-delete:${contest.id}`, `删除比赛 ${contest.title}`, {
												kind: "contest-delete",
												id: contest.id
											});
										},
										children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(TrashIcon, { size: 13 }), pendingDelete === contest.id ? "确认删除？" : "删除"]
									})]
								})
							]
						}, contest.id))
					})
				]
			});
		}
		/** Help tab: capabilities, workflow, safety boundary, skill name. */
		function HelpTab(props) {
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
				className: "oiwb-stack",
				children: [
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("section", {
						className: "oiwb-card",
						children: [/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("h2", {
							className: "oiwb-card-title",
							children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(HelpIcon, { size: 14 }), "这个面板能做什么"]
						}), /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("ul", {
							className: "oiwb-list",
							children: [
								/* @__PURE__ */ (0, react_jsx_runtime.jsx)("li", { children: "检查题目包结构：题面、题解、std、数据、spec.json 是否齐全" }),
								/* @__PURE__ */ (0, react_jsx_runtime.jsx)("li", { children: "构建 Hydro / HOJ 原生题目包" }),
								/* @__PURE__ */ (0, react_jsx_runtime.jsx)("li", { children: "本地评测 std 代码，查看命令输出、退出码与耗时" }),
								/* @__PURE__ */ (0, react_jsx_runtime.jsx)("li", { children: "管理 Hydro / HOJ 连接与比赛方案" })
							]
						})]
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("section", {
						className: "oiwb-card",
						children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", {
							className: "oiwb-card-title",
							children: "推荐工作流"
						}), /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("ol", {
							className: "oiwb-steps",
							children: [
								/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("strong", { children: "检查" }), "：确认题目包结构完整，缺什么补什么"] }),
								/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("strong", { children: "构建" }), "：生成 Hydro / HOJ 题目包（可双目标）"] }),
								/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("strong", { children: "评测" }), "：本地跑 std，确认数据强度与时限"] }),
								/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("strong", { children: "发布" }), "：在目标 OJ 中导入题目包"] })
							]
						})]
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("section", {
						className: "oiwb-card",
						children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", {
							className: "oiwb-card-title",
							children: "安全边界"
						}), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("p", {
							className: "oiwb-text",
							children: "面板只向宿主发送结构化参数，由宿主在工作台根目录内执行固定工具链； 密码与 Token 只通过环境变量名引用，不在面板中输入或保存明文。"
						})]
					}),
					/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("section", {
						className: "oiwb-card",
						children: [
							/* @__PURE__ */ (0, react_jsx_runtime.jsx)("h2", {
								className: "oiwb-card-title",
								children: "技能"
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("p", {
								className: "oiwb-text",
								children: [
									"在对话中提及技能名 ",
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("code", {
										className: "oiwb-code",
										children: "oi-workbench"
									}),
									"， Agent 会按出题流程执行（当前状态：",
									props.state.skillRegistered ? "已注册" : "未注册",
									"）。"
								]
							}),
							/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("dl", {
								className: "oiwb-kv",
								children: [
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dt", { children: "根目录" }),
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dd", { children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)("code", {
										className: "oiwb-code",
										children: props.state.root === "" ? "（未配置）" : props.state.root
									}) }),
									/* @__PURE__ */ (0, react_jsx_runtime.jsx)("dt", { children: "插件版本" }),
									/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("dd", { children: ["v", props.state.version] })
								]
							})
						]
					})
				]
			});
		}
		/** Bottom command log: message, argv, stdout, stderr, timing. */
		function LogDrawer(props) {
			const [expanded, setExpanded] = (0, react.useState)(true);
			const toneClass = props.log.tone === "ok" ? "oiwb-log-tone is-ok" : props.log.tone === "error" ? "oiwb-log-tone is-error" : "oiwb-log-tone is-running";
			const toneText = props.log.tone === "ok" ? "完成" : props.log.tone === "error" ? "失败" : "进行中";
			const command = props.log.command;
			const stdout = command?.stdout ?? "";
			const stderr = command?.stderr ?? "";
			return /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("section", {
				className: "oiwb-log",
				"aria-live": "polite",
				children: [/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("header", {
					className: "oiwb-log-head",
					children: [
						/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("span", {
							className: "oiwb-log-title",
							children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)(TerminalIcon, { size: 13 }), props.log.title]
						}),
						/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", {
							className: toneClass,
							children: toneText
						}),
						command === void 0 ? null : /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("span", {
							className: "oiwb-log-meta",
							children: [
								"退出码 ",
								command.exitCode,
								" · ",
								command.durationMs,
								" ms"
							]
						}),
						/* @__PURE__ */ (0, react_jsx_runtime.jsxs)("span", {
							className: "oiwb-log-actions",
							children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
								type: "button",
								className: "oiwb-btn ghost",
								onClick: () => setExpanded((value) => !value),
								children: expanded ? "收起" : "展开"
							}), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("button", {
								type: "button",
								className: "oiwb-btn icon",
								"aria-label": "关闭日志",
								onClick: props.onDismiss,
								children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)(CloseIcon, { size: 12 })
							})]
						})
					]
				}), expanded ? /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
					className: "oiwb-log-body",
					children: [
						props.log.message === void 0 || props.log.message === "" ? null : /* @__PURE__ */ (0, react_jsx_runtime.jsx)("p", {
							className: "oiwb-log-msg",
							children: props.log.message
						}),
						props.log.tone === "running" ? /* @__PURE__ */ (0, react_jsx_runtime.jsxs)("div", {
							className: "oiwb-running",
							children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("span", { className: "oiwb-spinner" }), "执行中…"]
						}) : null,
						command === void 0 ? null : /* @__PURE__ */ (0, react_jsx_runtime.jsxs)(react_jsx_runtime.Fragment, { children: [
							command.argv.length === 0 ? null : /* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
								className: "oiwb-log-argv",
								children: /* @__PURE__ */ (0, react_jsx_runtime.jsx)("code", { children: command.argv.join(" ") })
							}),
							stdout.trim() === "" ? null : /* @__PURE__ */ (0, react_jsx_runtime.jsxs)(react_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
								className: "oiwb-log-label",
								children: "stdout"
							}), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("pre", {
								className: "oiwb-pre",
								children: stdout
							})] }),
							stderr.trim() === "" ? null : /* @__PURE__ */ (0, react_jsx_runtime.jsxs)(react_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, react_jsx_runtime.jsx)("div", {
								className: "oiwb-log-label is-error",
								children: "stderr"
							}), /* @__PURE__ */ (0, react_jsx_runtime.jsx)("pre", {
								className: "oiwb-pre is-error",
								children: stderr
							})] }),
							stdout.trim() === "" && stderr.trim() === "" ? /* @__PURE__ */ (0, react_jsx_runtime.jsx)("p", {
								className: "oiwb-log-msg",
								children: "（没有命令输出）"
							}) : null
						] })
					]
				}) : null]
			});
		}
		/**
		* Panel styles. Every selector is scoped by the panel's own data attribute and
		* every color reads a `--dsw-*` theme token first, so light, dark and skinned
		* themes keep native contrast. No CSS-module build chain is involved.
		*/
		const STYLES = `
[data-dsh-oiwb-view] {
  --oiwb-border: var(--dsw-alias-border-l2, rgba(128, 128, 128, 0.28));
  --oiwb-border-strong: var(--dsw-alias-border-l3, rgba(128, 128, 128, 0.42));
  --oiwb-bg: var(--dsw-alias-bg-subtle, rgba(128, 128, 128, 0.06));
  --oiwb-bg-hover: var(--dsw-alias-interactive-bg-hover, rgba(128, 128, 128, 0.13));
  --oiwb-input-bg: var(--dsw-specific-input-major, rgba(128, 128, 128, 0.08));
  --oiwb-text: var(--dsw-alias-label-primary, #e4e4e4);
  --oiwb-text-2: var(--dsw-alias-label-secondary, #a4a4a4);
  --oiwb-text-3: var(--dsw-alias-label-tertiary, #7c7c7c);
  --oiwb-brand: var(--dsw-alias-brand-primary, #4a9eff);
  --oiwb-brand-fill: var(--dsw-alias-button-primary-fill, #3b82f6);
  --oiwb-on-brand: var(--dsw-alias-label-primary-inverted, #ffffff);
  --oiwb-danger: var(--dsw-alias-label-danger, #ff6b6b);
  --oiwb-warning: var(--dsw-alias-label-warning, #f0a63c);
  --oiwb-success: var(--dsw-alias-detail-success, #3fb950);
  --oiwb-mono: var(--dsw-alias-font-mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace);
  --oiwb-font: var(--dsw-font-family, system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif);

  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  background: var(--dsw-alias-bg-base, transparent);
  color: var(--oiwb-text);
  font-family: var(--oiwb-font);
  font-size: 13px;
  line-height: 1.55;
  container-type: inline-size;
}
[data-dsh-oiwb-view] *,
[data-dsh-oiwb-view] *::before,
[data-dsh-oiwb-view] *::after {
  box-sizing: border-box;
}
[data-dsh-oiwb-view] h1,
[data-dsh-oiwb-view] h2,
[data-dsh-oiwb-view] p {
  margin: 0;
}
[data-dsh-oiwb-view] code {
  font-family: var(--oiwb-mono);
  font-size: 11.5px;
}

/* --- header ---------------------------------------------------------------- */
.oiwb-head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: none;
  padding: 16px 20px 10px;
}
.oiwb-head-main {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}
.oiwb-title {
  font-size: 17px;
  font-weight: 700;
  line-height: 1.3;
  color: var(--oiwb-text);
}
.oiwb-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  min-width: 0;
}
.oiwb-meta-path {
  max-width: 46ch;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--oiwb-mono);
  font-size: 11px;
  color: var(--oiwb-text-3);
}
.oiwb-head-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  flex: none;
}
.oiwb-chip {
  display: inline-flex;
  align-items: center;
  height: 20px;
  padding: 0 8px;
  border-radius: 10px;
  border: 1px solid var(--oiwb-border);
  background: var(--oiwb-bg);
  color: var(--oiwb-text-2);
  font-size: 11px;
  white-space: nowrap;
}
.oiwb-chip.is-ok {
  color: var(--oiwb-success);
}
.oiwb-chip.is-warn {
  color: var(--oiwb-warning);
}

/* --- tabs ------------------------------------------------------------------ */
.oiwb-tabs {
  display: flex;
  align-items: stretch;
  gap: 2px;
  flex: none;
  padding: 0 12px;
  border-bottom: 1px solid var(--oiwb-border);
  overflow-x: auto;
}
.oiwb-tab {
  appearance: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px 9px;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--oiwb-text-2);
  font: inherit;
  font-size: 13px;
  white-space: nowrap;
  cursor: pointer;
}
.oiwb-tab:hover {
  color: var(--oiwb-text);
  background: var(--oiwb-bg);
}
.oiwb-tab.is-active {
  color: var(--oiwb-text);
  font-weight: 600;
  border-bottom-color: var(--oiwb-brand);
}
.oiwb-tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  background: var(--oiwb-bg);
  color: var(--oiwb-text-2);
  font-size: 10.5px;
  font-weight: 500;
}

/* --- body ------------------------------------------------------------------ */
.oiwb-body {
  flex: 1 1 auto;
  min-height: 0;
  overflow: auto;
  padding: 16px 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.oiwb-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}
.oiwb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 10px;
}
.oiwb-stat {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 12px 14px;
  border: 1px solid var(--oiwb-border);
  border-radius: 12px;
  background: var(--oiwb-bg);
  min-width: 0;
}
.oiwb-stat-icon {
  position: absolute;
  top: 12px;
  right: 12px;
  color: var(--oiwb-text-3);
}
.oiwb-stat-value {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.25;
  color: var(--oiwb-text);
}
.oiwb-stat-label {
  font-size: 12px;
  color: var(--oiwb-text-2);
}
.oiwb-stat-hint {
  margin-top: 2px;
  font-size: 11px;
  color: var(--oiwb-text-3);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.oiwb-stat.is-warn .oiwb-stat-value {
  color: var(--oiwb-warning);
}
.oiwb-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px 16px;
  border: 1px solid var(--oiwb-border);
  border-radius: 12px;
  background: var(--oiwb-bg);
  min-width: 0;
}
.oiwb-card-title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 650;
  color: var(--oiwb-text);
}
.oiwb-kv {
  display: grid;
  grid-template-columns: max-content minmax(0, 1fr);
  gap: 6px 16px;
  margin: 0;
  font-size: 12.5px;
}
.oiwb-kv dt {
  color: var(--oiwb-text-2);
  white-space: nowrap;
}
.oiwb-kv dd {
  margin: 0;
  color: var(--oiwb-text);
  overflow-wrap: anywhere;
  min-width: 0;
}
.oiwb-code {
  padding: 1px 6px;
  border-radius: 5px;
  background: var(--dsw-alias-bg-layer, rgba(128, 128, 128, 0.14));
  color: var(--oiwb-text);
  overflow-wrap: anywhere;
}
.oiwb-text {
  font-size: 12.5px;
  color: var(--oiwb-text-2);
}
.oiwb-hint {
  font-size: 11.5px;
  color: var(--oiwb-text-3);
}
.oiwb-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* --- controls -------------------------------------------------------------- */
.oiwb-btn {
  appearance: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 30px;
  padding: 0 11px;
  border: 1px solid var(--oiwb-border);
  border-radius: 8px;
  background: transparent;
  color: var(--oiwb-text);
  font: inherit;
  font-size: 12.5px;
  line-height: 1;
  white-space: nowrap;
  cursor: pointer;
}
.oiwb-btn:hover:not(:disabled) {
  background: var(--oiwb-bg-hover);
}
.oiwb-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.oiwb-btn.is-active {
  background: var(--oiwb-bg-hover);
  border-color: var(--oiwb-border-strong);
}
.oiwb-btn.primary {
  background: var(--oiwb-brand-fill);
  border-color: transparent;
  color: var(--oiwb-on-brand);
}
.oiwb-btn.primary:hover:not(:disabled) {
  background: var(--dsw-alias-button-primary-hover, var(--oiwb-brand-fill));
}
.oiwb-btn.ghost {
  border-color: transparent;
  background: transparent;
  color: var(--oiwb-text-2);
}
.oiwb-btn.ghost:hover:not(:disabled) {
  color: var(--oiwb-text);
  background: var(--oiwb-bg-hover);
}
.oiwb-btn.danger {
  color: var(--oiwb-danger);
}
.oiwb-btn.danger.is-confirm {
  border-color: var(--oiwb-danger);
  background: transparent;
}
.oiwb-btn.icon {
  width: 26px;
  height: 26px;
  padding: 0;
  border-color: transparent;
  background: transparent;
  color: var(--oiwb-text-3);
}
.oiwb-btn.icon:hover:not(:disabled) {
  color: var(--oiwb-text);
  background: var(--oiwb-bg-hover);
}
.oiwb-input,
.oiwb-select {
  height: 30px;
  min-width: 0;
  padding: 0 9px;
  border: 1px solid var(--oiwb-border);
  border-radius: 8px;
  background: var(--oiwb-input-bg);
  color: var(--oiwb-text);
  font: inherit;
  font-size: 12.5px;
}
.oiwb-select {
  cursor: pointer;
}
.oiwb-input:focus,
.oiwb-select:focus,
.oiwb-btn:focus-visible {
  outline: 2px solid var(--dsw-alias-monitor-focus-ring, var(--oiwb-brand));
  outline-offset: 1px;
}
.oiwb-input::placeholder {
  color: var(--oiwb-text-3);
}
.oiwb-input:disabled {
  opacity: 0.6;
}

/* --- banners / placeholders ------------------------------------------------ */
.oiwb-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 9px 12px;
  border: 1px solid var(--oiwb-border);
  border-radius: 9px;
  background: var(--oiwb-bg);
  color: var(--oiwb-text-2);
  font-size: 12.5px;
}
.oiwb-banner.is-warn {
  border-left: 3px solid var(--oiwb-warning);
}
.oiwb-banner.is-error {
  border-left: 3px solid var(--oiwb-danger);
  color: var(--oiwb-text);
}
.oiwb-banner .oiwb-btn {
  margin-left: auto;
}
.oiwb-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 34px 20px;
  border: 1px dashed var(--oiwb-border-strong);
  border-radius: 12px;
  text-align: center;
  color: var(--oiwb-text-2);
}
.oiwb-placeholder h2 {
  font-size: 14px;
  font-weight: 650;
  color: var(--oiwb-text);
}
.oiwb-placeholder p {
  max-width: 60ch;
  font-size: 12.5px;
}
.oiwb-fatal {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  padding: 28px 24px;
}
.oiwb-fatal h2 {
  font-size: 15px;
  color: var(--oiwb-text);
}
.oiwb-fatal-msg {
  font-family: var(--oiwb-mono);
  font-size: 12px;
  color: var(--oiwb-danger);
  overflow-wrap: anywhere;
}

/* --- problems -------------------------------------------------------------- */
.oiwb-problems,
.oiwb-oj-list,
.oiwb-contests {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}
.oiwb-problem,
.oiwb-oj-card,
.oiwb-contest-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid var(--oiwb-border);
  border-radius: 10px;
  background: var(--oiwb-bg);
  min-width: 0;
}
.oiwb-problem-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  min-width: 0;
}
.oiwb-problem-name {
  font-family: var(--oiwb-mono);
  font-size: 12.5px;
  font-weight: 600;
  color: var(--oiwb-text);
  overflow-wrap: anywhere;
  min-width: 0;
}
.oiwb-problem-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-left: auto;
}
.oiwb-badges {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
}
.oiwb-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 20px;
  padding: 0 7px;
  border: 1px solid var(--oiwb-border);
  border-radius: 10px;
  color: var(--oiwb-text-2);
  font-size: 11px;
  white-space: nowrap;
}
.oiwb-badge::before {
  content: "";
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
}
.oiwb-badge.is-on {
  color: var(--oiwb-success);
  border-color: var(--oiwb-border);
}
.oiwb-badge.is-off {
  color: var(--oiwb-text-3);
  opacity: 0.75;
}
.oiwb-badge.is-count {
  color: var(--oiwb-text-2);
}
.oiwb-badge.is-count::before {
  display: none;
}
.oiwb-judge {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  flex-wrap: wrap;
  padding-top: 8px;
  border-top: 1px dashed var(--oiwb-border);
}
.oiwb-judge .oiwb-field {
  width: 210px;
}
.oiwb-judge .oiwb-btn {
  margin-bottom: 1px;
}

/* --- forms ----------------------------------------------------------------- */
.oiwb-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px 16px;
  border: 1px dashed var(--oiwb-border-strong);
  border-radius: 12px;
  background: var(--oiwb-bg);
  min-width: 0;
}
.oiwb-form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 10px 12px;
}
.oiwb-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}
.oiwb-field > span {
  font-size: 11.5px;
  color: var(--oiwb-text-2);
}
.oiwb-field > .oiwb-hint {
  color: var(--oiwb-text-3);
}
.oiwb-form-error {
  font-size: 12px;
  color: var(--oiwb-danger);
}
.oiwb-form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.oiwb-picker {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 190px;
  overflow: auto;
  padding: 6px 8px;
  border: 1px solid var(--oiwb-border);
  border-radius: 8px;
  background: var(--oiwb-input-bg);
}
.oiwb-pick {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 3px 4px;
  border-radius: 5px;
  font-family: var(--oiwb-mono);
  font-size: 12px;
  color: var(--oiwb-text);
  cursor: pointer;
}
.oiwb-pick:hover {
  background: var(--oiwb-bg-hover);
}
.oiwb-pick input {
  accent-color: var(--oiwb-brand);
}

/* --- OJ / contests --------------------------------------------------------- */
.oiwb-oj-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  min-width: 0;
}
.oiwb-oj-name {
  font-size: 13px;
  font-weight: 650;
  color: var(--oiwb-text);
}
.oiwb-kind {
  display: inline-flex;
  align-items: center;
  height: 20px;
  padding: 0 8px;
  border-radius: 6px;
  background: var(--dsw-alias-bg-layer, rgba(128, 128, 128, 0.14));
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.oiwb-kind.is-hydro {
  color: var(--oiwb-brand);
}
.oiwb-kind.is-hoj {
  color: var(--oiwb-warning);
}
.oiwb-tag {
  display: inline-flex;
  align-items: center;
  height: 20px;
  padding: 0 8px;
  border: 1px solid var(--oiwb-brand);
  border-radius: 10px;
  color: var(--oiwb-brand);
  font-size: 11px;
}
.oiwb-contest-title {
  font-size: 13px;
  font-weight: 650;
  color: var(--oiwb-text);
  overflow-wrap: anywhere;
}
.oiwb-contest-problems {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
}
.oiwb-oj-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

/* --- log drawer ------------------------------------------------------------ */
.oiwb-log {
  display: flex;
  flex-direction: column;
  flex: none;
  max-height: 42%;
  min-height: 0;
  border-top: 1px solid var(--oiwb-border);
  background: var(--oiwb-bg);
}
.oiwb-log-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: none;
  padding: 7px 14px;
  border-bottom: 1px solid var(--oiwb-border);
  font-size: 12px;
  min-width: 0;
}
.oiwb-log-title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: var(--oiwb-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}
.oiwb-log-tone {
  display: inline-flex;
  align-items: center;
  height: 18px;
  padding: 0 7px;
  border-radius: 9px;
  background: var(--dsw-alias-bg-layer, rgba(128, 128, 128, 0.14));
  color: var(--oiwb-text-2);
  font-size: 11px;
  flex: none;
}
.oiwb-log-tone.is-ok {
  color: var(--oiwb-success);
}
.oiwb-log-tone.is-error {
  color: var(--oiwb-danger);
}
.oiwb-log-tone.is-running {
  color: var(--oiwb-brand);
}
.oiwb-log-meta {
  font-family: var(--oiwb-mono);
  font-size: 11px;
  color: var(--oiwb-text-3);
  flex: none;
}
.oiwb-log-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  flex: none;
}
.oiwb-log-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 0;
  overflow: auto;
  padding: 8px 14px 12px;
}
.oiwb-log-msg {
  font-size: 12.5px;
  color: var(--oiwb-text);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.oiwb-log-argv {
  font-family: var(--oiwb-mono);
  font-size: 11px;
  color: var(--oiwb-text-3);
  overflow-wrap: anywhere;
}
.oiwb-log-label {
  font-size: 10.5px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--oiwb-text-3);
}
.oiwb-log-label.is-error {
  color: var(--oiwb-danger);
}
.oiwb-pre {
  margin: 0;
  padding: 8px 10px;
  max-height: 200px;
  overflow: auto;
  border: 1px solid var(--oiwb-border);
  border-radius: 8px;
  background: var(--dsw-alias-bg-layer, rgba(128, 128, 128, 0.12));
  color: var(--oiwb-text);
  font-family: var(--oiwb-mono);
  font-size: 11.5px;
  line-height: 1.5;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.oiwb-pre.is-error {
  color: var(--oiwb-danger);
}
.oiwb-running {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--oiwb-text-2);
}
.oiwb-spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  flex: none;
  border: 2px solid var(--oiwb-border);
  border-top-color: var(--oiwb-brand);
  border-radius: 50%;
  animation: oiwb-spin 0.8s linear infinite;
}
@keyframes oiwb-spin {
  to { transform: rotate(360deg); }
}

/* --- lists ----------------------------------------------------------------- */
.oiwb-list {
  margin: 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 12.5px;
  color: var(--oiwb-text-2);
}
.oiwb-steps {
  margin: 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12.5px;
  color: var(--oiwb-text-2);
}
.oiwb-steps strong {
  color: var(--oiwb-text);
}

/* --- narrow panel ---------------------------------------------------------- */
@container (max-width: 620px) {
  .oiwb-head {
    flex-wrap: wrap;
    padding: 12px 14px 8px;
  }
  .oiwb-body {
    padding: 12px 14px 18px;
  }
  .oiwb-problem-actions {
    margin-left: 0;
    width: 100%;
  }
  .oiwb-judge {
    flex-direction: column;
    align-items: stretch;
  }
  .oiwb-judge .oiwb-field {
    width: auto;
  }
  .oiwb-kv {
    grid-template-columns: 1fr;
    gap: 2px 0;
  }
  .oiwb-kv dt {
    margin-top: 4px;
  }
  .oiwb-log {
    max-height: 50%;
  }
}
`;
		//#endregion
		//#region src/client/index.tsx
		/** Row order among the shell's global panel rows (Plugins is 0, Schedule 10). */
		const PANEL_ORDER = 30;
		/** Services that must be up before this plugin's `apply` runs. */
		const inject = ["slots"];
		/**
		* Register the panel's sidebar row and center-column page.
		* @param ctx - client root context (services: slots).
		* @returns disposer releasing both registrations.
		*/
		function registerWorkbenchPanel(ctx) {
			const slots = ctx.slots;
			const disposers = [];
			/** Install one seat contribution; a failed seat never blocks the other. */
			const seat = (label, install) => {
				try {
					disposers.push(install());
				} catch (error) {
					console.error(`[oi-workbench] 注册槽位失败：${label}`, error);
				}
			};
			seat("sidebar.panellist", () => slots.inject("sidebar.panellist", () => slots.register({
				name: "sidebar.panellist",
				id: WORKBENCH_PANEL_ID,
				order: PANEL_ORDER,
				label: () => "OI 工作台"
			}, WorkbenchIcon)));
			seat("main", () => slots.inject("main", () => slots.register({
				name: "main",
				key: WORKBENCH_PANEL_ID
			}, WorkbenchPanel)));
			return () => {
				for (const dispose of disposers.splice(0)) try {
					dispose();
				} catch (error) {
					console.error("[oi-workbench] 释放槽位失败", error);
				}
			};
		}
		/**
		* Client plugin body.
		* @param ctx - client root context (services: slots).
		*/
		function apply(ctx) {
			try {
				ctx.effect(() => registerWorkbenchPanel(ctx), "oi-workbench: sidebar row + main panel");
			} catch (error) {
				console.error("[oi-workbench] 客户端面板注册失败，已跳过", error);
			}
		}
		//#endregion
		exports.WORKBENCH_PANEL_ID = WORKBENCH_PANEL_ID;
		exports.apply = apply;
		exports.inject = inject;
		return module.exports;
	}
});

//# sourceMappingURL=client.js.map