<template>
    <div class="ExperimentsList">
        <div class="list-group">
            <a href="#" class="list-group-item list-group-item-action" v-for="experiment in experiments"
                :key="experiment.id" :value="experiment">
                <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">{{ experiment.name }}</h5>
                    <!-- <small>{{ experiment.created_at }}</small> -->
                </div>
            </a>
        </div>
    </div>
</template>

<script>
import { mapState, mapGetters } from "vuex";
import api from "@/api.js";

export default {
  components: {

  },
  data() {
    return {
      selectedMachine: undefined,
      loading: false,
      error: "",
      showAlert: false,
    };
  },
  computed: {
    connectionOptions() {
      let options = {};
      let stateConnectedOptions = this.$store.state.machine.connection.options;
      if (
        this.isConnected &&
        this.currentConnection !== undefined &&
        !(this.currentConnection.id in options)
      ) {
        options[this.currentConnection.id] = this.currentConnection;
        return {
          ...stateConnectedOptions,
          ...{
            devices: options,
          },
        };
      }
      return stateConnectedOptions;
    },
    ...mapState("machine", {
      currentConnection: (state) => state.connection.current,
      machineState: (state) => state.machineState,
    }),
    ...mapGetters("machine", ["isDisconnected", "isConnected"]),
  },
  watch: {
    connectionOptions(newVal) {
      const options = newVal.devices;
      if (this.isDisconnected && !(this.selectedMachine in options)) {
        const [firstDeviceId] = Object.keys(options);
        this.selectedMachine = firstDeviceId;
      }
    },
    currentConnection(newVal) {
      if (newVal != null) {
        this.selectedMachine = newVal.id;
      }
    },
  },
  mounted() {
    this.getExperimentsList();
  },
  methods: {
    async disconnectMachine() {
      await this.connectCommand({
        command: "disconnect",
      });
    },
    async connectMachine() {
      await this.connectCommand({
        command: "connect",
        device_id: this.selectedMachine,
      });
    },
    async connectCommand(payload) {
      this.loading = true;
      this.showAlert = false;
      try {
        const response = await api.post("/api/connection", payload);
        console.log("Connection response: " + response);
        this.loading = false;
      } catch (err) {
        this.error = err.response.data;
        this.showAlert = true;
        this.loading = false;
      }
    },
    getExperimentsList() {
      this.loading = true;
      this.showAlert = false;
      this.$store
        .dispatch("machine/updateConnection")
        .then((data) => {
          this.loading = false;
          if (data.current.id != null) {
            this.selectedMachine = data.current.id;
          } else {
            const [firstDeviceId] = Object.keys(data.options.devices);
            this.selectedMachine = firstDeviceId;
          }
        })
        .catch((err) => {
          this.loading = false;
          this.error = err.response.data;
          this.showAlert = true;
        });
    },
    onDismissed() {
      // do something when alert is dismissed
    },
  },
  sockets: {
    changeMachineListEvent() { },
  },
};
</script>

<style scoped></style>