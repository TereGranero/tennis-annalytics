import { createApp } from "vue"
import App from "./App.vue"
import router from "./router"
import '@fortawesome/fontawesome-free/css/all.min.css'

// sudo npm install bootstrap
import 'bootstrap/dist/css/bootstrap.css'



// Create application
const app= createApp(App)

// Use router
app.use(router)

// Mount application
app.mount("#app")
