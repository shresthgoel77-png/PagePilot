import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

let guestId = typeof window !== 'undefined' ? localStorage.getItem('guest_session_id') : null;
if (!guestId && typeof window !== 'undefined') {
    guestId = crypto.randomUUID();
    localStorage.setItem('guest_session_id', guestId);
}

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    withCredentials: true,
});

api.interceptors.request.use((config) => {
    const token = useAuthStore.getState().token;
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    } else if (guestId) {
        config.headers['X-Guest-Session-Id'] = guestId;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Standard middleware interception for handling dead tokens or expired sessions across all API boundaries cleanly
        if (error.response && error.response.status === 401) {
            useAuthStore.getState().logout();
            // Removed automatic redirect to allow guest workflow to bypass forced login constraints
        }
        return Promise.reject(error);
    }
);

export default api;
