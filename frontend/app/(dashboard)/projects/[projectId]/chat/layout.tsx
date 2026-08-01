import { ChatSidebar } from '@/components/chat-sidebar';

export default async function ChatLayout({ children, params }: { children: React.ReactNode, params: Promise<{ projectId: string }> }) {
    const resolvedParams = await params;
    return (
        <div className="flex h-full w-full bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
            <div className="hidden lg:flex w-80 shrink-0 h-full border-r border-slate-200 relative z-20">
                <ChatSidebar projectId={resolvedParams.projectId} />
            </div>

            <div className="flex-1 relative flex flex-col h-full bg-white overflow-hidden">
                {children}
            </div>
        </div>
    );
}
