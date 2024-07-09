(function(global, factory) {
  typeof exports === "object" && typeof module !== "undefined" ? module.exports = factory(require("vue")) : typeof define === "function" && define.amd ? define(["vue"], factory) : (global = typeof globalThis !== "undefined" ? globalThis : global || self, global["endless-growth-experiment-parameters"] = factory(global.Vue));
})(this, function(vue) {
  "use strict";
  const _hoisted_1 = /* @__PURE__ */ vue.createElementVNode("h3", null, "Global Parameters", -1);
  const _hoisted_2 = { class: "row mb-3" };
  const _hoisted_3 = /* @__PURE__ */ vue.createElementVNode("label", {
    for: "inputCycleTime",
    class: "col-sm-2 col-form-label"
  }, "Cycle time", -1);
  const _hoisted_4 = { class: "col-auto" };
  const _hoisted_5 = { class: "input-group mb-3" };
  const _hoisted_6 = /* @__PURE__ */ vue.createElementVNode("span", {
    id: "inputCycleTimeUnit",
    class: "input-group-text"
  }, "seconds", -1);
  const _hoisted_7 = /* @__PURE__ */ vue.createElementVNode("h3", null, "Reactors parameters", -1);
  const _hoisted_8 = { class: "row mb-2 g-2" };
  const _hoisted_9 = /* @__PURE__ */ vue.createElementVNode("div", { class: "col-sm-4 col-form-label" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Enabled")
  ], -1);
  const _hoisted_10 = ["id", "onUpdate:modelValue"];
  const _hoisted_11 = ["for"];
  const _hoisted_12 = { class: "row mb-2 g-2" };
  const _hoisted_13 = /* @__PURE__ */ vue.createElementVNode("div", { class: "col-sm-4 col-form-label" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Dilution Threshold"),
    /* @__PURE__ */ vue.createElementVNode("div", {
      id: "passwordHelpBlock",
      class: "form-text"
    }, " An optical density value which triggers the dilution process in the reactor. ")
  ], -1);
  const _hoisted_14 = { class: "form-floating" };
  const _hoisted_15 = ["id", "onUpdate:modelValue", "aria-label", "disabled"];
  const _hoisted_16 = ["for"];
  const _hoisted_17 = { class: "row mb-2 g-2" };
  const _hoisted_18 = /* @__PURE__ */ vue.createElementVNode("div", { class: "col-sm-4 col-form-label" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Dilution Target OD")
  ], -1);
  const _hoisted_19 = { class: "form-floating" };
  const _hoisted_20 = ["id", "onUpdate:modelValue", "aria-label", "disabled"];
  const _hoisted_21 = ["for"];
  const _hoisted_22 = { class: "row mb-2 g-2" };
  const _hoisted_23 = /* @__PURE__ */ vue.createElementVNode("div", { class: "col-sm-4 col-form-label" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Dilution Volume (mL)")
  ], -1);
  const _hoisted_24 = { class: "form-floating" };
  const _hoisted_25 = ["id", "onUpdate:modelValue", "aria-label", "disabled"];
  const _hoisted_26 = ["for"];
  const _sfc_main = {
    __name: "ExperimentParameters",
    emits: ["updateParameters"],
    setup(__props, { emit: __emit }) {
      const emit = __emit;
      const cycleTime = vue.ref(60 * 4);
      const reactors = vue.ref(
        Array(8).fill(null).map((_, index) => ({
          index: index + 1,
          enabled: false,
          volume: 1,
          threshold: 0.8,
          targetOD: 0.3
        }))
      );
      const emitUpdate = () => {
        const enabledReactors = reactors.value.filter((reactor) => reactor.enabled).map(({ enabled, ...rest }) => rest);
        emit("updateParameters", {
          cycleTime: cycleTime.value,
          reactors: enabledReactors
        });
      };
      vue.onBeforeMount(() => {
        emitUpdate();
      });
      return (_ctx, _cache) => {
        return vue.openBlock(), vue.createElementBlock("section", null, [
          _hoisted_1,
          vue.createElementVNode("form", null, [
            vue.createElementVNode("div", _hoisted_2, [
              _hoisted_3,
              vue.createElementVNode("div", _hoisted_4, [
                vue.createElementVNode("div", _hoisted_5, [
                  vue.withDirectives(vue.createElementVNode("input", {
                    id: "inputCycleTime",
                    "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => cycleTime.value = $event),
                    type: "number",
                    class: "form-control",
                    "aria-label": "Cycle time",
                    "aria-describedby": "inputCycleTimeUnit",
                    onChange: emitUpdate
                  }, null, 544), [
                    [
                      vue.vModelText,
                      cycleTime.value,
                      void 0,
                      { number: true }
                    ]
                  ]),
                  _hoisted_6
                ])
              ])
            ])
          ]),
          _hoisted_7,
          vue.createElementVNode("form", null, [
            vue.createElementVNode("div", _hoisted_8, [
              _hoisted_9,
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(reactors.value, (reactor) => {
                return vue.openBlock(), vue.createElementBlock("div", {
                  key: reactor.index,
                  class: "col-12 col-sm-1"
                }, [
                  vue.createElementVNode("div", null, [
                    vue.withDirectives(vue.createElementVNode("input", {
                      id: `inputEnabled-${reactor.index}`,
                      "onUpdate:modelValue": ($event) => reactor.enabled = $event,
                      class: "form-check-input",
                      type: "checkbox",
                      onChange: emitUpdate
                    }, null, 40, _hoisted_10), [
                      [vue.vModelCheckbox, reactor.enabled]
                    ]),
                    vue.createElementVNode("label", {
                      class: "form-check-label mx-1",
                      for: `inputEnabled-${reactor.index}`
                    }, "Reactor " + vue.toDisplayString(reactor.index), 9, _hoisted_11)
                  ])
                ]);
              }), 128))
            ]),
            vue.createElementVNode("div", _hoisted_12, [
              _hoisted_13,
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(reactors.value, (reactor) => {
                return vue.openBlock(), vue.createElementBlock("div", {
                  key: reactor.index,
                  class: "col-12 col-sm-1"
                }, [
                  vue.createElementVNode("div", _hoisted_14, [
                    vue.withDirectives(vue.createElementVNode("input", {
                      id: `inputOdDilutionThreshold-${reactor.index}`,
                      "onUpdate:modelValue": ($event) => reactor.threshold = $event,
                      type: "number",
                      class: "form-control",
                      "aria-label": `OD Dilution Threshold for Reactor ${reactor.index}`,
                      disabled: !reactor.enabled,
                      onChange: emitUpdate
                    }, null, 40, _hoisted_15), [
                      [
                        vue.vModelText,
                        reactor.threshold,
                        void 0,
                        { number: true }
                      ]
                    ]),
                    vue.createElementVNode("label", {
                      for: `inputOdDilutionThreshold-${reactor.index}`
                    }, "Reactor " + vue.toDisplayString(reactor.index), 9, _hoisted_16)
                  ])
                ]);
              }), 128))
            ]),
            vue.createElementVNode("div", _hoisted_17, [
              _hoisted_18,
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(reactors.value, (reactor) => {
                return vue.openBlock(), vue.createElementBlock("div", {
                  key: reactor.index,
                  class: "col-12 col-sm-1"
                }, [
                  vue.createElementVNode("div", _hoisted_19, [
                    vue.withDirectives(vue.createElementVNode("input", {
                      id: `inputDilutionTargetOD-${reactor.index}`,
                      "onUpdate:modelValue": ($event) => reactor.targetOD = $event,
                      type: "number",
                      class: "form-control",
                      "aria-label": `Dilution Target OD for Reactor ${reactor.index}`,
                      disabled: !reactor.enabled,
                      onChange: emitUpdate
                    }, null, 40, _hoisted_20), [
                      [
                        vue.vModelText,
                        reactor.targetOD,
                        void 0,
                        { number: true }
                      ]
                    ]),
                    vue.createElementVNode("label", {
                      for: `inputDilutionTargetOD-${reactor.index}`
                    }, "Reactor " + vue.toDisplayString(reactor.index), 9, _hoisted_21)
                  ])
                ]);
              }), 128))
            ]),
            vue.createElementVNode("div", _hoisted_22, [
              _hoisted_23,
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(reactors.value, (reactor) => {
                return vue.openBlock(), vue.createElementBlock("div", {
                  key: reactor.index,
                  class: "col-12 col-sm-1"
                }, [
                  vue.createElementVNode("div", _hoisted_24, [
                    vue.withDirectives(vue.createElementVNode("input", {
                      id: `inputDilutionVolume-${reactor.index}`,
                      "onUpdate:modelValue": ($event) => reactor.volume = $event,
                      type: "number",
                      class: "form-control",
                      "aria-label": `Dilution Volume for Reactor ${reactor.index}`,
                      disabled: !reactor.enabled,
                      onChange: emitUpdate
                    }, null, 40, _hoisted_25), [
                      [
                        vue.vModelText,
                        reactor.volume,
                        void 0,
                        { number: true }
                      ]
                    ]),
                    vue.createElementVNode("label", {
                      for: `inputDilutionVolume-${reactor.index}`
                    }, "Reactor " + vue.toDisplayString(reactor.index), 9, _hoisted_26)
                  ])
                ]);
              }), 128))
            ])
          ])
        ]);
      };
    }
  };
  return _sfc_main;
});
