import { useState, useRef, useCallback } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useQueryClient, useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import api from '../lib/api';

interface ReasoningState {
    content: string;
    isStreaming: boolean;
    error: Error | null;
}

export function useReasoningStream(projectId: string) {
    const [state, setState] = useState<ReasoningState>({ content: '', isStreaming: false, error: null });
    const abortControllerRef = useRef<AbortController | null>(null);

    const executeReasoning = useCallback(async (query: string, pdfIds: string[], mode: string = "compare") => {
        if (state.isStreaming) return;

        setState({ content: '', isStreaming: true, error: null });
        abortControllerRef.current = new AbortController();

        try {
            await fetchEventSource(`http://127.0.0.1:8000/api/v1/projects/${projectId}/reason`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    query,
                    pdf_ids: pdfIds,
                    mode
                }),
                signal: abortControllerRef.current.signal,
                onmessage(event) {
                    if (event.data) {
                        try {
                            const parsed = JSON.parse(event.data);
                            if (parsed.type === 'token') {
                                setState(prev => ({ ...prev, content: prev.content + parsed.content }));
                            } else if (parsed.type === 'done') {
                                setState(prev => ({ ...prev, isStreaming: false }));
                            } else if (parsed.type === 'error') {
                                setState(prev => ({ ...prev, isStreaming: false, error: new Error(parsed.content) }));
                                toast.error(`Reasoning Fault: ${parsed.content}`);
                            }
                        } catch (e) {
                            console.error("Stream parse warning securely handled.", e);
                        }
                    }
                },
                onerror(err) {
                    setState(prev => ({ ...prev, isStreaming: false, error: err }));
                    toast.error("Critical Stream Socket disruption detected structurally.");
                    throw err;
                }
            });
        } catch (error: any) {
            setState(prev => ({ ...prev, isStreaming: false, error }));
        }
    }, [projectId, state.isStreaming]);

    const stopStream = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setState(prev => ({ ...prev, isStreaming: false }));
        }
    }, []);

    return { ...state, executeReasoning, stopStream };
}

export const useGapAnalysis = (projectId: string) => {
    return useMutation({
        mutationFn: async ({ focus_area }: { focus_area?: string }) => {
            const { data } = await api.post(`/projects/${projectId}/gaps`, { focus_area });
            return data;
        },
        onError: () => toast.error('JSON Extraction fault bounded mapping Gap bounds.')
    });
};
