// api.js
import axios from "axios";

let baseURL = window.location.origin + "/api";

const api = axios.create({
  baseURL: baseURL,
});

export default api;
