<template>
  <div id="CulturePlot">
    <!-- Add the button here -->
    <CButton color="success" class="mt-3 ml-3" @click="plotAllData">
      Plot
    </CButton>

    <div
      v-for="vial in vials"
      :id="`vial-${vial}`"
      :key="vial"
      class="graph-container"
    />
  </div>
</template>

<script>
import Plotly from "plotly.js";
import { mapActions, mapState } from "vuex";
import { CButton } from "@coreui/vue";

export default {
  name: "ExperimentChart",
  components: {
    CButton,
  },
  computed: {
    ...mapState("experiment", ["plot_data", "currentExperiment"]),
  },
  data() {
    return {
      vials: Array.from({ length: 7 }, (_, i) => i + 1),
    };
  },
  methods: {
    ...mapActions("experiment", ["fetchCulturePlot"]),

    async plotAllData() {
      // Fetch and plot data for each vial
      if (!this.currentExperiment) {
        return;
      }
      for (let vial of this.vials) {
        console.log(this.currentExperiment, "currentExperiment");
        await this.fetchCulturePlot(vial);
        this.plotData(vial);
      }
    },

    plotData(vial) {
      const data = this.plot_data[vial] || [];

      const layout = {
        title: `Culture ${vial}`,
        xaxis: {
          title: "Time",
        },
        yaxis: {
          title: "Optical Density",
          automargin: true,
          mode: "lines+markers",
        },
        yaxis2: {
          title: "Generation",
          overlaying: "y",
          side: "right",
          automargin: true,
        },
        yaxis3: {
          title: "Concentration",
          overlaying: "y",
          side: "right",
          position: 0.92,
          automargin: true,
        },
        yaxis4: {
          title: "Growth Rate",
          overlaying: "y",
          side: "left",
          position: 0.08,
          automargin: true,
        },
      };

      const graphDiv = document.getElementById(`vial-${vial}`);
      if (graphDiv) {
        Plotly.react(`vial-${vial}`, data, layout);
      }
    },
  },
  mounted() {
    this.plotAllData();
  },
};
</script>

<style scoped>
#CulturePlot {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.graph-container {
  width: 90vw;
  height: 80vh;
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
}
</style>
