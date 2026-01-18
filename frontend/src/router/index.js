import {createRouter, createWebHistory} from 'vue-router'
import Register from '@/components/Register.vue';
import Login from '@/components/Login.vue';
import Profile from '@/components/Profile.vue';

const routes = [
    {path: '/', redirect: '/login'},
    {path: '/register', component: Register},
    {path: '/login', component: Login},
    {path: '/profile', component: Profile},
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;
