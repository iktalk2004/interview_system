import {createRouter, createWebHistory} from 'vue-router'
import Register from '@/components/Register.vue';
import Login from '@/components/Login.vue';
import Profile from '@/components/Profile.vue';

const routes = [
    {path: '/', redirect: '/profile'},
    {path: '/register', component: Register},
    {path: '/login', component: Login},
    {path: '/profile', component: Profile, meta: {requiresAuth: true}},
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

// 全局前置守卫
router.beforeEach((to, from, next) => {
    const isAuthenticated = !!localStorage.getItem('access_token');

    if (to.meta.requiresAuth && !isAuthenticated) {
        // 跳转到登录页面, 并带上当前页面的路径，以便登录后返回
        next({
            path: '/login',
            query: {redirect: to.fullPath}
        });
    } else {
        // 如果已登录有token，正常放行
        next();
    }
});

export default router;
