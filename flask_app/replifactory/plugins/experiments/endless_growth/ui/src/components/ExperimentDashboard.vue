<script setup>
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { PieChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent
} from "echarts/components";
import VChart, { THEME_KEY } from "vue-echarts";
import { ref, provide, onMounted, nextTick } from "vue";

use([
  CanvasRenderer,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent
]);

provide(THEME_KEY, "light");

const option = ref({
  title: {
    text: "Traffic Sources",
    left: "center"
  },
  tooltip: {
    trigger: "item",
    formatter: "{a} <br/>{b} : {c} ({d}%)"
  },
  legend: {
    orient: "vertical",
    left: "left",
    data: ["Direct", "Email", "Ad Networks", "Video Ads", "Search Engines"]
  },
  series: [
    {
      name: "Traffic Sources",
      type: "pie",
      radius: "55%",
      center: ["50%", "60%"],
      data: [
        { value: 335, name: "Direct" },
        { value: 310, name: "Email" },
        { value: 234, name: "Ad Networks" },
        { value: 135, name: "Video Ads" },
        { value: 1548, name: "Search Engines" }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: "rgba(0, 0, 0, 0.5)"
        }
      }
    }
  ]
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
  <section ref="chartContainer" class="w-100 bg-body" style="height: 400px;">
    <v-chart class="chart" :option="option" />
  </section>
</template>

<style scoped>
.chart {
  height: 400px;
}
</style>
