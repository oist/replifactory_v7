(function(global, factory) {
  typeof exports === "object" && typeof module !== "undefined" ? module.exports = factory(require("vue")) : typeof define === "function" && define.amd ? define(["vue"], factory) : (global = typeof globalThis !== "undefined" ? globalThis : global || self, global["endless-growth-experiment-description"] = factory(global.Vue));
})(this, function(vue) {
  "use strict";
  const _export_sfc = (sfc, props) => {
    const target = sfc.__vccOpts || sfc;
    for (const [key, val] of props) {
      target[key] = val;
    }
    return target;
  };
  const _sfc_main = {};
  const _hoisted_1 = /* @__PURE__ */ vue.createStaticVNode("<p> Objective: To maintain a microbial culture at a constant OD by applying infinite dilution techniques, ensuring the culture remains in the exponential growth phase </p><p> Background: Optical density at 600 nm (OD600) is a common measure of bacterial culture density. It reflects the light scattering by the bacteria in the culture. The OD600 value is used to estimate the cell concentration and to maintain the culture in the desired growth phase1. </p><p>Method:</p><ol><li><b>Preparation:</b> Begin with a microbial culture at a known OD, which is within the linear range of the spectrophotometer used for OD measurements. </li><li><b>Cycling Process:</b><ul><li><b>Measure OD:</b> At regular intervals (e.g., every 30 minutes), measure the OD of the culture. </li><li><b>Dilution:</b> If the OD exceeds the target value, dilute the culture with fresh medium to bring it back to the desired OD. </li><li><b>Inoculation:</b> After dilution, inoculate the culture into a new vessel to continue growth. </li></ul></li><li><b>Monitoring:</b> Continuously monitor the OD to ensure it stays within the target range, indicating the culture is in the log phase of growth. </li></ol><p>Considerations:</p><ul><li><b>Dilution Factor:</b> The dilution factor depends on the initial and target OD values. It should be calculated to ensure the culture is brought back to the target OD after each cycle. </li><li><b>Growth Phase:</b> Maintaining the culture at a specific OD helps keep it in the exponential (log) phase, which is ideal for many types of experiments, such as protein expression2. </li></ul><p> Conclusion: This experiment allows for the continuous cultivation of a microbial culture at a controlled OD, facilitating studies that require the culture to remain in a specific growth phase. </p>", 7);
  const _hoisted_8 = [
    _hoisted_1
  ];
  function _sfc_render(_ctx, _cache) {
    return vue.openBlock(), vue.createElementBlock("section", null, _hoisted_8);
  }
  const ExperimentDescription = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
  return ExperimentDescription;
});
