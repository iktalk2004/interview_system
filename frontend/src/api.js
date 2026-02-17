// 这个文件是封装axios的，用于发送请求，连接Django的
import axios from 'axios'


const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1/',
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
    },
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

// 拦截器：添加token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token');  // access_token是Django返回的
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// 响应拦截器：处理token过期
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;

        if (error.response.status === 401) {
            if (!originalRequest._retry) {
                originalRequest._retry = true;  // 防止重复刷新,无限循环

                if (isRefreshing) {
                    // 如果正在刷新token，等待刷新完成
                    return new Promise((resolve, reject) => {
                        failedQueue.push({resolve, reject});
                    }).then(token => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return api(originalRequest);
                    }).catch(err => {
                        // 等待过程中发生错误，清理token并跳转
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('refresh_token');
                        window.location.href = '/login';
                        return Promise.reject(err);
                    })
                }

                // 状态修改为刷新中
                isRefreshing = true;

                const refresh_token = localStorage.getItem('refresh_token');

                if (!refresh_token) {
                    // 没有refresh_token，直接踢登录
                    localStorage.removeItem('access_token');
                    window.location.href = '/login';
                    return Promise.reject(error);
                }

                try {
                    const response = await axios.post(
                        'http://localhost:8000/api/v1/token/refresh', {
                            refresh: refresh_token
                        });

                    const newAccessToken = response.data.access;
                    localStorage.setItem('access_token', newAccessToken);

                    processQueue(null, newAccessToken);  // 更新队列中的所有请求

                    originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;  // 重新发送请求，使用新的token

                    return api(originalRequest);
                } catch (refreshError) {
                    // 刷新失败，清除token，大概率是refresh_token也过期了
                    processQueue(refreshError, null)
                    localStorage.removeItem('access_token')
                    localStorage.removeItem('refresh_token')

                    // 提示用户并跳转
                    if (typeof window !== 'undefined' && typeof alert !== 'undefined') {
                        alert('登录已过期，请重新登录');
                    }

                    window.location.href = '/login';
                    return Promise.reject(refreshError);
                } finally {
                    isRefreshing = false;
                }
            }
        }

        return Promise.reject(error);
    }
)

// 用户认证相关
export const authAPI = {
    login: (username, password) => api.post('users/login/', { username, password }),
    register: (username, email, password) => api.post('users/register/', { username, email, password }),
    logout: () => api.post('users/logout/'),
    getUserProfile: () => api.get('users/profile/'),
    updateUserProfile: (data) => api.put('users/profile/', data)
};

// 题目相关
export const questionsAPI = {
    getQuestions: (params) => api.get('questions/', { params }),
    getQuestion: (id) => api.get(`questions/${id}/`),
    createQuestion: (data) => api.post('questions/', data),
    updateQuestion: (id, data) => api.put(`questions/${id}/`, data),
    deleteQuestion: (id) => api.delete(`questions/${id}/`)
};

// 分类相关
export const categoriesAPI = {
    getCategories: () => api.get('categories/'),
    getCategory: (id) => api.get(`categories/${id}/`),
    createCategory: (data) => api.post('categories/', data),
    updateCategory: (id, data) => api.put(`categories/${id}/`, data),
    deleteCategory: (id) => api.delete(`categories/${id}/`)
};

// 练习相关
export const practiceAPI = {
    getInteractions: (params) => api.get('practice/interactions/', { params }),
    getInteraction: (id) => api.get(`practice/interactions/${id}/`),
    createInteraction: (data) => api.post('practice/interactions/', data),
    updateInteraction: (id, data) => api.put(`practice/interactions/${id}/`, data),
    deleteInteraction: (id) => api.delete(`practice/interactions/${id}/`),
    getHistory: () => api.get('practice/interactions/history/'),
    toggleFavorite: (id) => api.post(`practice/interactions/${id}/favorite/`),
    resetInteraction: (id) => api.post(`practice/interactions/${id}/reset_interaction/`),
    scoreByEmbedding: (id) => api.post(`practice/interactions/${id}/embedding_score/`),
    scoreByDeepSeek: (id) => api.post(`practice/interactions/${id}/deepseek_score/`)
};

// 推荐系统相关
export const recommenderAPI = {
    getRecommendations: (params) => api.get('recommender/recommendations/', { params }),
    markAsViewed: (id) => api.post(`recommender/recommendations/${id}/viewed/`),
    markAsAnswered: (id) => api.post(`recommender/recommendations/${id}/answered/`),
    getUserPreferences: () => api.get('recommender/preferences/'),
    updateUserPreferences: () => api.post('recommender/preferences/update/')
};

// 数据分析相关
export const analyticsAPI = {
    getDashboard: () => api.get('analytics/dashboard/overview/'),
    getDailyStats: (params) => api.get('analytics/daily-stats/', { params }),
    getPerformanceTrend: (params) => api.get('analytics/performance-trends/', { params }),
    getScoreDistribution: () => api.get('analytics/score-distribution/'),
    getLeaderboard: () => api.get('analytics/dashboard/leaderboard/')
};

// 评分系统相关
export const scoringAPI = {
    getScores: (params) => api.get('scoring/scoring/', { params }),
    getScore: (id) => api.get(`scoring/scoring/${id}/`),
    createScore: (data) => api.post('scoring/scoring/', data),
    scoreInteraction: (data) => api.post('scoring/scoring/score_interaction/', data),
    getLatestScores: (params) => api.get('scoring/scoring/get_latest_scores/', { params })
};

export default api;
