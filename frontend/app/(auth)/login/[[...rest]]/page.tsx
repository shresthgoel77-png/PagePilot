"use client";

import { SignIn } from "@clerk/nextjs";

export default function LoginPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-zinc-950 relative overflow-hidden text-zinc-100 p-4">
            {/* Top-center radial gradient */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none" />

            {/* Subtle Noise Texture Mapping Gracefully */}
            <div className="absolute inset-0 z-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] pointer-events-none mix-blend-overlay"></div>

            <div className="w-full max-w-md relative z-10 overflow-hidden flex flex-col items-center">
                <SignIn
                    appearance={{
                        elements: {
                            card: "bg-zinc-900 border border-zinc-800 shadow-2xl rounded-2xl w-full p-8",
                            headerTitle: "text-3xl font-bold tracking-tight text-white mb-2 text-center",
                            headerSubtitle: "text-sm text-zinc-400 text-center",
                            formButtonPrimary: "w-full bg-cyan-500 text-zinc-950 font-semibold hover:bg-cyan-400 hover:shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300",
                            formFieldLabel: "text-zinc-300",
                            formFieldInput: "bg-zinc-950 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus:ring-cyan-500 focus:border-cyan-500",
                            footerActionText: "text-sm text-zinc-500",
                            footerActionLink: "text-cyan-500 font-semibold hover:text-cyan-400 hover:underline transition-colors"
                        }
                    }}
                />
            </div>
        </div>
    );
}
