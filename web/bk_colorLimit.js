import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";
import { getBestTextColor } from "./utils.js";

// Displays input text on a node

app.registerExtension({
	name: "bk.BK_ColorLimit",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "BK_ColorLimit") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				if (this.widgets) {
					const pos = this.widgets.findIndex((w) => w.name === "result");
					if (pos !== -1) {
						for (let i = pos; i < this.widgets.length; i++) {
							this.widgets[i].onRemove?.();
						}
						this.widgets.length = pos;
					}
				}

				const w = ComfyWidgets["STRING"](this, "result", ["STRING", { multiline: true }], app).widget;
				w.inputEl.readOnly = true;
				w.inputEl.rows = 1;
				w.inputEl.style.background = message.text;
				w.inputEl.style.color = getBestTextColor(message.text)
				w.inputEl.style.textShadow = "0 1px 2px black";
				w.inputEl.style.textAlign = "center";
				w.value = message.text;

				this.onResize?.(this.size);
			};
		}
	},
});
