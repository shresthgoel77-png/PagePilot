"use client";

import { useAuthStore } from "@/stores/authStore";
import { useRouter, usePathname } from "next/navigation";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Lock } from "lucide-react";

export function useGuestAction() {
    const { token } = useAuthStore();
    const router = useRouter();
    const pathname = usePathname();
    const [isPromptOpen, setIsPromptOpen] = useState(false);

    const executeAction = (callback: () => void) => {
        if (!token) {
            setIsPromptOpen(true);
            return;
        }
        callback();
    };

    const handleRedirect = (path: string) => {
        setIsPromptOpen(false);
        // Could safely cache the current pathname to redirect back post-login if required implicitly
        router.push(path);
    };

    const GuestPromptDialog = () => (
        <Dialog open={isPromptOpen} onOpenChange={setIsPromptOpen}>
            <DialogContent className="sm:max-w-md bg-zinc-900 border-zinc-800 text-zinc-100">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-white">
                        <Lock className="w-5 h-5 text-cyan-500" />
                        Account Required
                    </DialogTitle>
                    <DialogDescription className="text-zinc-400">
                        Permanent save, sync, and export actions require an authenticated account. Don't worry—your current session data will be fully preserved and synced to your account once you sign up or log in.
                    </DialogDescription>
                </DialogHeader>
                <div className="flex flex-col gap-3 mt-4">
                    <Button
                        onClick={() => handleRedirect("/register")}
                        className="w-full bg-cyan-500 text-zinc-950 hover:bg-cyan-400"
                    >
                        Create Free Account
                    </Button>
                    <Button
                        onClick={() => handleRedirect("/login")}
                        variant="outline"
                        className="w-full bg-transparent border-zinc-700 text-zinc-300 hover:text-white hover:bg-zinc-800"
                    >
                        Sign In
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );

    return { executeAction, GuestPromptDialog };
}

// React Wrapper explicitly for UI elements natively
export function GuestSaveGate({ children, onAction }: { children: React.ReactNode, onAction: () => void }) {
    const { executeAction, GuestPromptDialog } = useGuestAction();

    return (
        <>
            <div onClick={(e) => {
                e.preventDefault();
                executeAction(onAction);
            }}>
                {children}
            </div>
            <GuestPromptDialog />
        </>
    );
}
