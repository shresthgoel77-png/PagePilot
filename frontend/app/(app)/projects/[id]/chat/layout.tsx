import { ReactNode } from "react";
import { ChatSidebar } from "@/components/chat-sidebar";

export default function ChatLayout({ children, params }: { children: ReactNode, params: { id: string } }) {
    return (
        <div className="flex h-full w-full overflow-hidden bg-zinc-950 rounded-2xl border border-zinc-800 relative z-10 shadow-2xl">
            {/* Left Panel: Chat Sessions Sidebar */}
            <div className="w-64 h-full shrink-0 relative z-20">
                <ChatSidebar projectId={params.id} />
            </div>

            {/* Center + Right Panels */}
            {children}
        </div>
    );
}
