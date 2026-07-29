"use client";

import { useEffect, useState } from "react";

export default function Home() {
    const [health, setHealth] = useState<{ status?: string; db?: string; error?: string } | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch("/api/health")
            .then((res) => {
                if (!res.ok) throw new Error("API Route Failure");
                return res.json();
            })
            .then((data) => {
                setHealth(data);
                setLoading(false);
            })
            .catch((err) => {
                setHealth({ status: "error", error: err.message });
                setLoading(false);
            });
    }, []);

    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-zinc-950 text-white">
            <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
                <h1 className="text-4xl font-bold text-center mb-8 bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                    ResearchOS
                </h1>

                <div className="flex flex-col items-center justify-center border border-zinc-800 rounded-lg p-8 bg-zinc-900 shadow-2xl">
                    <h2 className="text-2xl font-semibold mb-4 text-zinc-100">System Status</h2>

                    {loading ? (
                        <p className="text-zinc-400 animate-pulse">Connecting to backend /api/health ...</p>
                    ) : (
                        <div className="flex flex-col space-y-4 w-full max-w-md">
                            <div className="flex justify-between items-center p-3 border border-zinc-800 rounded bg-zinc-950">
                                <span className="text-zinc-400">API Status</span>
                                <span className={`px-2 py-1 rounded text-xs font-bold ${health?.status === 'ok' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                                    {health?.status ? health.status.toUpperCase() : "UNREACHABLE"}
                                </span>
                            </div>

                            <div className="flex justify-between items-center p-3 border border-zinc-800 rounded bg-zinc-950">
                                <span className="text-zinc-400">Database</span>
                                <span className={`px-2 py-1 rounded text-xs font-bold ${health?.db === 'connected' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
                                    {health?.db ? health.db.toUpperCase() : (health?.error || "TIMEOUT")}
                                </span>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}
