const { execSync } = require("child_process");

const components = [
  {
    name: "od-measure-experiment-parameters",
    entry: "src/components/ExperimentParameters.vue",
  },
  {
    name: "od-measure-experiment-description",
    entry: "src/components/ExperimentDescription.vue",
  },
];

components.forEach((component, index) => {
  console.log(`Building ${component.name}...`);
  // Use --no-clean option for every execSync call after the first one
  const buildCommand = `vue-cli-service build --target lib --formats umd-min --name ${component.name} ${component.entry}${index > 0 ? " --no-clean" : ""}`;
  execSync(buildCommand, { stdio: "inherit" });
  console.log(`${component.name} built successfully.`);
});
