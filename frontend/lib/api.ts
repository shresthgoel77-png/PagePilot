import axios from 'axios';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    withCredentials: true,
});

api.interceptors.request.use(async (config) => {
    // Only attempt to get token in the browser environment
    if (typeof window !== 'undefined') {
        try {
            const token = await (window as any).Clerk?.session?.getToken();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        } catch (error) {
            console.error('Error fetching Clerk token within interceptor:', error);
        }
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

export default api;
