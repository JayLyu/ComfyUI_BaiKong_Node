import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

/**
 * 把输出结果展示在 Node 下方
 * @param {*} nodeName
 */

function registerColorNode(nodeName) {
  app.registerExtension({
    name: `baikong.${nodeName}`,
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
      if (nodeData.name === nodeName) {
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

          const w = ComfyWidgets["STRING"](
            this,
            "result",
            ["STRING", { multiline: true }],
            app
          ).widget;
          w.inputEl.readOnly = true;
          w.inputEl.rows = 1;
          // console.log(message.text[0])
          // Message Format: "text": [{"bg_color","front_color"}]
          const show_text =
            message.text[0].front_color
              ? `BACKGROUND(${message.text[0].bg_color})\nTEXT(${message.text[0].front_color})`
              : `${message.text[0].bg_color}`;
          w.inputEl.style.background = message.text[0].bg_color;
          w.inputEl.style.color = message.text[0].front_color;
          w.inputEl.style.textAlign = "center";
          w.value = show_text;

          this.onResize?.(this.size);
        };
      }
    },
  });
}

// 注册节点
registerColorNode("BK_ColorLimit");
registerColorNode("BK_ColorSelector");
registerColorNode("BK_ColorContrast");
registerColorNode("BK_ColorLuminance");
registerColorNode("BK_ImageLayout")