"use client";

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { formatDistanceToNow } from 'date-fns';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { useChatSessions, useUpdateSessionTitle, useDeleteSession } from '@/hooks/useChatSessions';

export function ChatSidebar({ projectId }: { projectId: string }) {
    const { data: sessions, isLoading } = useChatSessions(projectId);
    const { mutate: updateTitle } = useUpdateSessionTitle();
    const { mutate: deleteSession } = useDeleteSession();
    const pathname = usePathname();
    const router = useRouter();

    const [editingId, setEditingId] = useState<string | null>(null);
    const [editValue, setEditValue] = useState("");

    const activeSessionId = pathname.split('/').pop();

    const handleRename = (sessionId: string, newTitle: string) => {
        if (newTitle.trim() && newTitle.length <= 100) {
            updateTitle({ sessionId, title: newTitle.trim() });
        }
        setEditingId(null);
    };

    const handleDelete = (sessionId: string) => {
        if (confirm("Execute structural eradication explicitly mapping bounds uniquely?")) {
            deleteSession({ sessionId, projectId }, {
                onSuccess: () => {
                    if (activeSessionId === sessionId) {
                        router.push(`/dashboard/projects/${projectId}/chat`);
                    }
                }
            });
        }
    };

    return (
        <div className="flex flex-col h-full w-full bg-slate-50 border-r border-slate-200 shadow-sm relative z-20">
            <div className="p-4 border-b border-slate-200 bg-white">
                <Link href={`/dashboard/projects/${projectId}/chat`}>
                    <Button className="w-full font-bold shadow-sm bg-blue-600 hover:bg-blue-700 text-white transition-all">+ New Global Vector Chat</Button>
                </Link>
            </div>

            <ScrollArea className="flex-1">
                {isLoading && <div className="p-4 flex flex-col space-y-4">{[1, 2, 3, 4, 5].map(i => <div key={i} className="h-16 bg-slate-200 rounded-md animate-pulse w-full"></div>)}</div>}

                {!isLoading && sessions?.length === 0 && (
                    <div className="p-8 text-center text-xs font-bold text-slate-400 mt-10 tracking-widest uppercase">No Bounds Executed.</div>
                )}

                <div className="p-3 space-y-2">
                    {sessions?.map((s: any) => {
                        const isActive = activeSessionId === s.id;
                        return (
                            <div key={s.id} className={`group flex flex-col p-3 rounded-lg cursor-pointer transition-all border ${isActive ? 'bg-white border-blue-200 shadow-sm' : 'border-transparent hover:bg-white hover:border-slate-200'}`}>
                                <div className="flex justify-between items-start">
                                    <div className="flex-1 overflow-hidden pr-2" onClick={() => router.push(`/dashboard/projects/${projectId}/chat/${s.id}`)}>
                                        {editingId === s.id ? (
                                            <input
                                                autoFocus
                                                type="text"
                                                value={editValue}
                                                onChange={e => setEditValue(e.target.value)}
                                                onBlur={() => handleRename(s.id, editValue)}
                                                onKeyDown={e => e.key === 'Enter' && handleRename(s.id, editValue)}
                                                className="w-full text-xs font-bold bg-slate-50 border-b-2 border-blue-400 outline-none p-1"
                                            />
                                        ) : (
                                            <div className="text-sm font-extrabold truncate text-slate-800">{s.title}</div>
                                        )}
                                        <div className="text-[10px] uppercase font-bold tracking-widest mt-1 text-slate-400">
                                            {formatDistanceToNow(new Date(s.updated_at), { addSuffix: true })}
                                        </div>
                                    </div>
                                    <div className="hidden group-hover:flex space-x-1 shrink-0">
                                        <button onClick={(e) => { e.stopPropagation(); setEditValue(s.title); setEditingId(s.id); }} className="text-xs font-bold w-6 h-6 flex items-center justify-center bg-slate-100 hover:bg-slate-200 text-slate-600 rounded">E</button>
                                        <button onClick={(e) => { e.stopPropagation(); handleDelete(s.id); }} className="text-xs font-bold w-6 h-6 flex items-center justify-center bg-red-50 hover:bg-red-100 text-red-600 rounded">X</button>
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
