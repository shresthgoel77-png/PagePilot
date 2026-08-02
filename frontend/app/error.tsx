"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { TriangleAlert, RotateCcw } from "lucide-react";
import { useRouter } from "next/navigation";

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    const router = useRouter();

    useEffect(() => {
        console.error("Global Fault Executed:", error);
    }, [error]);

    return (
        <div className="min-h-screen w-full bg-zinc-950 flex flex-col items-center justify-center p-4">
            <div className="max-w-md w-full bg-zinc-900 border border-zinc-800 rounded-3xl p-8 text-center shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-red-500/10 rounded-full blur-[100px] pointer-events-none"></div>

                <div className="w-20 h-20 bg-zinc-950 border border-zinc-800/80 rounded-full flex items-center justify-center mx-auto mb-6 shadow-[-10px_-10px_30px_rgba(255,255,255,0.02)] ring-1 ring-zinc-800">
                    <TriangleAlert className="w-8 h-8 text-red-500 animate-pulse" />
                </div>

                <h1 className="text-2xl font-black text-white tracking-tight mb-2">System Interruption</h1>
                <p className="text-zinc-500 font-medium text-sm leading-relaxed mb-8">
                    An unexpected structural failure occurred executing rendering limits natively. Please recycle the active frame boundaries efficiently.
                </p>

                <div className="flex flex-col gap-3">
                    <Button
                        onClick={() => reset()}
                        className="w-full h-12 bg-zinc-100 hover:bg-white text-zinc-950 font-black tracking-tight rounded-xl transition-all shadow-[0_0_15px_rgba(255,255,255,0.1)] hover:scale-[1.02]"
                    >
                        <RotateCcw className="w-4 h-4 mr-2" /> Attempt Recovery
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => router.push('/dashboard')}
                        className="w-full h-12 bg-transparent border-zinc-800 text-zinc-400 font-bold hover:text-white hover:bg-zinc-800 rounded-xl transition-all hover:border-zinc-700"
                    >
                        Return to Command Center
                    </Button>
                </div>
            </div>
        </div>
    );
}
