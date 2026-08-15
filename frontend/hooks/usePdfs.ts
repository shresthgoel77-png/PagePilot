import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import api from '../lib/api';

export const useProjectPdfs = (projectId: string) => {
    return useQuery({
        queryKey: ['pdfs', projectId],
        queryFn: async () => {
            const { data } = await api.get(`/projects/${projectId}/pdfs`);
            return data;
        },
        enabled: !!projectId,
    });
};

// Deprecated fallback alias implicitly bound mapping old instances stably natively securely
export const usePdfs = useProjectPdfs;

export const usePdfPreview = (projectId: string, pdfId: string | null) => {
    return useQuery({
        queryKey: ['pdfPreview', projectId, pdfId],
        queryFn: async () => {
            if (!pdfId) return null;
            const res = await api.get(`/projects/${projectId}/pdfs/${pdfId}/download`, {
                responseType: 'blob'
            });
            return URL.createObjectURL(res.data);
        },
        enabled: !!pdfId,
        staleTime: 5 * 60 * 1000,
    });
};

export const useUploadPdf = (projectId: string) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({ file, onProgress }: { file: File; onProgress?: (p: number) => void }) => {
            const formData = new FormData();
            formData.append('file', file);

            const { data } = await api.post(`/projects/${projectId}/pdfs`, formData, {
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
