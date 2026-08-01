"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Toaster } from "sonner";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const { user, token, logout } = useAuthStore();
    const router = useRouter();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        if (!token && mounted) {
            router.push("/login");
        }
    }, [token, router, mounted]);

    const handleLogout = () => {
        logout();
        router.push("/login");
    };

    // Enforce Next hydration natively bypassing mismatches effectively
    if (!mounted) return null;

    return (
        <div className="min-h-screen flex flex-col md:flex-row bg-slate-50 relative overflow-hidden">
            <Toaster richColors position="top-right" />
            {/* Dynamic Header Mobile */}
            <div className="md:hidden flex flex-row items-center justify-between p-4 border-b bg-white shadow-sm z-20 relative">
                <span className="font-bold text-xl text-slate-900 tracking-tight">ResearchOS</span>
                <Sheet>
                    {/* @ts-ignore */}
                    <SheetTrigger asChild>
                        <Button variant="outline" size="sm">Menu</Button>
                    </SheetTrigger>
                    <SheetContent side="left" className="w-64 p-0">
                        <nav className="flex flex-col space-y-2 mt-12 p-4">
                            <a href="/dashboard" className="text-md font-semibold text-slate-700 hover:text-blue-600 transition-colors">Overview Hub</a>
                            <a href="/dashboard/projects" className="text-md font-semibold text-slate-700 hover:text-blue-600 transition-colors">Documents & Projects</a>
                        </nav>
                        <div className="absolute bottom-4 left-4 right-4">
                            <Button onClick={handleLogout} variant="destructive" className="w-full">Log out completely</Button>
                        </div>
                    </SheetContent>
                </Sheet>
            </div>

            {/* Main Desktop Sidebar Context */}
            <aside className="w-64 bg-white border-r hidden md:flex flex-col flex-shrink-0 relative h-screen shadow-md z-10 transition-all">
                <div className="p-6 border-b border-slate-100 flex items-center justify-center">
                    <h2 className="text-2xl font-extrabold tracking-tighter bg-gradient-to-br from-slate-900 to-slate-600 bg-clip-text text-transparent">ResearchOS</h2>
                </div>
                <nav className="flex-1 p-4 flex flex-col space-y-2 overflow-y-auto">
                    <a href="/dashboard" className="p-3 rounded-lg hover:bg-slate-100 font-semibold text-sm transition-colors text-slate-600">Overview Board</a>
                    <a href="/dashboard/projects" className="p-3 rounded-lg hover:bg-slate-100 font-semibold text-sm transition-colors text-slate-600">Project Architectures</a>
                </nav>
                <div className="p-4 border-t border-slate-100 bg-slate-50 w-full relative">
                    {user && (
                        <DropdownMenu>
                            {/* @ts-ignore */}
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" className="w-full h-14 justify-start space-x-3 px-3">
                                    <Avatar className="h-8 w-8 shadow-sm">
                                        <AvatarFallback className="text-sm font-bold bg-slate-800 text-white">{user?.email?.charAt(0).toUpperCase()}</AvatarFallback>
                                    </Avatar>
                                    <span className="text-sm font-medium truncate w-full text-left text-slate-700">{user.email}</span>
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-60 p-2">
                                <div className="p-3 text-xs text-slate-400 font-mono tracking-tight truncate border-b mb-2">{user.email}</div>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={handleLogout} className="text-red-600 font-bold hover:bg-red-50 rounded-sm cursor-pointer p-3">
                                    Logout Session
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    )}
                </div>
            </aside>

            {/* Primary Payload Body Mapping Screen Coordinates Natively */}
            <main className="flex-1 overflow-y-auto bg-slate-50 flex flex-col w-full h-full lg:h-screen relative">
                <div className="w-full max-w-7xl mx-auto p-4 md:p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
