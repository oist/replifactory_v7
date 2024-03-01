<template>
  <div class="d-flex align-items-center py-4 h-100">
    <MachineNotification />
    <main class="form-signin w-100 m-auto">
      <form v-if="!authorized" @submit.prevent="login">
        <img class="mb-4" :src="`${publicPath}favicon.svg`" alt="" width="72" height="57" />
        <h1 class="h3 mb-3 fw-normal">Please sign in</h1>

        <div class="form-floating">
          <input id="floatingInput" v-model="email" type="email" class="form-control" placeholder="Email" name="email" />
          <label for="floatingInput">Email address</label>
        </div>
        <div class="form-floating">
          <input id="floatingPassword" v-model="password" type="password" class="form-control" placeholder="Password"
            name="password" />
          <label for="floatingPassword">Password</label>
        </div>

        <div class="form-check text-start my-3">
          <input id="flexCheckDefault" class="form-check-input" type="checkbox" value="remember-me" name="remember_me" />
          <label class="form-check-label" for="flexCheckDefault">
            Remember me
          </label>
        </div>
        <button class="btn btn-primary w-100 py-2" type="submit">
          Sign in
        </button>
        <p class="mt-3 mb-3 text-body-secondary">
          <BootstrapRouterLink to="/help" class="text-decoration-none"> Help </BootstrapRouterLink>
        </p>
      </form>
      <div v-else class="m-auto">
        <p>You have already logged in.</p>
        <a href="/" class="btn btn-success">Go to home</a>
      </div>
    </main>
  </div>
</template>

<script>
import MachineNotification from "@/client/components/machine/MachineNotification.vue";
import { mapGetters } from "vuex";
import BootstrapRouterLink from "@/client/router/BootstrapRouterLink.vue";


export default {
  name: "LoginPage",
  components: {
    MachineNotification,
    BootstrapRouterLink,
  },
  data() {
    return {
      email: "",
      password: "",
      publicPath: import.meta.env.BASE_URL,
    };
  },
  computed: {
    ...mapGetters("security", ["authorized"]),
  },
  methods: {
    login() {
      this.$store
        .dispatch("security/login", {
          email: this.email,
          password: this.password,
        })
        .then(() => {
          this.$router.push(this.$route.query.next || '/');
        })
        .catch((err) => {
          if (err.response.status == 400) {

            this.$store.dispatch("notifyWarning", {
              content: err.response.data.response.errors,
            });
          } else {
            this.$store.dispatch("notifyDanger", {
              content: err.response.statusText,
            });
          }
        });
    },
  },
};
</script>

<style>
.form-signin {
  max-width: 330px;
  padding: 1rem;
}

html,
body {
  height: 100%;
}
</style>
