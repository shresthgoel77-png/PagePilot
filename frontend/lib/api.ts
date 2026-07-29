import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

// Initialize HTTP connection targeting generic localhost default mappings 
const api = axios.create({
    baseURL: 'http://localhost:8000',
    withCredentials: true,
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Standard middleware interception for handling dead tokens or expired sessions across all API boundaries cleanly
        if (error.response && error.response.status === 401) {
            useAuthStore.getState().logout();
            if (typeof window !== 'undefined') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default api;
