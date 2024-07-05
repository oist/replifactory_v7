import * as Vue from "vue";
window.Vue = Vue;

export async function fetchPlugins() {
  const response = await fetch("/api/plugins");
  return response.json();
}

export async function loadPlugins(app) {
  const plugins = await fetchPlugins();
  for (const plugin of plugins) {
    try {
      if (plugin.frontend_modules && Array.isArray(plugin.frontend_modules)) {
        for (const moduleInfo of plugin.frontend_modules) {
          // Assuming moduleInfo.url contains the URL to the module
          //   const module = await import(/* @vite-ignore */ moduleInfo.url);
          const asyncComponent = Vue.defineAsyncComponent(
            () => import(/* @vite-ignore */ moduleInfo.url),
          );
          app.component(plugin.name, asyncComponent);
          //   app.provide(plugin.name, module)
          //   if (module.default) {
          //     // Assuming the component is exported as default
          //     app.component(plugin.name, module.default);
          //   } else {
          // console.error(
          //       `Module ${moduleInfo.url} does not have a default export.`,
          //     );
          //   }
          //   if (typeof module.default === "function") {
          //     // Pass the Vue app instance to the imported module if it exports a function
          //     module.default(app);
          //   } else {
          //     // Use the module directly if it's not a function (e.g., a Vue plugin)
          //     app.use(module.default);
          //   }
        }
      }
    } catch (e) {
      console.error(`Error loading plugin ${plugin.name}: ${e}`);
    }
  }
}

export async function externalComponent(url) {
  let name;
  try {
    name = url
      .split("/")
      .reverse()[0]
      .match(/^(.*?)\.umd/)[1];
    if (!name) throw new Error("Failed to extract module name from URL");
  } catch (e) {
    return Promise.reject(new Error(`Error parsing URL: ${url} ${e.message}`));
  }

  // Check if the module is already loaded or being loaded
  if (window[name]) {
    // If it's a promise, return it directly to avoid creating a new promise
    if (window[name] instanceof Promise) {
      return window[name];
    }
    // If the module is already loaded, wrap it in a resolved promise
    return Promise.resolve(window[name]);
  }

  // Create a new promise for loading the module
  window[name] = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.async = true;
    script.addEventListener("load", () => {
      // Ensure the script is loaded by checking if the module is defined
      if (window[name]) {
        resolve(window[name]);
      } else {
        reject(new Error(`Module ${name} did not load correctly.`));
      }
    });
    script.addEventListener("error", () => {
      reject(new Error(`Error loading ${url}`));
    });
    script.src = url;
    document.head.appendChild(script);
  });

  return window[name];
}
