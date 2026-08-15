"use client";

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { formatDistanceToNow } from 'date-fns';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { useChatSessions, useUpdateSessionTitle, useDeleteSession, useCreateSession } from '@/hooks/useChatSessions';
import { Edit2, Trash2, Plus, MessageSquare, Loader2 } from 'lucide-react';


export function ChatSidebar({ projectId }: { projectId: string }) {
    const { data: sessions, isLoading } = useChatSessions(projectId);
    const { mutate: updateTitle } = useUpdateSessionTitle();
    const { mutate: deleteSession } = useDeleteSession();
    const { mutate: createSession, isPending: isCreating } = useCreateSession();
    const pathname = usePathname();
    const router = useRouter();

    const [editingId, setEditingId] = useState<string | null>(null);
    const [editValue, setEditValue] = useState("");

    const activeSessionId = pathname.split('/').pop();
    const isNewChat = activeSessionId === 'chat';

    const handleCreateSession = () => {
        createSession({ projectId }, {
            onSuccess: (newSession) => {
                router.push(`/projects/${projectId}/chat/${newSession.id}`);
            }
        });
    };

    const handleRename = (sessionId: string, newTitle: string) => {
        if (newTitle.trim() && newTitle.length <= 100) {
            updateTitle({ sessionId, title: newTitle.trim() });
        }
        setEditingId(null);
    };

    const handleDelete = (sessionId: string) => {
        if (confirm("Permanently delete this secure chat session?")) {
            deleteSession({ sessionId, projectId }, {
                onSuccess: () => {
                    if (activeSessionId === sessionId) {
                        router.push(`/projects/${projectId}/chat`);
                    }
                }
            });
        }
    };

    return (
        <div className="flex flex-col h-full w-full bg-zinc-950 border-r border-zinc-800 shadow-sm relative z-20">
            <div className="p-4 border-b border-zinc-800 bg-zinc-950">
                <Button
                    onClick={handleCreateSession}
                    disabled={isCreating}
                    className={`w-full font-bold shadow-sm transition-all ${isNewChat ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 hover:bg-cyan-500/30' : 'bg-cyan-500 text-zinc-950 hover:bg-cyan-400'}`}
                >
                    {isCreating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
                    New Conversation
                </Button>
            </div>

            <ScrollArea className="flex-1 px-3 py-4">
                {isLoading && (
                    <div className="flex flex-col space-y-3">
                        {[1, 2, 3, 4, 5].map(i => (
                            <div key={i} className="h-16 bg-zinc-900 rounded-xl animate-pulse border border-zinc-800/50 w-full"></div>
                        ))}
                    </div>
                )}

                {!isLoading && sessions?.length === 0 && (
                    <div className="flex flex-col items-center justify-center p-8 text-center mt-10 opacity-70">
                        <MessageSquare className="w-8 h-8 text-zinc-600 mb-3" />
                        <div className="text-xs font-bold text-zinc-500 tracking-widest uppercase">No Active Sessions</div>
                    </div>
                )}

                <div className="space-y-2">
                    {sessions?.map((s: any) => {
                        const isActive = activeSessionId === s.id;
                        return (
                            <div
                                key={s.id}
                                className={`group flex flex-col p-3 rounded-xl cursor-pointer transition-all border ${isActive
                                    ? 'bg-zinc-900 border-zinc-700 shadow-sm'
                                    : 'border-transparent hover:bg-zinc-900/50 hover:border-zinc-800'
                                    }`}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex-1 overflow-hidden pr-2" onClick={() => router.push(`/projects/${projectId}/chat/${s.id}`)}>
                                        {editingId === s.id ? (
                                            <input
                                                autoFocus
                                                type="text"
                                                value={editValue}
                                                onChange={e => setEditValue(e.target.value)}
                                                onBlur={() => handleRename(s.id, editValue)}
                                                onKeyDown={e => e.key === 'Enter' && handleRename(s.id, editValue)}
                                                className="w-full text-xs font-bold bg-zinc-950 text-white border-b border-cyan-500 outline-none px-1 py-0.5"
                                            />
                                        ) : (
                                            <div className={`text-sm font-bold truncate ${isActive ? 'text-zinc-100' : 'text-zinc-300'}`}>
                                                {s.title || "Untitled Session"}
                                            </div>
                                        )}
                                        <div className="text-[10px] uppercase font-bold tracking-widest mt-1 text-zinc-500">
                                            {formatDistanceToNow(new Date(s.updated_at), { addSuffix: true })}
                                        </div>
                                    </div>
                                    <div className="hidden group-hover:flex space-x-1 shrink-0">
                                        <button
                                            onClick={(e) => { e.stopPropagation(); setEditValue(s.title); setEditingId(s.id); }}
                                            className="text-xs font-bold w-6 h-6 flex items-center justify-center bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white rounded transition-colors"
                                        >
                                            <Edit2 className="w-3 h-3" />
                                        </button>
                                        <button
                                            onClick={(e) => { e.stopPropagation(); handleDelete(s.id); }}
                                            className="text-xs font-bold w-6 h-6 flex items-center justify-center bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded transition-colors"
                                        >
                                            <Trash2 className="w-3 h-3" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </ScrollArea>
        </div>
    );
}
