(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory(require("vue"));
	else if(typeof define === 'function' && define.amd)
		define([], factory);
	else if(typeof exports === 'object')
		exports["od-measure-replyfactory-plugin.75bba13b51cfe815"] = factory(require("vue"));
	else
		root["od-measure-replyfactory-plugin.75bba13b51cfe815"] = factory(root["Vue"]);
})((typeof self !== 'undefined' ? self : this), function(__WEBPACK_EXTERNAL_MODULE__274__) {
return /******/ (function() { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 262:
/***/ (function(__unused_webpack_module, exports) {

var __webpack_unused_export__;

__webpack_unused_export__ = ({ value: true });
// runtime helper for setting properties on components
// in a tree-shakable way
exports.A = (sfc, props) => {
    const target = sfc.__vccOpts || sfc;
    for (const [key, val] of props) {
        target[key] = val;
    }
    return target;
};


/***/ }),

/***/ 274:
/***/ (function(module) {

module.exports = __WEBPACK_EXTERNAL_MODULE__274__;

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	!function() {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = function(exports, definition) {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	!function() {
/******/ 		__webpack_require__.o = function(obj, prop) { return Object.prototype.hasOwnProperty.call(obj, prop); }
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/publicPath */
/******/ 	!function() {
/******/ 		__webpack_require__.p = "";
/******/ 	}();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};

// EXPORTS
__webpack_require__.d(__webpack_exports__, {
  "default": function() { return /* binding */ entry_lib; }
});

;// CONCATENATED MODULE: ./node_modules/@vue/cli-service/lib/commands/build/setPublicPath.js
/* eslint-disable no-var */
// This file is imported into lib/wc client bundles.

if (typeof window !== 'undefined') {
  var currentScript = window.document.currentScript
  if (false) { var getCurrentScript; }

  var src = currentScript && currentScript.src.match(/(.+\/)[^/]+\.js(\?.*)?$/)
  if (src) {
    __webpack_require__.p = src[1] // eslint-disable-line
  }
}

// Indicate to webpack that this file can be concatenated
/* harmony default export */ var setPublicPath = (null);

// EXTERNAL MODULE: external {"commonjs":"vue","commonjs2":"vue","root":"Vue"}
var external_commonjs_vue_commonjs2_vue_root_Vue_ = __webpack_require__(274);
;// CONCATENATED MODULE: ./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/Parameters.vue?vue&type=template&id=2942f497


const _hoisted_1 = /*#__PURE__*/(0,external_commonjs_vue_commonjs2_vue_root_Vue_.createStaticVNode)("<h3>Global Parameters</h3><form><div class=\"row mb-3\"><label for=\"inputCycleTime\" class=\"col-sm-2 col-form-label\">Cycle time</label><div class=\"col-auto\"><div class=\"input-group mb-3\"><input id=\"inputCycleTime\" type=\"number\" class=\"form-control\" aria-label=\"Cycle time\" aria-describedby=\"inputCycleTimeUnit\" value=\"240\"><span id=\"inputCycleTimeUnit\" class=\"input-group-text\">seconds</span></div></div></div></form><h3>Reactors parameters</h3>", 3)
const _hoisted_4 = { class: "row mb-2 g-2" }
const _hoisted_5 = /*#__PURE__*/(0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", { class: "col-sm-4 col-form-label" }, [
  /*#__PURE__*/(0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("strong", null, "Enabled")
], -1)
const _hoisted_6 = ["id"]
const _hoisted_7 = ["for"]
const _hoisted_8 = { class: "row mb-2 g-2" }
const _hoisted_9 = /*#__PURE__*/(0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", { class: "col-sm-4 col-form-label" }, [
  /*#__PURE__*/(0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("strong", null, "Dilution Threshold"),
  /*#__PURE__*/(0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", {
    id: "passwordHelpBlock",
    class: "form-text"
  }, " An optical density value which triggers the dilution process in the reactor. ")
], -1)
const _hoisted_10 = { class: "form-floating" }
const _hoisted_11 = ["id", "aria-label"]
const _hoisted_12 = ["for"]
const _hoisted_13 = { class: "row mb-2 g-2" }
const _hoisted_14 = /*#__PURE__*/(0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", { class: "col-sm-4 col-form-label" }, [
  /*#__PURE__*/(0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("strong", null, "Dilution Target OD")
], -1)
const _hoisted_15 = { class: "form-floating" }
const _hoisted_16 = ["id", "aria-label"]
const _hoisted_17 = ["for"]
const _hoisted_18 = { class: "row mb-2 g-2" }
const _hoisted_19 = /*#__PURE__*/(0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", { class: "col-sm-4 col-form-label" }, [
  /*#__PURE__*/(0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("strong", null, "Dilution Volume (mL)")
], -1)
const _hoisted_20 = { class: "form-floating" }
const _hoisted_21 = ["id", "aria-label"]
const _hoisted_22 = ["for"]

function render(_ctx, _cache) {
  return ((0,external_commonjs_vue_commonjs2_vue_root_Vue_.openBlock)(), (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementBlock)("section", null, [
    _hoisted_1,
    (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("form", null, [
      (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", _hoisted_4, [
        _hoisted_5,
        ((0,external_commonjs_vue_commonjs2_vue_root_Vue_.openBlock)(), (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementBlock)(external_commonjs_vue_commonjs2_vue_root_Vue_.Fragment, null, (0,external_commonjs_vue_commonjs2_vue_root_Vue_.renderList)(8, (n) => {
          return (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", {
            key: n,
            class: "col-12 col-sm-1"
          }, [
            (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", null, [
              (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("input", {
                id: `inputEnabled-${n}`,
                class: "form-check-input",
                type: "checkbox",
                checked: ""
              }, null, 8, _hoisted_6),
              (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("label", {
                class: "form-check-label mx-1",
                for: `inputEnabled-${n}`
              }, "Reactor " + (0,external_commonjs_vue_commonjs2_vue_root_Vue_.toDisplayString)(n), 9, _hoisted_7)
            ])
          ])
        }), 64))
      ]),
      (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", _hoisted_8, [
        _hoisted_9,
        ((0,external_commonjs_vue_commonjs2_vue_root_Vue_.openBlock)(), (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementBlock)(external_commonjs_vue_commonjs2_vue_root_Vue_.Fragment, null, (0,external_commonjs_vue_commonjs2_vue_root_Vue_.renderList)(8, (n) => {
          return (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", {
            key: n,
            class: "col-12 col-sm-1"
          }, [
            (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", _hoisted_10, [
              (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("input", {
                id: `inputOdDilutionThreshold-${n}`,
                type: "number",
                class: "form-control",
                "aria-label": `OD Dilution Threshold for Reactor ${n}`,
                value: 0.8
              }, null, 8, _hoisted_11),
              (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("label", {
                for: `inputOdDilutionThreshold-${n}`
              }, "Reactor " + (0,external_commonjs_vue_commonjs2_vue_root_Vue_.toDisplayString)(n), 9, _hoisted_12)
            ])
          ])
        }), 64))
      ]),
      (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", _hoisted_13, [
        _hoisted_14,
        ((0,external_commonjs_vue_commonjs2_vue_root_Vue_.openBlock)(), (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementBlock)(external_commonjs_vue_commonjs2_vue_root_Vue_.Fragment, null, (0,external_commonjs_vue_commonjs2_vue_root_Vue_.renderList)(8, (n) => {
          return (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", {
            key: n,
            class: "col-12 col-sm-1"
          }, [
            (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", _hoisted_15, [
              (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("input", {
                id: `inputDilutionTargetOD-${n}`,
                type: "number",
                class: "form-control",
                "aria-label": `Dilution Target OD for Reactor ${n}`,
                value: 0.3
              }, null, 8, _hoisted_16),
              (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("label", {
                for: `inputDilutionTargetOD-${n}`
              }, "Reactor " + (0,external_commonjs_vue_commonjs2_vue_root_Vue_.toDisplayString)(n), 9, _hoisted_17)
            ])
          ])
        }), 64))
      ]),
      (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", _hoisted_18, [
        _hoisted_19,
        ((0,external_commonjs_vue_commonjs2_vue_root_Vue_.openBlock)(), (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementBlock)(external_commonjs_vue_commonjs2_vue_root_Vue_.Fragment, null, (0,external_commonjs_vue_commonjs2_vue_root_Vue_.renderList)(8, (n) => {
          return (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", {
            key: n,
            class: "col-12 col-sm-1"
          }, [
            (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("div", _hoisted_20, [
              (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("input", {
                id: `inputDilutionVolume-${n}`,
                type: "number",
                class: "form-control",
                "aria-label": `Dilution Volume for Reactor ${n}`,
                value: 1.0
              }, null, 8, _hoisted_21),
              (0,external_commonjs_vue_commonjs2_vue_root_Vue_.createElementVNode)("label", {
                for: `inputDilutionVolume-${n}`
              }, "Reactor " + (0,external_commonjs_vue_commonjs2_vue_root_Vue_.toDisplayString)(n), 9, _hoisted_22)
            ])
          ])
        }), 64))
      ])
    ])
  ]))
}
;// CONCATENATED MODULE: ./src/components/Parameters.vue?vue&type=template&id=2942f497

// EXTERNAL MODULE: ./node_modules/vue-loader/dist/exportHelper.js
var exportHelper = __webpack_require__(262);
;// CONCATENATED MODULE: ./src/components/Parameters.vue

const script = {}

;
const __exports__ = /*#__PURE__*/(0,exportHelper/* default */.A)(script, [['render',render]])

/* harmony default export */ var Parameters = (__exports__);
;// CONCATENATED MODULE: ./node_modules/@vue/cli-service/lib/commands/build/entry-lib.js


/* harmony default export */ var entry_lib = (Parameters);


__webpack_exports__ = __webpack_exports__["default"];
/******/ 	return __webpack_exports__;
/******/ })()
;
});
//# sourceMappingURL=od-measure-replyfactory-plugin.75bba13b51cfe815.umd.js.map