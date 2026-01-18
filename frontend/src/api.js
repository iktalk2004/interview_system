import axios from 'axios'


const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});


// 拦截器：添加token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token');  // access_token是Django返回的
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;
