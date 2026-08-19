import axios from 'axios';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    withCredentials: true,
});

// Request interceptor to inject Mock Auth
api.interceptors.request.use((config) => {
    if (process.env.NEXT_PUBLIC_BYPASS_CLERK === 'true') {
        config.headers.Authorization = 'Bearer MOCK_TOKEN';
    }
    return config;
});

// Response error interceptor for diagnostic visibility
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            console.error(
                `[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url} → ${error.response.status}: ${error.response.data?.detail || 'Unknown error'}`
            );
        } else if (error.request) {
            console.error(
                `[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url} → No response (network error or CORS)`
            );
        }
        return Promise.reject(error);
    }
);

export default api;
