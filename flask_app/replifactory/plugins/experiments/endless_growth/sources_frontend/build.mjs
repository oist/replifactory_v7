import { build } from "vite";
import path from "path";
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

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
