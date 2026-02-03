import {createRouter, createWebHistory} from 'vue-router'
import Register from '@/components/Register.vue';
import Login from '@/components/Login.vue';
import Profile from '@/components/Profile.vue';
import QuestionsList from '@/components/QuestionsList.vue'
import CategoryManager from '@/components/CategoryManager.vue'
import Practice from "@/components/Practice.vue";
import PracticeDetail from '@/components/PracticeDetail.vue'
import Recommendations from '@/components/Recommendations.vue'
import Analytics from '@/components/Analytics.vue'
import Leaderboard from '@/components/Leaderboard.vue'
import ScoringHistory from '@/components/ScoringHistory.vue'

const routes = [
    {path: '/', redirect: '/recommendations'},
    {path: '/register', component: Register, meta: {requiresAuth: false}, name: 'Register'},
    {path: '/login', component: Login, meta: {requiresAuth: false}, name: 'Login'},
    {path: '/profile', component: Profile, meta: {requiresAuth: true}, name: 'Profile'},
    {path: '/questions', component: QuestionsList, meta: {requiresAuth: true}, name: 'QuestionsList'},
    {path: '/categories', component: CategoryManager, meta: {requiresAuth: true}, name: 'CategoryManager'},
    {path: '/practice', component: Practice, meta: {requiresAuth: true}, name: 'Practice'},
    {path: '/practice/:id', component: PracticeDetail, meta: {requiresAuth: true}, name: 'PracticeDetail'},
    {path: '/recommendations', component: Recommendations, meta: {requiresAuth: true}, name: 'Recommendations'},
    {path: '/analytics', component: Analytics, meta: {requiresAuth: true}, name: 'Analytics'},
    {path: '/leaderboard', component: Leaderboard, meta: {requiresAuth: true}, name: 'Leaderboard'},
    {path: '/scoring-history', component: ScoringHistory, meta: {requiresAuth: true}, name: 'ScoringHistory'}
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
