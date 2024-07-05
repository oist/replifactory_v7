(function(global, factory) {
  typeof exports === "object" && typeof module !== "undefined" ? module.exports = factory(require("vue")) : typeof define === "function" && define.amd ? define(["vue"], factory) : (global = typeof globalThis !== "undefined" ? globalThis : global || self, global["endless-growth-experiment-parameters"] = factory(global.Vue));
})(this, function(vue) {
  "use strict";
  const _hoisted_1 = /* @__PURE__ */ vue.createStaticVNode('<h3>Global Parameters</h3><form><div class="row mb-3"><label for="inputCycleTime" class="col-sm-2 col-form-label">Cycle time</label><div class="col-auto"><div class="input-group mb-3"><input id="inputCycleTime" type="number" class="form-control" aria-label="Cycle time" aria-describedby="inputCycleTimeUnit" value="240"><span id="inputCycleTimeUnit" class="input-group-text">seconds</span></div></div></div></form><h3>Reactors parameters</h3>', 3);
  const _hoisted_4 = { class: "row mb-2 g-2" };
  const _hoisted_5 = /* @__PURE__ */ vue.createElementVNode("div", { class: "col-sm-4 col-form-label" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Enabled")
  ], -1);
  const _hoisted_6 = ["id"];
  const _hoisted_7 = ["for"];
  const _hoisted_8 = { class: "row mb-2 g-2" };
  const _hoisted_9 = /* @__PURE__ */ vue.createElementVNode("div", { class: "col-sm-4 col-form-label" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Dilution Threshold"),
    /* @__PURE__ */ vue.createElementVNode("div", {
      id: "passwordHelpBlock",
      class: "form-text"
    }, " An optical density value which triggers the dilution process in the reactor. ")
  ], -1);
  const _hoisted_10 = { class: "form-floating" };
  const _hoisted_11 = ["id", "aria-label"];
  const _hoisted_12 = ["for"];
  const _hoisted_13 = { class: "row mb-2 g-2" };
  const _hoisted_14 = /* @__PURE__ */ vue.createElementVNode("div", { class: "col-sm-4 col-form-label" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Dilution Target OD")
  ], -1);
  const _hoisted_15 = { class: "form-floating" };
  const _hoisted_16 = ["id", "aria-label"];
  const _hoisted_17 = ["for"];
  const _hoisted_18 = { class: "row mb-2 g-2" };
  const _hoisted_19 = /* @__PURE__ */ vue.createElementVNode("div", { class: "col-sm-4 col-form-label" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Dilution Volume (mL)")
  ], -1);
  const _hoisted_20 = { class: "form-floating" };
  const _hoisted_21 = ["id", "aria-label"];
  const _hoisted_22 = ["for"];
  const _sfc_main = {
    __name: "ExperimentParameters",
    setup(__props) {
      return (_ctx, _cache) => {
        return vue.openBlock(), vue.createElementBlock("section", null, [
          _hoisted_1,
          vue.createElementVNode("form", null, [
            vue.createElementVNode("div", _hoisted_4, [
              _hoisted_5,
              (vue.openBlock(), vue.createElementBlock(vue.Fragment, null, vue.renderList(8, (n) => {
                return vue.createElementVNode("div", {
                  key: n,
                  class: "col-12 col-sm-1"
                }, [
                  vue.createElementVNode("div", null, [
                    vue.createElementVNode("input", {
                      id: `inputEnabled-${n}`,
                      class: "form-check-input",
                      type: "checkbox",
                      checked: ""
                    }, null, 8, _hoisted_6),
                    vue.createElementVNode("label", {
                      class: "form-check-label mx-1",
                      for: `inputEnabled-${n}`
                    }, "Reactor " + vue.toDisplayString(n), 9, _hoisted_7)
                  ])
                ]);
              }), 64))
            ]),
            vue.createElementVNode("div", _hoisted_8, [
              _hoisted_9,
              (vue.openBlock(), vue.createElementBlock(vue.Fragment, null, vue.renderList(8, (n) => {
                return vue.createElementVNode("div", {
                  key: n,
                  class: "col-12 col-sm-1"
                }, [
                  vue.createElementVNode("div", _hoisted_10, [
                    vue.createElementVNode("input", {
                      id: `inputOdDilutionThreshold-${n}`,
                      type: "number",
                      class: "form-control",
                      "aria-label": `OD Dilution Threshold for Reactor ${n}`,
                      value: 0.8
                    }, null, 8, _hoisted_11),
                    vue.createElementVNode("label", {
                      for: `inputOdDilutionThreshold-${n}`
                    }, "Reactor " + vue.toDisplayString(n), 9, _hoisted_12)
                  ])
                ]);
              }), 64))
            ]),
            vue.createElementVNode("div", _hoisted_13, [
              _hoisted_14,
              (vue.openBlock(), vue.createElementBlock(vue.Fragment, null, vue.renderList(8, (n) => {
                return vue.createElementVNode("div", {
                  key: n,
                  class: "col-12 col-sm-1"
                }, [
                  vue.createElementVNode("div", _hoisted_15, [
                    vue.createElementVNode("input", {
                      id: `inputDilutionTargetOD-${n}`,
                      type: "number",
                      class: "form-control",
                      "aria-label": `Dilution Target OD for Reactor ${n}`,
                      value: 0.3
                    }, null, 8, _hoisted_16),
                    vue.createElementVNode("label", {
                      for: `inputDilutionTargetOD-${n}`
                    }, "Reactor " + vue.toDisplayString(n), 9, _hoisted_17)
                  ])
                ]);
              }), 64))
            ]),
            vue.createElementVNode("div", _hoisted_18, [
              _hoisted_19,
              (vue.openBlock(), vue.createElementBlock(vue.Fragment, null, vue.renderList(8, (n) => {
                return vue.createElementVNode("div", {
                  key: n,
                  class: "col-12 col-sm-1"
                }, [
                  vue.createElementVNode("div", _hoisted_20, [
                    vue.createElementVNode("input", {
                      id: `inputDilutionVolume-${n}`,
                      type: "number",
                      class: "form-control",
                      "aria-label": `Dilution Volume for Reactor ${n}`,
                      value: 1
                    }, null, 8, _hoisted_21),
                    vue.createElementVNode("label", {
                      for: `inputDilutionVolume-${n}`
                    }, "Reactor " + vue.toDisplayString(n), 9, _hoisted_22)
                  ])
                ]);
              }), 64))
            ])
          ])
        ]);
      };
    }
  };
  return _sfc_main;
});
