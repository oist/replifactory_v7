import { createRouter, createWebHistory } from "vue-router";

import store from "@/client/store/index.js";

const routes = [
  {
    path: "/",
    name: "Index",
    component: () => import("@/client/pages/BiofactoryPage.vue"),
    beforeEnter: requireAuth,
    children: [
      {
        path: "/home",
        alias: "/",
        name: "Home",
        component: () => import("@/client/pages/biofactory/HomeSection.vue"),
      },
      {
        path: "/machine",
        name: "Machine",
        component: () => import("@/client/components/DeviceControl/DeviceControl.vue"),
      },
      {
        path: "/experiments",
        name: "Experiments",
        component: () => import("@/client/pages/biofactory/ExperimentSection.vue"),
        children: [
          {
            path: "/experiments/new",
            alias: "/experiments/",
            name: "NewExperiment",
            component: () => import("@/client/pages/biofactory/experiments/NewExperimentForm.vue"),
          },
          {
            path: "/experiments/:id",
            name: "ExperimentDetail",
            component: () => import("@/client/pages/biofactory/experiments/ExperimentDetail.vue"),
          }
        ],
      },
      {
        path: "/maintance",
        name: "Maintance",
        component: () => import("@/client/pages/biofactory/MaintanceSection.vue"),
      },
      {
        path: "/archive",
        name: "Archive",
        component: () => import("@/client/components/ArchiveTab/ArchiveTab.vue"),
      },
      {
        path: "/status",
        name: "Status",
        component: () => import("@/client/components/StatusTab/StatusTab.vue"),
      },
      {
        path: "/logs",
        name: "Logs",
        component: () => import("@/client/components/LogsTab/LogsTab.vue"),
      },
      {
        path: "/help",
        name: "Help",
        component: () => import("@/client/components/HelpTab/HelpTab.vue"),
      },
    ],
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/client/pages/LoginPage.vue"),
  },
  {
    path: "/man",
    name: "Manual",
    component: () => import("@/client/components/HelpTab/HelpTab.vue"),
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
