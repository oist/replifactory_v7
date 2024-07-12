(function(global, factory) {
  typeof exports === "object" && typeof module !== "undefined" ? module.exports = factory(require("vue")) : typeof define === "function" && define.amd ? define(["vue"], factory) : (global = typeof globalThis !== "undefined" ? globalThis : global || self, global["endless-growth-experiment-parameters"] = factory(global.Vue));
})(this, function(vue) {
  "use strict";
  const _export_sfc = (sfc, props) => {
    const target = sfc.__vccOpts || sfc;
    for (const [key, val] of props) {
      target[key] = val;
    }
    return target;
  };
  const _withScopeId = (n) => (vue.pushScopeId("data-v-f5b98fc1"), n = n(), vue.popScopeId(), n);
  const _hoisted_1 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("h3", null, "Global Parameters", -1));
  const _hoisted_2 = { class: "row mb-3" };
  const _hoisted_3 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("label", {
    for: "inputCycleTime",
    class: "col-md-2 col-form-label"
  }, "Cycle time", -1));
  const _hoisted_4 = { class: "col-auto" };
  const _hoisted_5 = { class: "input-group mb-3" };
  const _hoisted_6 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("span", {
    id: "inputCycleTimeUnit",
    class: "input-group-text"
  }, "seconds", -1));
  const _hoisted_7 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("h3", null, "Reactors parameters", -1));
  const _hoisted_8 = { class: "row mb-2 g-2" };
  const _hoisted_9 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("div", { class: "col-md-12 col-xl-3 col-form-label pb-0" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Enabled")
  ], -1));
  const _hoisted_10 = { class: "col-12 col-md-12 col-xl-9 row g-2 mt-0" };
  const _hoisted_11 = ["id", "onUpdate:modelValue"];
  const _hoisted_12 = ["for"];
  const _hoisted_13 = { class: "row mb-2 g-2" };
  const _hoisted_14 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("div", { class: "col-md-12 col-xl-3 col-form-label pb-0" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Dilution Threshold"),
    /* @__PURE__ */ vue.createElementVNode("div", {
      id: "passwordHelpBlock",
      class: "form-text mt-0"
    }, " An optical density value which triggers the dilution process in the reactor. ")
  ], -1));
  const _hoisted_15 = { class: "col-12 col-md-12 col-xl-9 row g-2 mt-0" };
  const _hoisted_16 = { class: "form-floating" };
  const _hoisted_17 = ["id", "onUpdate:modelValue", "aria-label", "disabled"];
  const _hoisted_18 = ["for"];
  const _hoisted_19 = { class: "row mb-2 g-2" };
  const _hoisted_20 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("div", { class: "col-md-12 col-xl-3 col-form-label pb-0" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Dilution Target OD")
  ], -1));
  const _hoisted_21 = { class: "col-12 col-md-12 col-xl-9 row g-2 mt-0" };
  const _hoisted_22 = { class: "form-floating" };
  const _hoisted_23 = ["id", "onUpdate:modelValue", "aria-label", "disabled"];
  const _hoisted_24 = ["for"];
  const _hoisted_25 = { class: "row mb-2 g-2" };
  const _hoisted_26 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("div", { class: "col-md-12 col-xl-3 col-form-label pb-0" }, [
    /* @__PURE__ */ vue.createElementVNode("strong", null, "Dilution Volume (mL)")
  ], -1));
  const _hoisted_27 = { class: "col-12 col-md-12 col-xl-9 row g-2 mt-0" };
  const _hoisted_28 = { class: "form-floating" };
  const _hoisted_29 = ["id", "onUpdate:modelValue", "aria-label", "disabled"];
  const _hoisted_30 = ["for"];
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
              vue.createElementVNode("div", _hoisted_10, [
                (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(reactors.value, (reactor) => {
                  return vue.openBlock(), vue.createElementBlock("div", {
                    key: reactor.index,
                    class: "col reactor-col"
                  }, [
                    vue.createElementVNode("div", null, [
                      vue.withDirectives(vue.createElementVNode("input", {
                        id: `inputEnabled-${reactor.index}`,
                        "onUpdate:modelValue": ($event) => reactor.enabled = $event,
                        class: "form-check-input",
                        type: "checkbox",
                        onChange: emitUpdate
                      }, null, 40, _hoisted_11), [
                        [vue.vModelCheckbox, reactor.enabled]
                      ]),
                      vue.createElementVNode("label", {
                        class: "form-check-label mx-1",
                        for: `inputEnabled-${reactor.index}`
                      }, "Reactor " + vue.toDisplayString(reactor.index), 9, _hoisted_12)
                    ])
                  ]);
                }), 128))
              ])
            ]),
            vue.createElementVNode("div", _hoisted_13, [
              _hoisted_14,
              vue.createElementVNode("div", _hoisted_15, [
                (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(reactors.value, (reactor) => {
                  return vue.openBlock(), vue.createElementBlock("div", {
                    key: reactor.index,
                    class: "col reactor-col"
                  }, [
                    vue.createElementVNode("div", _hoisted_16, [
                      vue.withDirectives(vue.createElementVNode("input", {
                        id: `inputOdDilutionThreshold-${reactor.index}`,
                        "onUpdate:modelValue": ($event) => reactor.threshold = $event,
                        type: "number",
                        class: "form-control",
                        "aria-label": `OD Dilution Threshold for Reactor ${reactor.index}`,
                        disabled: !reactor.enabled,
                        onChange: emitUpdate
                      }, null, 40, _hoisted_17), [
                        [
                          vue.vModelText,
                          reactor.threshold,
                          void 0,
                          { number: true }
                        ]
                      ]),
                      vue.createElementVNode("label", {
                        for: `inputOdDilutionThreshold-${reactor.index}`
                      }, "Reactor " + vue.toDisplayString(reactor.index), 9, _hoisted_18)
                    ])
                  ]);
                }), 128))
              ])
            ]),
            vue.createElementVNode("div", _hoisted_19, [
              _hoisted_20,
              vue.createElementVNode("div", _hoisted_21, [
                (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(reactors.value, (reactor) => {
                  return vue.openBlock(), vue.createElementBlock("div", {
                    key: reactor.index,
                    class: "col reactor-col"
                  }, [
                    vue.createElementVNode("div", _hoisted_22, [
                      vue.withDirectives(vue.createElementVNode("input", {
                        id: `inputDilutionTargetOD-${reactor.index}`,
                        "onUpdate:modelValue": ($event) => reactor.targetOD = $event,
                        type: "number",
                        class: "form-control",
                        "aria-label": `Dilution Target OD for Reactor ${reactor.index}`,
                        disabled: !reactor.enabled,
                        onChange: emitUpdate
                      }, null, 40, _hoisted_23), [
                        [
                          vue.vModelText,
                          reactor.targetOD,
                          void 0,
                          { number: true }
                        ]
                      ]),
                      vue.createElementVNode("label", {
                        for: `inputDilutionTargetOD-${reactor.index}`
                      }, "Reactor " + vue.toDisplayString(reactor.index), 9, _hoisted_24)
                    ])
                  ]);
                }), 128))
              ])
            ]),
            vue.createElementVNode("div", _hoisted_25, [
              _hoisted_26,
              vue.createElementVNode("div", _hoisted_27, [
                (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(reactors.value, (reactor) => {
                  return vue.openBlock(), vue.createElementBlock("div", {
                    key: reactor.index,
                    class: "col reactor-col"
                  }, [
                    vue.createElementVNode("div", _hoisted_28, [
                      vue.withDirectives(vue.createElementVNode("input", {
                        id: `inputDilutionVolume-${reactor.index}`,
                        "onUpdate:modelValue": ($event) => reactor.volume = $event,
                        type: "number",
                        class: "form-control",
                        "aria-label": `Dilution Volume for Reactor ${reactor.index}`,
                        disabled: !reactor.enabled,
                        onChange: emitUpdate
                      }, null, 40, _hoisted_29), [
                        [
                          vue.vModelText,
                          reactor.volume,
                          void 0,
                          { number: true }
                        ]
                      ]),
                      vue.createElementVNode("label", {
                        for: `inputDilutionVolume-${reactor.index}`
                      }, "Reactor " + vue.toDisplayString(reactor.index), 9, _hoisted_30)
                    ])
                  ]);
                }), 128))
              ])
            ])
          ])
        ]);
      };
    }
  };
  const ExperimentParameters = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-f5b98fc1"]]);
  return ExperimentParameters;
});
