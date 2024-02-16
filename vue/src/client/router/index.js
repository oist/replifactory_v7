import { createRouter, createWebHistory } from "vue-router";

import DeviceControl from "@/client/components/DeviceControl/DeviceControl.vue";
import ExperimentTab from "@/client/components/ExperimentTab/ExperimentTab.vue";
import NgrokTab from "@/client/components/Remote/NgrokTab.vue";
import HelpTab from "@/client/components/HelpTab/HelpTab.vue";
import StatusTab from "@/client/components/StatusTab/StatusTab.vue";
import LogsTab from "@/client/components/LogsTab/LogsTab.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("@/client/components/Replifactory.vue"),
    meta: {
      // requiresAuth: true,
    },
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
        path: "/remote",
        name: "Remote",
        component: NgrokTab,
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

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem("token");
    if (token) {
      next();
    } else {
      next("/login");
    }
  } else {
    next();
  }
});

export default router;
