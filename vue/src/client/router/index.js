import { createRouter, createWebHistory } from "vue-router";

import DeviceControl from "@/client/components/DeviceControl/DeviceControl.vue";
import ExperimentTab from "@/client/components/ExperimentTab/ExperimentTab.vue";
import HelpTab from "@/client/components/HelpTab/HelpTab.vue";
import StatusTab from "@/client/components/StatusTab/StatusTab.vue";
import LogsTab from "@/client/components/LogsTab/LogsTab.vue";
import store from "@/client/store/index.js";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("@/client/components/Replifactory.vue"),
    beforeEnter: requireAuth,
    children: [
      {
        path: "/",
        alias: "/device",
        name: "Device",
        component: DeviceControl,
      },
      {
        path: "/experiment",
        name: "Experiment",
        component: ExperimentTab,
      },
      {
        path: "/status",
        name: "Status",
        component: StatusTab,
      },
      {
        path: "/logs",
        name: "Logs",
        component: LogsTab,
      },
    ],
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/client/components/Login.vue"),
  },
  {
    path: "/help",
    name: "Help",
    component: HelpTab,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

store.dispatch("security/verify");

// define a route guard function
function requireAuth(to, from, next) {
  store
    .dispatch("security/verify")
    .then((response) => {
      // if the session id is valid, allow the user to access the route
      if (response.status === 200) {
        next();
      } else {
        // if the session id is invalid, redirect the user to the login page
        next("/login");
      }
    })
    .catch((err) => {
      // handle any errors
      console.error(err);
      next("/login");
    });
}

export default router;
