import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import api from '../lib/api';

export const usePdfs = (projectId: string) => {
    return useQuery({
        queryKey: ['pdfs', projectId],
        queryFn: async () => {
            const { data } = await api.get(`/projects/${projectId}/pdfs`);
            return data;
        },
        enabled: !!projectId,
    });
};

export const useUploadPdf = (projectId: string) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({ file, onProgress }: { file: File; onProgress?: (p: number) => void }) => {
            const formData = new FormData();
            formData.append('file', file);

            const { data } = await api.post(`/projects/${projectId}/pdfs`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                onUploadProgress: (progressEvent) => {
                    if (onProgress && progressEvent.total) {
                        onProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total));
                    }
                }
            });
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pdfs', projectId] });
        }
        // Notice: Removed generalized toasts enabling Dropzone logic specifically tracking unique per-file execution bounds natively generating recursive execution states isolated.
    });
};

export const useDeletePdf = (projectId: string) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (pdfId: string) => {
            await api.delete(`/projects/${projectId}/pdfs/${pdfId}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pdfs', projectId] });
            toast.success('Document vectors implicitly detached from caching securely.');
        },
        onError: () => toast.error('Filesystem logical mapping failed deletion implicitly')
    });
};
