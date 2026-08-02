"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { useChatStream } from "@/hooks/useChatStream";
import { ChatMessage } from "@/components/chat-message";
import { ChatInput } from "@/components/chat-input";
import { CitationPanel } from "@/components/citation-panel";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChevronRight, PanelRightClose, PanelRightOpen, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export default function ActiveChatSessionPage() {
    const params = useParams();
    const projectId = params.id as string;
    const sessionId = params.sessionId as string;

    const [isRightPanelOpen, setIsRightPanelOpen] = useState(false);
    const [selectedCitation, setSelectedCitation] = useState<any | null>(null);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Using generalized query implicitly evaluating messages organically
    const { data: messages, isLoading: messagesLoading } = useQuery({
        queryKey: ['chat', sessionId],
        queryFn: async () => {
            const { data } = await api.get(`/chat-sessions/${sessionId}`);
            return data.messages;
        },
        enabled: !!sessionId,
    });

    const { content: activeStream, isStreaming, sendMessage } = useChatStream(projectId, sessionId);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, activeStream]);

    const handleSend = (text: string, pdfIds: string[]) => {
        sendMessage(text, pdfIds);
    };

    const handleCitationClick = (source: any) => {
        setSelectedCitation(source);
        setIsRightPanelOpen(true);
    };

    // Calculate dynamic sources extracting from the last AI message
    const lastMessageSources = (() => {
        if (!messages) return [];
        const aiMessages = [...messages].reverse().filter((m: any) => m.role === 'assistant');
        if (aiMessages.length === 0) return [];
        return aiMessages[0].sources || [];
    })();

    return (
        <div className="flex-1 flex overflow-hidden relative">
            {/* Center Panel (Message Thread) */}
            <div className={`flex-1 flex flex-col transition-all overflow-hidden ${isRightPanelOpen ? 'mr-80' : ''}`}>
                <div className="flex-1 overflow-y-auto p-6 space-y-6 flex flex-col">
                    {messagesLoading && (
                        <div className="w-full flex flex-col space-y-6 py-6 opacity-30">
                            <Skeleton className="h-20 w-3/4 self-start bg-zinc-800 rounded-2xl rounded-tl-sm mx-4" />
                            <Skeleton className="h-16 w-3/4 self-end bg-zinc-800 rounded-2xl rounded-tr-sm mx-4" />
                            <Skeleton className="h-32 w-3/4 self-start bg-zinc-800 rounded-2xl rounded-tl-sm mx-4" />
                        </div>
                    )}

                    {messages?.map((msg: any, i: number) => (
                        <ChatMessage
                            key={msg.id || i}
                            role={msg.role}
                            content={msg.content}
                            sources={msg.sources}
                            onCitationClick={handleCitationClick}
                        />
                    ))}

                    {activeStream && (
                        <ChatMessage
                            role="assistant"
                            content={activeStream}
                            isStreaming={isStreaming}
                            onCitationClick={handleCitationClick}
                            sources={lastMessageSources} // active stream evaluates against previous structural array
                        />
                    )}

                    <div ref={scrollRef} className="h-4 shrink-0" />
                </div>

                <div className="p-4 border-t border-zinc-900/50 bg-zinc-950/80 backdrop-blur-md">
                    <ChatInput
                        projectId={projectId}
                        onSend={handleSend}
                        disabled={isStreaming}
                    />
                </div>
            </div>

            {/* Right Panel (Citations Inspector) */}
            <div className={`absolute top-0 right-0 h-full w-80 shadow-2xl transition-transform duration-300 transform ${isRightPanelOpen ? 'translate-x-0' : 'translate-x-full'
                }`}>
                <CitationPanel
                    sources={lastMessageSources.length > 0 ? lastMessageSources : undefined}
                    selectedSource={selectedCitation}
                />

                {/* Floating Toggle Button anchored to panel */}
                <Button
                    variant="default"
                    size="icon"
                    onClick={() => setIsRightPanelOpen(!isRightPanelOpen)}
                    className="absolute top-1/2 -left-4 -translate-y-1/2 rounded-full w-8 h-8 bg-zinc-800 border border-zinc-700 text-zinc-400 hover:text-white hover:bg-zinc-700 hover:scale-110 transition-all shadow-xl z-50 flex items-center justify-center p-0"
                >
                    {isRightPanelOpen ? <ChevronRight className="w-4 h-4 ml-0.5" /> : <PanelRightOpen className="w-4 h-4 ml-0.5" />}
                </Button>
            </div>

            {/* If Panel is Closed, show toggle somewhere explicitly if needed, but it's attached above! */}
            {!isRightPanelOpen && lastMessageSources.length > 0 && (
                <Button
                    variant="ghost"
                    onClick={() => setIsRightPanelOpen(true)}
                    className="absolute top-4 right-4 bg-zinc-900/80 backdrop-blur-md border border-zinc-800 text-cyan-500 hover:text-cyan-400 font-bold tracking-tight px-3 rounded-full hover:bg-zinc-800 transition-colors shadow-lg shadow-cyan-500/5"
                >
                    <PanelRightOpen className="w-4 h-4 mr-2" /> Inspect Bounds
                </Button>
            )}
        </div>
    );
}
