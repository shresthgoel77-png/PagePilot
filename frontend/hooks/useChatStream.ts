import { useState, useRef, useCallback } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { useAuth } from '@clerk/nextjs';
interface StreamState {
    content: string;
    isStreaming: boolean;
    currentStatus: 'idle' | 'retrieving' | 'generating';
    error: Error | null;
    verifications: any[] | null;
}

export function useChatStream(projectId: string, sessionId: string) {
    const { getToken } = useAuth();
    const queryClient = useQueryClient();
    const [state, setState] = useState<StreamState>({ content: '', isStreaming: false, currentStatus: 'idle', error: null, verifications: null });
    const abortControllerRef = useRef<AbortController | null>(null);

    const sendMessage = useCallback(async (message: string, pdfIds?: string[]) => {
        if (state.isStreaming) return;

        setState({ content: '', isStreaming: true, currentStatus: 'idle', error: null, verifications: null });
        abortControllerRef.current = new AbortController();

        try {
            const token = await getToken();
            await fetchEventSource(`http://localhost:8000/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(process.env.NEXT_PUBLIC_BYPASS_CLERK === 'true' ? { 'Authorization': 'Bearer MOCK_TOKEN' } : (token ? { 'Authorization': `Bearer ${token}` } : {}))
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
                            if (parsed.type === 'status') {
                                setState(prev => ({ ...prev, currentStatus: parsed.content }));
                            } else if (parsed.type === 'token') {
                                setState(prev => ({ ...prev, content: prev.content + parsed.content }));
                            } else if (parsed.type === 'done') {
                                setState(prev => ({ ...prev, isStreaming: false, currentStatus: 'idle' }));
                                queryClient.invalidateQueries({ queryKey: ['chat', sessionId] });
                            } else if (parsed.type === 'error') {
                                setState(prev => ({ ...prev, isStreaming: false, currentStatus: 'idle', error: new Error(parsed.content) }));
                                toast.error(`Streaming explicitly blocked: ${parsed.content}`);
                            } else if (parsed.type === 'verification') {
                                setState(prev => ({ ...prev, verifications: parsed.content }));
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
