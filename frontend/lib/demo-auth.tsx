"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const DemoAuthContext = createContext<any>(null);

export const ClerkProvider = ({ children }: { children: React.ReactNode }) => {
    // For demo mode, we inherently simulate a logged-in user if MOCK_TOKEN is set.
    // In our case since we bypassed Clerk completely, let's just make everything available.
    const [isLoaded, setIsLoaded] = useState(true);
    const [isSignedIn, setIsSignedIn] = useState(true);

    return (
        <DemoAuthContext.Provider value={{ isLoaded, isSignedIn }}>
            {children}
        </DemoAuthContext.Provider>
    );
};

export const useUser = () => {
    return {
        isLoaded: true,
        isSignedIn: true,
        user: {
            id: "mock_clerk_id",
            primaryEmailAddress: { emailAddress: "demo@researchos.local" },
            fullName: "Demo User",
            firstName: "Demo",
            lastName: "User",
            imageUrl: ""
        }
    };
};

export const useAuth = () => {
    const router = useRouter();
    return {
        isLoaded: true,
        isSignedIn: true,
        userId: "mock_clerk_id",
        sessionId: "mock_session_id",
        getToken: async () => "MOCK_TOKEN",
        signOut: () => {
            document.cookie = "demo_auth=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            window.location.href = "/";
        }
    };
};

export const useClerk = () => {
    return {
        loaded: true,
        setActive: async () => { },
        signOut: () => {
            document.cookie = "demo_auth=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            window.location.href = "/";
        }
    };
};

export const useSignIn = () => {
    return {
        isLoaded: true,
        signIn: {
            create: async () => ({ status: "complete" })
        }
    };
};

export const SignIn = (props: any) => {
    const handleLogin = () => {
        // Set a cookie so we know they "logged in"
        document.cookie = "demo_auth=true; path=/";
        // MOCK_TOKEN is handled by Axios interceptor becauseNEXT_PUBLIC_BYPASS_CLERK=true
        window.location.href = "/dashboard";
    };

    return (
        <div className="flex flex-col items-center justify-center p-8 bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl w-full max-w-md">
            <h2 className="text-3xl font-bold tracking-tight text-white mb-2 text-center">Development Mode</h2>
            <p className="text-sm text-zinc-400 text-center mb-8">Click below to enter the local demo mode without Clerk authentication.</p>
            <button
                onClick={handleLogin}
                className="w-full py-2 px-4 bg-cyan-500 text-zinc-950 font-semibold rounded-md hover:bg-cyan-400 hover:shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300"
            >
                Enter Demo Version
            </button>
        </div>
    );
};

export const SignUp = SignIn;
