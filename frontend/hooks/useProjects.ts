import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import api from '../lib/api';

export const useProjects = () => {
    return useQuery({
        queryKey: ['projects'],
        queryFn: async () => {
            const { data } = await api.get('/projects');
            return data;
        },
    });
};

export const useProject = (projectId: string) => {
    return useQuery({
        queryKey: ['projects', projectId],
        queryFn: async () => {
            const { data } = await api.get(`/projects/${projectId}`);
            return data;
        },
        enabled: !!projectId,
    });
};

export const useProjectMetrics = (projectId: string) => {
    return useQuery({
        queryKey: ['projects', projectId, 'metrics'],
        queryFn: async () => {
            const { data } = await api.get(`/projects/${projectId}/metrics`);
            return data;
        },
        enabled: !!projectId,
    });
};

export const useCreateProject = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (projectData: { name: string; description?: string }) => {
            const { data } = await api.post('/projects', projectData);
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
            toast.success('Project structurally initiated');
        },
        onError: () => toast.error('Failed to initialize logical boundaries')
    });
};

export const useUpdateProject = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ id, data }: { id: string; data: { name?: string; description?: string } }) => {
            const response = await api.put(`/projects/${id}`, data);
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
            queryClient.invalidateQueries({ queryKey: ['projects', variables.id] });
            toast.success('Project configuration updated cleanly');
        },
        onError: () => toast.error('Failed tracking parameter overrides')
    });
};

export const useDeleteProject = (redirectOnDelete = false) => {
    const queryClient = useQueryClient();
    const router = useRouter();

    return useMutation({
        mutationFn: async (id: string) => {
            await api.delete(`/projects/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
            toast.success('Project completely obliterated implicitly tracking vectors natively.');
            if (redirectOnDelete) {
                router.push('/dashboard');
            }
        },
        onError: () => toast.error('Logical locks blocked dataset truncations.')
    });
};
