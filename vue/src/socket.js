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

socket.on("current", (data) => {
  store.commit("machine/updateData", data);
});

socket.on("history", (data) => {
  store.commit("machine/updateData", data);
});

socket.on("ConnectionOptionsUpdated", (options) => {
  store.commit("machine/updateConnectionOptions", options);
});

socket.on("MachineConnected", (payload) => {
  store.commit("machine/updateCurrentConnetion", payload);
});

socket.on("SendQueueUpdated", (payload) => {
  store.commit("machine/updateSendQueue", payload);
});

socket.on("CommandQueueUpdated", (payload) => {
  store.commit("machine/updateCommandQueue", payload);
});
