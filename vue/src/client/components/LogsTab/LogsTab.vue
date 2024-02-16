<template>
  <div>
    <!-- Log Tail Selection -->
    <div class="d-flex align-items-center mt-3">
      <CButton
        color="info"
        class="btn mt-3"
        style="width: 20%"
        @click="fetchLogTails"
      >
        Get Logs
      </CButton>
      <CFormFloating class="mt-3 ml-3" style="width: 20%">
        <CFormInput
          id="floatingInput"
          type="number"
          style="background-color: transparent; border: none"
          :value="formatNumber(lines)"
          floating-label="Number of Lines"
        />
      </CFormFloating>
    </div>

    <!-- Display Log Tails -->
    <div v-for="(content, fileName) in logs" :key="fileName" class="mt-3">
      <h3>{{ fileName }}</h3>
      <pre>{{ content }}</pre>
    </div>
  </div>
</template>

<script>
import api from "@/api";
import { CButton, CFormInput, CFormFloating } from "@coreui/vue";

export default {
  components: {
    CButton,
    CFormInput,
    CFormFloating,
  },
  data() {
    return {
      lines: 100,
      logs: {},
    };
  },
  mounted() {
    this.fetchLogTails();
  },
  methods: {
    formatNumber(number) {
      return number !== null ? number.toFixed(0) : "N/A";
    },
    fetchLogTails() {
      api.get(`/log/${this.lines}/`).then((response) => {
        this.logs = response.data;
      });
    },
  },
};
</script>
