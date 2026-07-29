import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import api from '../lib/api';
import { useAuthStore } from '../stores/authStore';

export const useLogin = () => {
    const setUser = useAuthStore((state) => state.setUser);
    const router = useRouter();

    return useMutation({
        mutationFn: async (credentials: Record<string, string>) => {
            const response = await api.post('/auth/login', credentials);
            const token = response.data.access_token;

            const meResponse = await api.get('/auth/me', {
                headers: { Authorization: `Bearer ${token}` }
            });
            return { user: meResponse.data, token };
        },
        onSuccess: (data) => {
            setUser(data.user, data.token);
            toast.success('Login successful!');
            router.push('/dashboard');
        },
        onError: (error: any) => {
            const message = error.response?.data?.detail || 'Invalid login credentials';
            toast.error(message);
        }
    });
};

export const useRegister = () => {
    const router = useRouter();

    return useMutation({
        mutationFn: async (userData: Record<string, string>) => {
            const response = await api.post('/auth/register', userData);
            return response.data;
        },
        onSuccess: () => {
            toast.success('Registration successful! Please login.');
            router.push('/login');
        },
        onError: (error: any) => {
            const message = error.response?.data?.detail || 'Registration failed structurally natively.';
            toast.error(message);
        }
    });
};
