import { openBlock as e, createElementBlock as t, createElementVNode as l, Fragment as s, renderList as i, toDisplayString as c, createStaticVNode as r } from "vue";
const a = /* @__PURE__ */ r('<h3>Global Parameters</h3><form><div class="row mb-3"><label for="inputCycleTime" class="col-sm-2 col-form-label">Cycle time</label><div class="col-auto"><div class="input-group mb-3"><input id="inputCycleTime" type="number" class="form-control" aria-label="Cycle time" aria-describedby="inputCycleTimeUnit" value="240"><span id="inputCycleTimeUnit" class="input-group-text">seconds</span></div></div></div></form><h3>Reactors parameters</h3>', 3), n = { class: "row mb-2 g-2" }, d = /* @__PURE__ */ l("div", { class: "col-sm-4 col-form-label" }, [
  /* @__PURE__ */ l("strong", null, "Enabled")
], -1), u = ["id"], m = ["for"], _ = { class: "row mb-2 g-2" }, p = /* @__PURE__ */ l("div", { class: "col-sm-4 col-form-label" }, [
  /* @__PURE__ */ l("strong", null, "Dilution Threshold"),
  /* @__PURE__ */ l("div", {
    id: "passwordHelpBlock",
    class: "form-text"
  }, " An optical density value which triggers the dilution process in the reactor. ")
], -1), h = { class: "form-floating" }, b = ["id", "aria-label"], f = ["for"], v = { class: "row mb-2 g-2" }, g = /* @__PURE__ */ l("div", { class: "col-sm-4 col-form-label" }, [
  /* @__PURE__ */ l("strong", null, "Dilution Target OD")
], -1), y = { class: "form-floating" }, D = ["id", "aria-label"], T = ["for"], k = { class: "row mb-2 g-2" }, $ = /* @__PURE__ */ l("div", { class: "col-sm-4 col-form-label" }, [
  /* @__PURE__ */ l("strong", null, "Dilution Volume (mL)")
], -1), R = { class: "form-floating" }, w = ["id", "aria-label"], x = ["for"], B = {
  __name: "ExperimentParameters",
  setup(O) {
    return (C, E) => (e(), t("section", null, [
      a,
      l("form", null, [
        l("div", n, [
          d,
          (e(), t(s, null, i(8, (o) => l("div", {
            key: o,
            class: "col-12 col-sm-1"
          }, [
            l("div", null, [
              l("input", {
                id: `inputEnabled-${o}`,
                class: "form-check-input",
                type: "checkbox",
                checked: ""
              }, null, 8, u),
              l("label", {
                class: "form-check-label mx-1",
                for: `inputEnabled-${o}`
              }, "Reactor " + c(o), 9, m)
            ])
          ])), 64))
        ]),
        l("div", _, [
          p,
          (e(), t(s, null, i(8, (o) => l("div", {
            key: o,
            class: "col-12 col-sm-1"
          }, [
            l("div", h, [
              l("input", {
                id: `inputOdDilutionThreshold-${o}`,
                type: "number",
                class: "form-control",
                "aria-label": `OD Dilution Threshold for Reactor ${o}`,
                value: 0.8
              }, null, 8, b),
              l("label", {
                for: `inputOdDilutionThreshold-${o}`
              }, "Reactor " + c(o), 9, f)
            ])
          ])), 64))
        ]),
        l("div", v, [
          g,
          (e(), t(s, null, i(8, (o) => l("div", {
            key: o,
            class: "col-12 col-sm-1"
          }, [
            l("div", y, [
              l("input", {
                id: `inputDilutionTargetOD-${o}`,
                type: "number",
                class: "form-control",
                "aria-label": `Dilution Target OD for Reactor ${o}`,
                value: 0.3
              }, null, 8, D),
              l("label", {
                for: `inputDilutionTargetOD-${o}`
              }, "Reactor " + c(o), 9, T)
            ])
          ])), 64))
        ]),
        l("div", k, [
          $,
          (e(), t(s, null, i(8, (o) => l("div", {
            key: o,
            class: "col-12 col-sm-1"
          }, [
            l("div", R, [
              l("input", {
                id: `inputDilutionVolume-${o}`,
                type: "number",
                class: "form-control",
                "aria-label": `Dilution Volume for Reactor ${o}`,
                value: 1
              }, null, 8, w),
              l("label", {
                for: `inputDilutionVolume-${o}`
              }, "Reactor " + c(o), 9, x)
            ])
          ])), 64))
        ])
      ])
    ]));
  }
};
export {
  B as default
};
