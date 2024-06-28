<template>
  <div>
    <!-- <button @click="createToast">Show Toaster</button> -->
    <CToaster placement="top-end" class="pt-5">
      <CToast
        v-for="(toast, index) in messages"
        :key="index"
        :delay="toast.delay"
        :autohide="toast.autohide"
        :color="toast.color"
        visible
      >
        <CToastHeader close-button>
          <span class="me-auto fw-bold">{{ toast.title }}</span>
          <!-- <small>7 min ago</small> -->
        </CToastHeader>
        <CToastBody>
          {{ toast.content }}
        </CToastBody>
      </CToast>
    </CToaster>
  </div>
</template>

<script>
import { mapState } from "vuex";
import { CToaster, CToast, CToastHeader, CToastBody } from "@coreui/vue";

export default {
  components: {
    CToaster,
    CToast,
    CToastHeader,
    CToastBody,
  },
  computed: {
    ...mapState(["messages"]),
  },
  methods: {
    createToast() {
      this.$store.dispatch("notifyWarning", {
        // title: 'new toast',
        content: "Lorem ipsum dolor cet emit",
      });
    },
  },
};
</script>
