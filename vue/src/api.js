// api.js
import axios from "axios";

let baseURL = window.location.origin;

// set the cookie and header names
axios.defaults.xsrfCookieName = "XSRF-TOKEN";
axios.defaults.xsrfHeaderName = "X-CSRF-Token";

const api = axios.create({
  baseURL: baseURL,
});

export default api;
