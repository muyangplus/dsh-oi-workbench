window.__ModuleLoader__.load({
	id: "@muyangplus/dsh-oi-workbench",
	factory: (require) => {
		var module = { exports: {} };
		var exports = module.exports;
		Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
		//#region src/client/index.ts
		const inject = ["slots"];
		const API = "/oi-workbench/api";
		function el(tag, cls, text) {
			const e = document.createElement(tag);
			if (cls) e.className = cls;
			if (text !== void 0) e.textContent = text;
			return e;
		}
		const styles = `
.oiwb-action{display:flex;align-items:center;gap:6px;padding:6px 8px;border-radius:8px;cursor:pointer;color:var(--theme-text,#ccc);font-size:12px;white-space:nowrap}
.oiwb-action:hover{background:rgba(74,158,255,.1);color:var(--theme-text,#fff)}
.oiwb-modal{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:9999;display:flex;align-items:center;justify-content:center}
.oiwb-card{width:min(720px,92vw);max-height:86vh;background:var(--theme-bg,#1e1e1e);border:1px solid var(--theme-border,#333);border-radius:12px;display:flex;flex-direction:column;overflow:hidden}
.oiwb-head{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid var(--theme-border,#333)}
.oiwb-body{padding:14px;overflow:auto}
.oiwb-page{font-family:ui-monospace,monospace;font-size:12px;line-height:1.6}
.oiwb-list{list-style:none;margin:0;padding:0}
.oiwb-item{display:flex;align-items:center;gap:8px;padding:8px 10px;border:1px solid var(--theme-border,#333);border-radius:8px;margin-bottom:6px}
.oiwb-item .name{flex:1;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.oiwb-item .badge{font-size:10px;padding:2px 6px;border-radius:10px;background:rgba(74,158,255,.12);color:#4a9eff}
.oiwb-btn{background:var(--theme-accent,#4a9eff);color:#fff;border:none;border-radius:6px;padding:4px 10px;cursor:pointer;font-size:12px;white-space:nowrap}
.oiwb-btn.ghost{background:transparent;border:1px solid var(--theme-border,#444);color:var(--theme-text,#ccc)}
.oiwb-close{background:transparent;border:1px solid var(--theme-border,#444);color:var(--theme-text,#ccc);border-radius:6px;padding:4px 10px;cursor:pointer;font-size:12px}
.oiwb-msg{margin-top:10px;padding:8px 10px;border-radius:6px;background:var(--theme-input-bg,#111);border:1px solid var(--theme-border,#333);white-space:pre-wrap;max-height:240px;overflow:auto;font-size:11px}
`;
		function fetchJson(path, init) {
			return fetch(API + path, {
				headers: { "content-type": "application/json" },
				...init
			}).then((r) => r.json());
		}
		function buildPanel() {
			const page = el("div", "oiwb-page");
			const h = el("h3", void 0, "OI 出题工作台");
			const rootInfo = el("p", void 0, "Root: -");
			page.append(h, rootInfo);
			const list = el("ul", "oiwb-list");
			page.append(list);
			const msg = el("div", "oiwb-msg");
			msg.style.display = "none";
			page.append(msg);
			const say = (text) => {
				msg.textContent = text;
				msg.style.display = text ? "block" : "none";
			};
			const refresh = () => {
				fetchJson("/problems").then((d) => {
					rootInfo.textContent = "Root: " + d.root;
					list.textContent = "";
					if (!d.problems?.length) {
						list.append(el("li", "oiwb-item", "（未发现题目包）"));
						return;
					}
					for (const p of d.problems) {
						const li = el("li", "oiwb-item");
						const name = el("span", "name", p.name);
						const badge = el("span", "badge", (p.hasProblemMd ? "题面✓" : "题面✗") + " " + (p.hasSolution ? "题解✓" : "题解✗"));
						const btnCheck = el("button", "oiwb-btn ghost", "检查");
						btnCheck.addEventListener("click", () => {
							say("检查中… " + p.path);
							fetchJson("/problems/check", {
								method: "POST",
								body: JSON.stringify({ dir: p.path })
							}).then((r) => say(JSON.stringify(r, null, 2))).catch((e) => say("请求失败: " + e));
						});
						const btnBuild = el("button", "oiwb-btn", "构建");
						btnBuild.addEventListener("click", () => {
							say("构建中… " + p.path);
							fetchJson("/problems/build", {
								method: "POST",
								body: JSON.stringify({ dir: p.path })
							}).then((r) => say(JSON.stringify(r, null, 2))).catch((e) => say("请求失败: " + e));
						});
						li.append(name, badge, btnCheck, btnBuild);
						list.append(li);
					}
				}).catch((e) => say("加载失败: " + e));
			};
			refresh();
			const timer = window.setInterval(refresh, 6e4);
			page.dataset.timer = String(timer);
			return page;
		}
		function openModal() {
			const modal = el("div", "oiwb-modal");
			const card = el("div", "oiwb-card");
			const head = el("div", "oiwb-head");
			const title = el("span", void 0, "OI 工作台");
			const close = el("button", "oiwb-close", "关闭");
			close.addEventListener("click", () => modal.remove());
			head.append(title, close);
			const body = el("div", "oiwb-body");
			body.append(buildPanel());
			card.append(head, body);
			modal.append(card);
			modal.addEventListener("click", (e) => {
				if (e.target === modal) modal.remove();
			});
			document.body.append(modal);
		}
		function apply(ctx) {
			ctx.effect(() => ctx.slots.inject("sidebar.footer.action", () => ctx.slots.register({
				name: "sidebar.footer.action",
				id: "oi-workbench-panel",
				order: -100,
				label: () => "OI 工作台",
				component: () => ({ render(props) {
					const style = document.createElement("style");
					style.textContent = styles;
					const action = el("div", "oiwb-action");
					action.textContent = props.wide ? "OI 工作台" : "OI";
					action.addEventListener("click", openModal);
					const frag = document.createDocumentFragment();
					frag.append(style, action);
					return frag;
				} })
			})), "dsh-oi-workbench: sidebar action");
		}
		//#endregion
		exports.apply = apply;
		exports.inject = inject;
		return module.exports;
	}
});

//# sourceMappingURL=client.js.map