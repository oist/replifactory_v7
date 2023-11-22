<template>
  <div id="alerts">
    <BAlert :model-value="true" :variant="backendConnectedAlertVariant" class="m-0 py-1 rounded-0 border border-0">
      Backend <strong>{{ connected ? "connected" : "disconnected" }}</strong>
    </BAlert>
  </div>
  <CContainer :fluid="true">
    <CRow>
      <CCol md="3">
        <CAccordion :active-item-key="1" class="mt-3">
          <CAccordionItem :item-key="1">
            <CAccordionHeader>
              Connection
            </CAccordionHeader>
            <CAccordionBody>
              <MachineConnection />
            </CAccordionBody>
          </CAccordionItem>
        </CAccordion>
        <CAccordion :active-item-key="2" class="mt-3">
          <CAccordionItem :item-key="2">
            <CAccordionHeader>
              State
            </CAccordionHeader>
            <CAccordionBody>
              <MachineState />
            </CAccordionBody>
          </CAccordionItem>
        </CAccordion>
        <CAccordion :active-item-key="3" class="mt-3">
          <CAccordionItem :item-key="3">
            <CAccordionHeader>
              Experiment Info
            </CAccordionHeader>
            <CAccordionBody>

            </CAccordionBody>
          </CAccordionItem>
        </CAccordion>
      </CCol>
      <CCol md="9">
        <ul class="nav nav-tabs">
          <BootstrapRouterLink to="/experiment">Experiment</BootstrapRouterLink>
          <BootstrapRouterLink to="/device">Device</BootstrapRouterLink>
          <BootstrapRouterLink to="/remote">Remote</BootstrapRouterLink>
          <BootstrapRouterLink to="/help">Help</BootstrapRouterLink>
          <BootstrapRouterLink to="/status">Status</BootstrapRouterLink>
          <BootstrapRouterLink to="/logs">Logs</BootstrapRouterLink>
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
import { mapState } from 'vuex';

import MachineConnection from "@/client/components/machine/MachineConnection.vue";
import MachineState from "@/client/components/machine/MachineState.vue";
import { CContainer, CRow, CCol, CAccordion, CAccordionItem, CAccordionHeader, CAccordionBody } from '@coreui/vue';
import BootstrapRouterLink from "@/client/router/BootstrapRouterLink";

export default {
  name: 'App',
  computed: {
    backendConnectedAlertVariant() {
      return this.connected ? "primary" : "danger";
    },
    ...mapState(['hostname']),
    ...mapState({
      connected: state => state.backendConnected,
    }),
  },
  async mounted() {
    socket.connect();
  },

  components: {
    MachineConnection,
    MachineState,
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
      currentTab: 'Machine',
      tabs: ['Experiment', 'Device', 'Remote', 'Help', 'Status', 'Logs']
    };
  },
};
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 0 auto;
  max-width: 1024px;
}
</style>