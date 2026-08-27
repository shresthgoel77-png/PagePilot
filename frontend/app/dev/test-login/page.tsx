"use client";

import { useEffect, useState } from "react";
import { useSignIn, useClerk } from "@/lib/demo-auth";
import { useRouter } from "next/navigation";

/**
 * Dev-only auto-login page.
 * 1. Calls POST /dev/create-test-session on the backend to get a Clerk sign-in ticket
 * 2. Uses Clerk's signIn.create({ strategy: 'ticket' }) to authenticate
 * 3. Redirects to /dashboard
 *
 * Only works when NEXT_PUBLIC_BYPASS_CLERK=true
 */
export default function TestLoginPage() {
    const signInHook = useSignIn();
    const clerk = useClerk();
    const router = useRouter();
    const [status, setStatus] = useState("Initializing...");
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Wait for Clerk to load
        const isLoaded = (signInHook as any).isLoaded ?? clerk.loaded;
        const signIn = (signInHook as any).signIn ?? signInHook;
        const setActive = (signInHook as any).setActive ?? clerk.setActive;

        if (!isLoaded || !signIn) return;

        const bypass = process.env.NEXT_PUBLIC_BYPASS_CLERK === "true";
        if (!bypass) {
            setError("NEXT_PUBLIC_BYPASS_CLERK is not true. This page is disabled.");
            return;
        }

        const doLogin = async () => {
            try {
                // Step 1: Get a sign-in token from the backend
                setStatus("Requesting sign-in token from backend...");
                const res = await fetch("http://localhost:8000/dev/create-test-session", {
                    method: "POST",
                });
                if (!res.ok) {
                    const body = await res.json().catch(() => ({}));
                    throw new Error(body.detail || `Backend returned ${res.status}`);
                }
                const { token } = await res.json();
                if (!token) throw new Error("No token returned from backend");

                // Step 2: Use the token to sign in via Clerk
                setStatus("Authenticating with Clerk...");
                const result = await signIn.create({
                    strategy: "ticket",
                    ticket: token,
                });

                if (result.status === "complete" && result.createdSessionId) {
                    setStatus("Setting active session...");
                    await setActive({ session: result.createdSessionId });
                    setStatus("Authenticated! Redirecting to dashboard...");
                    router.push("/dashboard");
                } else {
                    throw new Error(`Sign-in returned status: ${result.status}`);
                }
            } catch (err: any) {
                console.error("Test login failed:", err);
                setError(err.message || "Unknown error");
                setStatus("Failed");
            }
        };

        doLogin();
    }, [signInHook, clerk, router]);

    return (
        <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 max-w-md w-full shadow-2xl">
                <h1 className="text-xl font-black text-white mb-4 tracking-tight">
                    Dev Test Login
                </h1>
                {error ? (
                    <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg p-4 text-sm font-medium">
                        {error}
                    </div>
                ) : (
                    <div className="flex items-center gap-3">
                        <div className="w-4 h-4 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                        <span className="text-sm text-zinc-400 font-medium">{status}</span>
                    </div>
                )}
            </div>
        </div>
    );
}
