import { io } from "socket.io-client";
import store from "@/client/store";

export const socket = io("/machine");

socket.on("connect", () => {
  store.commit("setBackendConnected", true);
});

socket.on("disconnect", () => {
  store.commit("setBackendConnected", false);
});

socket.on("connect_error", (error) => {
  store.commit("setBackendConnected", false);
  console.log("Connection error:", error);
});

socket.on("reconnect", (attemptNumber) => {
  console.log(`Reconnected after ${attemptNumber} attempts`);
});

socket.on("ConnectionOptionsUpdated", (options) => {
  store.commit("machine/updateConnectionOptions", options);
});

socket.on("MachineStateChanged", (payload) => {
  store.commit("machine/updateMachineState", {
    id: payload.state_id,
    string: payload.state_string,
  });
});

socket.on("MachineConnected", (payload) => {
  store.commit("machine/updateCurrentConnetion", payload);
});

socket.on("DevicesStateChanged", (payload) => {
  store.commit("machine/updateDevices", payload);
});
