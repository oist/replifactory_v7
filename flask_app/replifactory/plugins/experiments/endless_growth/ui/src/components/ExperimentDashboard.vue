<script setup>
import { LineChart } from "echarts/charts";
import {
  DatasetComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
  TitleComponent,
  ToolboxComponent,
  MarkPointComponent,
  MarkAreaComponent,
  MarkLineComponent,
  DataZoomComponent,
  DataZoomInsideComponent,
} from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import VChart, { THEME_KEY } from "vue-echarts";
import { defineProps, watch, provide, ref } from "vue";

use([
  LegendComponent,
  TooltipComponent,
  DatasetComponent,
  GridComponent,
  LineChart,
  CanvasRenderer,
  TitleComponent,
  ToolboxComponent,
  MarkPointComponent,
  MarkAreaComponent,
  MarkLineComponent,
  DataZoomComponent,
  DataZoomInsideComponent,
]);

provide(THEME_KEY, "light");

const props = defineProps({
  // experimentId: {
  //   type: Object,
  //   required: true,
  // },
  experimentData: {
    type: Object,
    required: true,
  },
});

const option = ref({
  title: {
    text: "Optical Density per Time",
    subtext: "Duration of the experiment: 48 hours",
    left: "center",
  },
  legend: {
    orient: "vertical",
    left: "left",
    top: "top",
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
      dataZoom: {
        yAxisIndex: "none",
      },
      restore: {},
      saveAsImage: {},
    },
  },
  // dataZoom: [
  //   // {
  //   //   startValue: "2024-07-12 07:43:58",
  //   // },
  //   {
  //     type: "inside",
  //   },
  // ],
  xAxis: {
    type: "time",
  },
  yAxis: {
    type: "value",
  },
  // series: [
  //   {
  //     type: "line",
  //     datasetIndex: 0,
  //     showSymbol: false,
  //     name: "OD Reactor 1",
  //     encode: { x: "datetime", y: "optical_density" },
  //     markPoint: {
  //       data: [
  //         { coord: ["2024-08-30 07:43:58", 0.742], name: "Dead", value: "Ded" },
  //       ],
  //     },
  //   },
  //   {
  //     type: "line",
  //     datasetIndex: 1,
  //     showSymbol: false,
  //     name: "OD Reactor 2",
  //     encode: { x: "datetime", y: "optical_density" },
  //     markArea: {
  //       itemStyle: {
  //         color: "rgba(255, 173, 177, 0.4)",
  //       },
  //       data: [
  //         [
  //           {
  //             name: "Sampling",
  //             xAxis: "2024-09-16 07:43:58",
  //           },
  //           {
  //             xAxis: "2024-09-26 07:43:58",
  //           },
  //         ],
  //       ],
  //     },
  //     markLine: {
  //       data: [
  //         {
  //           name: "OD Threshold",
  //           yAxis: 0.87,
  //         },
  //       ],
  //     },
  //   },
  //   {
  //     type: "line",
  //     showSymbol: false,
  //     name: "Events",
  //     data: [],
  //     markLine: {
  //           data: [
  //               {
  //                   xAxis: "2024-07-12 07:43:58",
  //                   label: {
  //                       show: true,
  //                       formatter: 'Start',
  //                       color: 'red'
  //                   },
  //                   lineStyle: {
  //                       color: 'red'
  //                   }
  //               },
  //               {
  //                   xAxis: "2024-12-14 07:43:58",
  //                   label: {
  //                       show: true,
  //                       formatter: 'System Reboot',
  //                       color: 'blue'
  //                   },
  //                   lineStyle: {
  //                       color: 'blue'
  //                   }
  //               },
  //               {
  //                   xAxis: "2025-02-14 07:43:58",
  //                   label: {
  //                       show: true,
  //                       formatter: 'End',
  //                       color: 'green'
  //                   },
  //                   lineStyle: {
  //                       color: 'green'
  //                   }
  //               }
  //           ]
  //       },
  //   },
  // ],
});


watch(props, (newVal) => {
  const experimentData = newVal.experimentData;
  const series = experimentData.dataset.map((data, index) => ({
    type: "line",
    datasetIndex: index,
    showSymbol: false,
    name: data.meta.name,
    encode: { x: "datetime", y: "optical_density" },
    markArea: {
      itemStyle: {
        color: "rgba(255, 173, 177, 0.4)",
      },
      data: data.markedAreas,
    },
  }));
  series.push({
    type: "line",
    showSymbol: false,
    name: "Events",
    data: [],
    markLine: {
      data: experimentData.events.map((event) => ({
        xAxis: event.datetime,
        label: {
          show: true,
          formatter: event.name,
          color: "black",
        },
        lineStyle: {
          color: "black",
        },
      })),
    },
  });
  const newOption = {
    ...option.value,
    dataset: experimentData.dataset,
    series: series,
    dataZoom: [
      {
        startValue: experimentData.startTime,
      },
      {
        type: "inside",
      },
    ],
  };

  option.value = newOption;
});
</script>

<template>
  <section class="w-100 bg-body overflow-hidden" style="height: 400px">
    <v-chart class="chart w-100" :option="option" autoresize />
  </section>
</template>

<style scoped>
.chart {
  height: 400px;
}
</style>
