import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

const app = createApp(App)

// axios.defaults.baseURL = 'http://localhost:8000/api/';  // Django API基址

app.use(router)

app.mount('#app')
