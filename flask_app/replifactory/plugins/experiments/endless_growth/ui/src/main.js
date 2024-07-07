import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

import * as icons from "@coreui/icons"
import "bootstrap/dist/css/bootstrap.css"
import "bootstrap-vue-next/dist/bootstrap-vue-next.css"

createApp(App)
.provide("icons", icons)
.mount('#app')
