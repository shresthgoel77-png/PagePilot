import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';

export const useChatSessions = (projectId: string) => {
    return useQuery({
        queryKey: ['chat-sessions', projectId],
        queryFn: async () => {
            const { data } = await api.get(`/chat-sessions`, { params: { project_id: projectId } });
            return data;
        },
        enabled: !!projectId
    });
};

export const useCreateSession = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ projectId, title }: { projectId: string; title?: string }) => {
            const { data } = await api.post(`/chat-sessions`, { project_id: projectId, title });
            return data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['chat-sessions', data.project_id] });
        }
    });
};

export const useUpdateSessionTitle = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ sessionId, title }: { sessionId: string; title: string }) => {
            const { data } = await api.put(`/chat-sessions/${sessionId}`, { title });
            return data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['chat-sessions', data.project_id] });
        }
    });
};

export const useDeleteSession = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ sessionId, projectId }: { sessionId: string, projectId: string }) => {
            await api.delete(`/chat-sessions/${sessionId}`);
            return { projectId };
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['chat-sessions', data.projectId] });
        }
    });
};
