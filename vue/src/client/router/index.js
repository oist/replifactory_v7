import { createRouter, createWebHistory } from "vue-router";

import DeviceControl from "@/client/components/DeviceControl/DeviceControl";
import ExperimentTab from "@/client/components/ExperimentTab/ExperimentTab";
import NgrokTab from "@/client/components/Remote/NgrokTab";
import HelpTab from "@/client/components/HelpTab/HelpTab";
import StatusTab from "@/client/components/StatusTab/StatusTab";
import LogsTab from "@/client/components/LogsTab/LogsTab";

const routes = [
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
    path: "/help",
    name: "Help",
    component: HelpTab,
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
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
