import { useState, useRef, useCallback } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { useAuthStore } from '../stores/authStore';

interface StreamState {
    content: string;
    isStreaming: boolean;
    error: Error | null;
}

export function useChatStream(projectId: string, sessionId: string) {
    const queryClient = useQueryClient();
    const [state, setState] = useState<StreamState>({ content: '', isStreaming: false, error: null });
    const abortControllerRef = useRef<AbortController | null>(null);

    const sendMessage = useCallback(async (message: string, pdfIds?: string[]) => {
        if (state.isStreaming) return;

        setState({ content: '', isStreaming: true, error: null });
        abortControllerRef.current = new AbortController();

        try {
            // Initiate explicit SSE boundaries natively avoiding fetch latency uniquely 
            await fetchEventSource(`http://localhost:8000/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(useAuthStore.getState().token
                        ? { 'Authorization': `Bearer ${useAuthStore.getState().token}` }
                        : localStorage.getItem('guest_session_id')
                            ? { 'X-Guest-Session-Id': localStorage.getItem('guest_session_id') as string }
                            : {})
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    project_id: projectId,
                    message,
                    pdf_ids: pdfIds
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
                                queryClient.invalidateQueries({ queryKey: ['chat', sessionId] });
                            } else if (parsed.type === 'error') {
                                setState(prev => ({ ...prev, isStreaming: false, error: new Error(parsed.content) }));
                                toast.error(`Streaming explicitly blocked: ${parsed.content}`);
                            }
                        } catch (e) {
                            console.error("Stream parse fault efficiently safely ignored intrinsically:", e);
                        }
                    }
                },
                onerror(err) {
                    setState(prev => ({ ...prev, isStreaming: false, error: err }));
                    toast.error("Critical Stream Socket disruption detected.");
                    throw err;
                }
            });
        } catch (error: any) {
            console.error("Fetch Event explicit hook aborted gracefully inherently securely mapped:", error);
            setState(prev => ({ ...prev, isStreaming: false, error }));
        }
    }, [projectId, sessionId, state.isStreaming, queryClient]);

    const stopStream = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setState(prev => ({ ...prev, isStreaming: false }));
        }
    }, []);

    return { ...state, sendMessage, stopStream };
}
