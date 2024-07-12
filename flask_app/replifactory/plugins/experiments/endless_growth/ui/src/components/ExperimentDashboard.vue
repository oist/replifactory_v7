<script setup>
import { LineChart } from "echarts/charts";
import {
  DatasetComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
  TitleComponent,
  ToolboxComponent,
} from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";

use([
  LegendComponent,
  TooltipComponent,
  DatasetComponent,
  GridComponent,
  LineChart,
  CanvasRenderer,
  TitleComponent,
  ToolboxComponent,
]);

import { nextTick, onMounted, provide, ref } from "vue";
import VChart, { THEME_KEY } from "vue-echarts";

provide(THEME_KEY, "light");

const option = ref({
  title: {
    text: "Optical Density per Time",
    subtext: "Duration of the experiment: 48 hours",
    left: "center",
  },
  legend: {
    orient: "horizontal",
    left: "center",
    top: "bottom",
  },
  tooltip: {
    trigger: "axis",
    axisPointer: {
      type: "cross",
    },
  },
  toolbox: {
    show: true,
    feature: {
      saveAsImage: {},
    },
  },
  dataset: [
    {
      source: [
        [1, "2024-07-12 07:43:58", 0.1],
        [2, "2024-07-13 07:43:58", 0.2],
        [3, "2024-07-14 07:43:58", 0.4],
        [4, "2024-07-15 07:43:58", 0.6],
        [5, "2024-07-16 07:43:58", 0.8],
        [6, "2024-07-17 07:43:58", 0.2],
        [7, "2024-07-18 07:43:58", 0.4],
        [8, "2024-07-19 07:43:58", 0.6],
        [9, "2024-07-20 07:43:58", 0.8],
        [10, "2024-07-21 07:43:58", 0.2],
      ],
      dimensions: ["cycle", "datetime", "optical_density"],
    },
    {
      dimensions: ["cycle", "datetime", "optical_density"],
      source: [
        [1, "2024-07-12 07:43:58", 0.7],
        [2, "2024-07-13 07:43:58", 0.7],
        [3, "2024-07-14 07:43:58", 0.35],
        [4, "2024-07-15 07:43:58", 0.86],
        [5, "2024-07-16 07:43:58", 0.37],
        [6, "2024-07-17 07:43:58", 0.74],
        [7, "2024-07-18 07:43:58", 0.63],
        [8, "2024-07-19 07:43:58", 0.38],
        [9, "2024-07-20 07:43:58", 0.36],
        [10, "2024-07-21 07:43:58", 0.78],
      ],
    },
  ],
  xAxis: {
    type: "time",
  },
  yAxis: {
    type: "value",
  },
  series: [
    {
      type: "line",
      datasetIndex: 0,
      showSymbol: false,
      name: "OD Reactor 1",
      encode: { x: "datetime", y: "optical_density" },
    },
    {
      type: "line",
      datasetIndex: 1,
      showSymbol: false,
      name: "OD Reactor 2",
      encode: { x: "datetime", y: "optical_density" },
    },
  ],
});

const chartContainer = ref(null);

onMounted(() => {
  nextTick(() => {
    // Ensure the chart initializes after the container is guaranteed to be in the DOM and visible
    if (chartContainer.value) {
      // Initialize or update your chart here
      // Since you're using vue-echarts, the chart initialization is handled for you
      // Just make sure the container is visible and has dimensions
    }
  });
});
</script>

<template>
  <section
    ref="chartContainer"
    class="w-100 bg-body overflow-hidden"
    style="height: 400px"
  >
    <v-chart class="chart w-100" :option="option" autoresize />
  </section>
</template>

<style scoped>
.chart {
  height: 400px;
}
</style>
