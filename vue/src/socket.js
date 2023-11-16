import { reactive } from "vue";
import { io } from "socket.io-client";
import store from "@/client/store";
export const state = reactive({
  machine: {
    state_id: 0,
    state_string: "Unknown",
  },
  connected: false,
  usbDeviceDisconnected: [],
  connectionOptions: {},
  currentConnection: {
    devices: {},
  },
});

// export const socket = io(`${window.location.origin}/socket.io/machine`);
export const socket = io("/machine");

socket.on("connect", () => {
  state.connected = true;
});

socket.on("disconnect", () => {
  state.connected = false;
});

socket.on('connect_error', (error) => {
  state.connected = false;
  console.log('Connection error:', error);
});

socket.on('reconnect', (attemptNumber) => {
  console.log(`Reconnected after ${attemptNumber} attempts`);
});

socket.on("ConnectionOptionsUpdated", (options) => {
  store.commit("machine/updateConnectionOptions", options);
});
socket.on("MachineStateChanged", (payload) => {
  state.machine.state_id = payload.state_id
  state.machine.state_string = payload.state_string
});
socket.on("MachineConnected", (payload) => {
  store.commit("machine/updateCurrentConnetion", payload)
})