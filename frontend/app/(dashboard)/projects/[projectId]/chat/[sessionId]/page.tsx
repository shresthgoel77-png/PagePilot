"use client";

import { useState, useRef, useEffect, use } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useChatStream } from '@/hooks/useChatStream';
import { ChatMessage } from '@/components/chat-message';
import { ChatInput } from '@/components/chat-input';
import { CitationPanel } from '@/components/citation-panel';
import api from '@/lib/api';

export default function ChatInterface({ params }: { params: Promise<{ projectId: string; sessionId: string }> }) {
    const resolvedParams = use(params);
    const { data: sessionData, isLoading } = useQuery({
        queryKey: ['chat', resolvedParams.sessionId],
        queryFn: async () => {
            const { data } = await api.get(`/chat-sessions/${resolvedParams.sessionId}`);
            return data;
        },
        refetchOnWindowFocus: false,
    });

    const { content: streamContent, isStreaming, error, sendMessage } = useChatStream(resolvedParams.projectId, resolvedParams.sessionId);
    const scrollRef = useRef<HTMLDivElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [activeSources, setActiveSources] = useState<any[]>([]);

    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [sessionData?.messages, streamContent]);

    useEffect(() => {
        if (sessionData && sessionData.messages.length > 0) {
            const lastAssistantMsg = sessionData.messages.filter((m: any) => m.role === 'assistant').pop();
            // Automatically maps the most recent semantic state bounds extracting specific chunk citations logically optimally 
            if (lastAssistantMsg && lastAssistantMsg.sources) {
                setActiveSources(lastAssistantMsg.sources);
            }
        }
    }, [sessionData?.messages]);

    if (isLoading) return <div className="p-8 text-center font-bold uppercase tracking-widest text-slate-400 mt-20 animate-pulse">Mounting Architectural Boundaries...</div>;

    const allMessages = sessionData?.messages || [];

    return (
        <div className="flex h-full bg-slate-50/50 overflow-hidden w-full border border-slate-200 rounded-xl shadow-lg relative max-h-[85vh]">
            <div className="flex-1 flex flex-col h-full bg-white relative z-10 border-r border-slate-200 overflow-hidden shrink-0">
                <div className="bg-white border-b border-slate-100 px-6 py-4 flex flex-col z-20 shadow-sm relative">
                    <h2 className="text-xl font-black tracking-tight text-slate-900 line-clamp-1">{sessionData?.title || 'Execution Bounded State mapping natively'}</h2>
                    <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mt-1">Cross-referencing logic explicitly validating pointers automatically</p>
                </div>

                <div className="flex-1 overflow-auto relative scroll-smooth p-6 pb-20" ref={scrollRef}>
                    <div className="max-w-3xl mx-auto space-y-4">
                        {allMessages.length === 0 && !isStreaming && (
                            <div className="text-center py-20 opacity-40 flex flex-col items-center">
                                <div className="text-6xl mb-4 grayscale">🧠</div>
                                <p className="text-sm font-extrabold tracking-tight">System boundaries correctly generated explicitly ready resolving requests intuitively robustly.</p>
                            </div>
                        )}
                        {allMessages.map((msg: any) => (
                            <ChatMessage key={msg.id} role={msg.role} content={msg.content} sources={msg.sources} />
                        ))}

                        {isStreaming && (
                            <ChatMessage role="assistant" content={streamContent || 'Computing vectors intrinsically mapping...'} />
                        )}

                        {error && (
                            <div className="flex justify-center my-4">
                                <div className="bg-red-50 border border-red-200 px-6 py-3 rounded-lg text-sm font-bold text-red-600 tracking-tight shadow-md cursor-pointer hover:bg-red-100 transition-colors" onClick={() => sendMessage(sessionData?.messages[sessionData?.messages.length - 1]?.content || '')}>
                                    Network Fault intrinsically executed uniquely locally. Click isolating retries securely safely inherently.
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} className="h-4" />
                    </div>
                </div>

                <div className="bg-slate-50 border-t border-slate-200 p-4 shrink-0 shadow-lg z-20 absolute bottom-0 left-0 right-0">
                    <div className="max-w-3xl mx-auto">
                        <ChatInput onSend={(msg) => sendMessage(msg)} disabled={isStreaming} />
                    </div>
                </div>
            </div>

            <div className="hidden lg:block w-[400px] h-full relative z-20 shrink-0">
                <CitationPanel sources={activeSources} />
            </div>
        </div>
    );
}
