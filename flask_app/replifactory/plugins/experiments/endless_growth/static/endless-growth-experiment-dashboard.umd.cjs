(function(global, factory) {
  typeof exports === "object" && typeof module !== "undefined" ? module.exports = factory(require("vue")) : typeof define === "function" && define.amd ? define(["vue"], factory) : (global = typeof globalThis !== "undefined" ? globalThis : global || self, global["endless-growth-experiment-dashboard"] = factory(global.Vue));
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
  const _hoisted_1 = /* @__PURE__ */ vue.createElementVNode("h1", null, "Dashboard", -1);
  const _hoisted_2 = [
    _hoisted_1
  ];
  function _sfc_render(_ctx, _cache) {
    return vue.openBlock(), vue.createElementBlock("section", null, _hoisted_2);
  }
  const ExperimentDashboard = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render]]);
  return ExperimentDashboard;
});
