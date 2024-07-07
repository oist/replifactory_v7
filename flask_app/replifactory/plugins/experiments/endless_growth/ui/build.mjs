import { build } from "vite";

const libraries = [
  {
    entry: "src/components/ExperimentDescription.vue",
    fileName: "endless-growth-experiment-description",
    name: "endless-growth-experiment-description",
  },
  {
    entry: "src/components/ExperimentParameters.vue",
    fileName: "endless-growth-experiment-parameters",
    name: "endless-growth-experiment-parameters",
  },
  {
    entry: "src/components/ExperimentDashboard.vue",
    fileName: "endless-growth-experiment-dashboard",
    name: "endless-growth-experiment-dashboard",
  },
];

libraries.forEach(async (lib) => {
  await build({
    build: {
      outDir: "../static",
      lib: {
        ...lib,
        formats: ["umd"],
      },
      emptyOutDir: false,
    },
  });
});
