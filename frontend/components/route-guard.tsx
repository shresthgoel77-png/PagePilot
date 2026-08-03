"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";

export function RouteGuard({ children }: { children: React.ReactNode }) {
    const { token } = useAuthStore();
    const router = useRouter();
    const pathname = usePathname();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        if (!mounted) return;

        const isAuthRoute = pathname.startsWith("/login") || pathname.startsWith("/register");
        const protectedPaths = ['/settings', '/dashboard', '/projects'];
        const isProtected = protectedPaths.some(p => pathname.startsWith(p));

        // Inject / ensure guest token is cleanly populated client-side globally
        if (typeof window !== 'undefined' && !localStorage.getItem('guest_session_id')) {
            localStorage.setItem('guest_session_id', crypto.randomUUID());
        }

        if (!token && isProtected) {
            router.push("/login");
        } else if (token && isAuthRoute) {
            router.push("/dashboard");
        }
    }, [token, router, pathname, mounted]);

    if (!mounted) return null;

    return <>{children}</>;
}
