<template>
    <div class="d-flex align-items-center py-4 h-100">
        <main class="form-signin w-100 m-auto">
            <form>
                <img class="mb-4" :src="`${publicPath}favicon.svg`" alt="" width="72" height="57">
                <h1 class="h3 mb-3 fw-normal">Please sign in</h1>

                <div class="form-floating">
                    <input type="email" v-model="email" class="form-control" id="floatingInput" placeholder="Email">
                    <label for="floatingInput">Email address</label>
                </div>
                <div class="form-floating">
                    <input type="password" v-model="password" class="form-control" id="floatingPassword"
                        placeholder="Password">
                    <label for="floatingPassword">Password</label>
                </div>

                <div class="form-check text-start my-3">
                    <input class="form-check-input" type="checkbox" value="remember-me" id="flexCheckDefault">
                    <label class="form-check-label" for="flexCheckDefault">
                        Remember me
                    </label>
                </div>
                <button class="btn btn-primary w-100 py-2" type="submit" @click="login">Sign in</button>
                <p class="mt-3 mb-3 text-body-secondary"><a href="#">Help</a></p>
            </form>
        </main>
    </div>
</template>

<script>
export default {
    name: "LoginPage",
    data() {
        return {
            email: '',
            password: '',
            publicPath: import.meta.env.BASE_URL,
        };
    },
    methods: {
        login() {
            // Send login request and handle authentication token
            // Store token in local storage
        }
    }
};
</script>

<style>
.form-signin {
    max-width: 330px;
    padding: 1rem;
}
html, body {
    height: 100%;
}
</style>