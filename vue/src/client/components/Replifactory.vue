<template>
  <div id="alerts">
    <BAlert :model-value="true" :variant="backendConnectedAlertVariant"
      class="m-0 py-1 rounded-0 border border-0 d-flex justify-content-between align-content-center flex-wrap">
      <div class="flex-fill">
        Backend <strong>{{ connected ? "connected" : "disconnected" }}</strong>
      </div>
      <CFormSwitch id="switchDebug" v-model="debug" label="Debug" @input="debugHandleSwitchChange" />
      <a href="/security/logout" class="btn btn-outline-danger btn-sm ms-2">Logout</a>
      <MachineNotification />
    </BAlert>
  </div>
  <CContainer :fluid="true">
    <CRow>
      <CCol md="2">
        <CAccordion :active-item-key="1" class="mt-3">
          <CAccordionItem :item-key="1">
            <CAccordionHeader> Connection </CAccordionHeader>
            <CAccordionBody>
              <MachineConnection />
            </CAccordionBody>
          </CAccordionItem>
        </CAccordion>
        <CAccordion :active-item-key="2" class="mt-3">
          <CAccordionItem :item-key="2">
            <CAccordionHeader> State </CAccordionHeader>
            <CAccordionBody>
              <MachineState />
            </CAccordionBody>
          </CAccordionItem>
        </CAccordion>
        <CAccordion :active-item-key="3" class="mt-3">
          <CAccordionItem :item-key="3">
            <CAccordionHeader> Experiment Info </CAccordionHeader>
            <CAccordionBody />
          </CAccordionItem>
        </CAccordion>
      </CCol>
      <CCol md="10">
        <ul class="nav nav-tabs">
          <li class="nav-item">
            <BootstrapRouterLink to="/experiment" class="nav-link">
              Experiment
            </BootstrapRouterLink>
          </li>
          <li class="nav-item">
            <BootstrapRouterLink to="/device" class="nav-link"> Device </BootstrapRouterLink>
          </li>
          <!-- <li class="nav-item"><BootstrapRouterLink to="/remote">Remote</BootstrapRouterLink></li> -->
          <li class="nav-item">
            <BootstrapRouterLink to="/help" class="nav-link"> Help </BootstrapRouterLink>
          </li>
          <li class="nav-item">
            <BootstrapRouterLink to="/status" class="nav-link"> Status </BootstrapRouterLink>
          </li>
          <li class="nav-item">
            <BootstrapRouterLink to="/logs" class="nav-link"> Logs </BootstrapRouterLink>
          </li>
        </ul>
        <div class="tab-content">
          <router-view />
        </div>
      </CCol>
    </CRow>
  </CContainer>
</template>

<script>
import { socket } from "@/socket";
import { mapState, mapMutations } from "vuex";

import MachineConnection from "@/client/components/machine/MachineConnection.vue";
import MachineState from "@/client/components/machine/MachineState.vue";
import MachineNotification from "@/client/components/machine/MachineNotification.vue";
import {
  CContainer,
  CRow,
  CCol,
  CAccordion,
  CAccordionItem,
  CAccordionHeader,
  CAccordionBody,
} from "@coreui/vue";
import BootstrapRouterLink from "@/client/router/BootstrapRouterLink.vue";

export default {
  name: "App",
  components: {
    MachineConnection,
    MachineState,
    MachineNotification,
    CContainer,
    CRow,
    CCol,
    CAccordion,
    CAccordionItem,
    CAccordionHeader,
    CAccordionBody,
    BootstrapRouterLink,
  },
  data() {
    return {
      currentTab: "Machine",
      tabs: ["Experiment", "Device", "Remote", "Help", "Status", "Logs"],
    };
  },
  computed: {
    backendConnectedAlertVariant() {
      return this.connected ? "primary" : "danger";
    },
    ...mapState(["hostname", "debug"]),
    ...mapState({
      connected: (state) => state.backendConnected,
    }),
  },
  async mounted() {
    socket.connect();
  },
  beforeCreate() {
    this.$store.commit("initialiseStore");
    this.$store.subscribe((mutation, state) => {
      localStorage.setItem("store", JSON.stringify(state));
    });
  },
  methods: {
    ...mapMutations(["setDebug"]),
    debugHandleSwitchChange(event) {
      this.setDebug(event.target.checked);
    },
  },
};
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 0 auto;
  max-width: 1024px;
}

.icon {
  vertical-align: middle !important;
}

.form-switch>label {
  margin: 0 !important;
}
</style>
