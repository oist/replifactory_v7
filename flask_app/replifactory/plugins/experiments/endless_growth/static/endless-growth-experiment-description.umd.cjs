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
  const _withScopeId = (n) => (vue.pushScopeId("data-v-aaa14cc2"), n = n(), vue.popScopeId(), n);
  const _hoisted_1 = { class: "card" };
  const _hoisted_2 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("p", null, [
    /* @__PURE__ */ vue.createTextVNode(" Edit "),
    /* @__PURE__ */ vue.createElementVNode("code", null, "components/HelloWorld.vue"),
    /* @__PURE__ */ vue.createTextVNode(" to test HMR ")
  ], -1));
  const _hoisted_3 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("p", null, [
    /* @__PURE__ */ vue.createTextVNode(" Check out "),
    /* @__PURE__ */ vue.createElementVNode("a", {
      href: "https://vuejs.org/guide/quick-start.html#local",
      target: "_blank"
    }, "create-vue"),
    /* @__PURE__ */ vue.createTextVNode(", the official Vue + Vite starter ")
  ], -1));
  const _hoisted_4 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("p", null, [
    /* @__PURE__ */ vue.createTextVNode(" Learn more about IDE Support for Vue in the "),
    /* @__PURE__ */ vue.createElementVNode("a", {
      href: "https://vuejs.org/guide/scaling-up/tooling.html#ide-support",
      target: "_blank"
    }, "Vue Docs Scaling up Guide"),
    /* @__PURE__ */ vue.createTextVNode(". ")
  ], -1));
  const _hoisted_5 = /* @__PURE__ */ _withScopeId(() => /* @__PURE__ */ vue.createElementVNode("p", { class: "read-the-docs" }, "Click on the Vite and Vue logos to learn more", -1));
  const _sfc_main = {
    __name: "ExperimentDescription",
    props: {
      msg: String
    },
    setup(__props) {
      const count = vue.ref(0);
      return (_ctx, _cache) => {
        return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
          vue.createElementVNode("h1", null, vue.toDisplayString(__props.msg), 1),
          vue.createElementVNode("div", _hoisted_1, [
            vue.createElementVNode("button", {
              type: "button",
              onClick: _cache[0] || (_cache[0] = ($event) => count.value++)
            }, "count is " + vue.toDisplayString(count.value), 1),
            _hoisted_2
          ]),
          _hoisted_3,
          _hoisted_4,
          _hoisted_5
        ], 64);
      };
    }
  };
  const ExperimentDescription = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-aaa14cc2"]]);
  return ExperimentDescription;
});
