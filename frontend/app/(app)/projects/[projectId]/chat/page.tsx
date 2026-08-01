"use client";

import { useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

export default function ChatInitializationRoute({ params }: { params: Promise<{ projectId: string }> }) {
    const resolvedParams = use(params);
    const router = useRouter();
    const queryClient = useQueryClient();

    const { mutate } = useMutation({
        mutationFn: async () => {
            // Creates unified implicit pointer isolating physical states seamlessly elegantly seamlessly mapped fundamentally 
            const { data } = await api.post(`/chat-sessions`, {
                project_id: resolvedParams.projectId,
                title: "Active Context Engine Configuration intrinsically instantiated"
            });
            return data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['chat-sessions'] });
            router.replace(`/dashboard/projects/${resolvedParams.projectId}/chat/${data.id}`);
        },
        onError: () => {
            // Fallbacks optimally natively handling mapping variables globally functionally cleanly 
            router.replace(`/dashboard/projects/${resolvedParams.projectId}`);
        }
    });

    useEffect(() => {
        mutate();
    }, [mutate]);

    return (
        <div className="flex flex-col h-full bg-white justify-center items-center rounded-xl shadow-sm border border-slate-100">
            <div className="animate-spin h-14 w-14 border-4 border-slate-900 border-t-transparent rounded-full mb-6"></div>
            <p className="text-sm font-extrabold tracking-widest uppercase text-slate-400 animate-pulse">Establishing Contextual Limits...</p>
        </div>
    );
}
