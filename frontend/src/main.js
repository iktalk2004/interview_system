import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

// axios.defaults.baseURL = 'http://localhost:8000/api/';  // Django API基址

app.use(ElementPlus)
app.use(router)

app.mount('#app')
