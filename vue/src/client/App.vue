<template>
  <div id="app" class="container-fluid fixed-top p-0">
    <div id="alerts">
      <BAlert :model-value="true" :variant="backendConnectedAlertVariant" class="m-0 py-1 rounded-0 border border-0">
        Backend <strong>{{ connected ? "connected" : "disconnected" }}</strong>
      </BAlert>
    </div>
    <ul class="nav nav-tabs" id="myTab">
      <li class="nav-item" v-for="tab in tabs" :key="tab">
        <a class="nav-link" :class="{ active: currentTab === tab }" href="#" @click="currentTab = tab">{{ tab }}</a>
      </li>
    </ul>
    <div class="tab-content">
      <!--      <HomeTab v-if="currentTab === 'Home'"/>-->
      <MachineTab v-if="currentTab === 'Machine'" />
      <ExperimentTab v-if="currentTab === 'Experiment'" />
      <DeviceControl v-if="currentTab === 'Device'" />
      <NgrokTab v-if="currentTab === 'Remote'" />
      <HelpTab v-if="currentTab === 'Help'" />
      <StatusTab v-if="currentTab === 'Status'" />
      <LogsTab v-if="currentTab === 'Logs'" />
    </div>
  </div>
</template>

<script>
import { socket, state } from "@/socket";
import { mapState } from 'vuex';

import DeviceControl from './components/DeviceControl/DeviceControl';
// import HomeTab from '@/client/components/HomeTab/HomeTab';
import ExperimentTab from "@/client/components/ExperimentTab/ExperimentTab";
import NgrokTab from "@/client/components/Remote/NgrokTab";
import HelpTab from "@/client/components/HelpTab/HelpTab";
import StatusTab from "@/client/components/StatusTab/StatusTab";
import LogsTab from "@/client/components/LogsTab/LogsTab";
import MachineTab from "@/client/components/MachineTab/MachineTab";

export default {
  name: 'App',
  computed: {
    connected() {
      return state.connected;
    },
    backendConnectedAlertVariant() {
      return state.connected ? "primary" : "danger";
    },
    ...mapState(['hostname']),
  },
  async mounted() {
    await this.$store.dispatch('fetchHostname');
    document.title = this.hostname;

    socket.connect();
  },

  components: {
    ExperimentTab,
    DeviceControl,
    NgrokTab,
    HelpTab,
    StatusTab,
    LogsTab,
    MachineTab,
  },
  data() {
    return {
      currentTab: 'Machine',
      tabs: ['Machine', 'Experiment', 'Device', 'Remote', 'Help', 'Status', 'Logs']
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