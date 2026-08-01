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
        if (mounted) {
            const isAuthRoute = pathname.startsWith("/login") || pathname.startsWith("/register");
            if (!token && !isAuthRoute) {
                router.push("/login");
            } else if (token && isAuthRoute) {
                router.push("/dashboard");
            }
        }
    }, [token, router, pathname, mounted]);

    if (!mounted) return null;

    return <>{children}</>;
}
