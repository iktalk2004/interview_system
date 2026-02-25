import {createRouter, createWebHistory} from 'vue-router'
import Register from '@/components/Register.vue';
import Login from '@/components/Login.vue';
import RegisterNew from '@/components/RegisterNew.vue';
import LoginNew from '@/components/LoginNew.vue';
import Profile from '@/components/Profile.vue';
import QuestionsList from '@/components/QuestionsList.vue'
import CategoryManager from '@/components/CategoryManager.vue'
import Practice from "@/components/Practice.vue";
import PracticeDetail from '@/components/PracticeDetail.vue'
import Recommendations from '@/components/Recommendations.vue'
import Analytics from '@/components/Analytics.vue'
import Leaderboard from '@/components/Leaderboard.vue'
import ScoringHistory from '@/components/ScoringHistory.vue'
import Dashboard from '@/components/Dashboard.vue'
import CodePractice from '@/components/CodePractice.vue'
import CodePracticeDetail from '@/components/CodePracticeDetail.vue'

const routes = [
    {path: '/', redirect: '/recommendations'},
    {path: '/register', component: Register, meta: {requiresAuth: false}, name: 'Register'},
    {path: '/login', component: Login, meta: {requiresAuth: false}, name: 'Login'},
    {path: '/register-new', component: RegisterNew, meta: {requiresAuth: false}, name: 'RegisterNew'},
    {path: '/login-new', component: LoginNew, meta: {requiresAuth: false}, name: 'LoginNew'},
    {path: '/profile', component: Profile, meta: {requiresAuth: true}, name: 'Profile'},
    {path: '/questions', component: QuestionsList, meta: {requiresAuth: true}, name: 'QuestionsList'},
    {path: '/categories', component: CategoryManager, meta: {requiresAuth: true}, name: 'CategoryManager'},
    {path: '/practice', component: Practice, meta: {requiresAuth: true}, name: 'Practice'},
    {path: '/practice/:id', component: PracticeDetail, meta: {requiresAuth: true}, name: 'PracticeDetail'},
    {path: '/recommendations', component: Recommendations, meta: {requiresAuth: true}, name: 'Recommendations'},
    {path: '/analytics', component: Analytics, meta: {requiresAuth: true}, name: 'Analytics'},
    {path: '/leaderboard', component: Leaderboard, meta: {requiresAuth: true}, name: 'Leaderboard'},
    {path: '/scoring-history', component: ScoringHistory, meta: {requiresAuth: true}, name: 'ScoringHistory'},
    {path: '/dashboard', component: Dashboard, meta: {requiresAuth: true, requiresAdmin: true}, name: 'Dashboard'},
    {path: '/code-practice', component: CodePractice, meta: {requiresAuth: true}, name: 'CodePractice'},
    {path: '/code-practice/:id', component: CodePracticeDetail, meta: {requiresAuth: true}, name: 'CodePracticeDetail'}
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

// 全局前置守卫
router.beforeEach((to, from, next) => {
    const isAuthenticated = !!localStorage.getItem('access_token');
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    const isAdmin = user && user.is_staff;

    if (to.meta.requiresAuth && !isAuthenticated) {
        // 跳转到登录页面, 并带上当前页面的路径，以便登录后返回
        next({
            path: '/login',
            query: {redirect: to.fullPath}
        });
    } else if (to.meta.requiresAdmin && !isAdmin) {
        // 需要管理员权限但用户不是管理员
        next('/recommendations');
    } else {
        // 如果已登录有token，正常放行
        next();
    }
});

export default router;
