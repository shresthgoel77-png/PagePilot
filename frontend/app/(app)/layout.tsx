"use client";

import { useUser, useAuth } from "@/lib/demo-auth";
import { useHealthStatus } from "@/hooks/useHealthStatus";
import { SidebarProvider, Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu, SidebarMenuItem, SidebarMenuButton } from "@/components/ui/sidebar";
import { Home, Folder, LogOut } from "lucide-react";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { usePathname } from "next/navigation";
import { CommandPalette } from "@/components/command-palette";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import Template from "./template";
import Link from "next/link";

export default function AppLayout({ children }: { children: React.ReactNode }) {
    useKeyboardShortcuts();

    const { user } = useUser();
    const { signOut } = useAuth();
    const health = useHealthStatus(10000);
    const pathname = usePathname();

    const isProjectContextRoute = pathname.startsWith('/projects/') && pathname.split('/').length > 2;

    const navItems = [
        { title: "Home", url: "/dashboard", icon: Home },
        { title: "Projects", url: "/projects", icon: Folder },
    ];

    if (isProjectContextRoute) {
        return <div className="h-full w-full bg-zinc-950 text-white">{children}</div>;
    }

    return (
        <>
            <CommandPalette />
            <SidebarProvider>
                <div className="flex min-h-screen w-full bg-zinc-50 relative overflow-hidden">
                    <Sidebar collapsible="icon" className="border-r border-zinc-200 bg-white">
                        <SidebarContent>
                            <SidebarGroup>
                                <SidebarGroupLabel>Application</SidebarGroupLabel>
                                <SidebarGroupContent>
                                    <SidebarMenu>
                                        {navItems.map((item) => (
                                            <SidebarMenuItem key={item.title}>
                                                <SidebarMenuButton asChild isActive={pathname === item.url || (item.url === '/projects' && pathname.startsWith('/projects'))}>
                                                    <Link href={item.url}>
                                                        <item.icon className="h-4 w-4" />
                                                        <span>{item.title}</span>
                                                    </Link>
                                                </SidebarMenuButton>
                                            </SidebarMenuItem>
                                        ))}
                                    </SidebarMenu>
                                </SidebarGroupContent>
                            </SidebarGroup>
                        </SidebarContent>
                    </Sidebar>

                    <main className="flex-1 flex flex-col min-w-0">
                        <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-4 border-b border-zinc-800 bg-zinc-950 px-4">
                            <SidebarTrigger className="text-zinc-400 hover:text-white" />

                            <div className="flex-1 flex items-center gap-4 text-zinc-500">
                                <div className="flex h-9 w-full max-w-sm items-center gap-2 rounded-md border border-zinc-800 bg-zinc-900 px-3 text-sm">
                                    <span className="opacity-50">Search... (Cmd+K)</span>
                                </div>
                            </div>

                            <div className="flex items-center gap-4">
                                <div className="flex items-center gap-2">
                                    <span className={`h-2.5 w-2.5 rounded-full ${health === 'green' ? 'bg-emerald-500' :
                                        health === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'
                                        } shadow-[0_0_8px_rgba(0,0,0,0.5)]`} />
                                </div>

                                {user && (
                                    <DropdownMenu>
                                        <DropdownMenuTrigger asChild>
                                            <Button variant="ghost" className="relative h-9 rounded-full px-2 gap-2 text-zinc-200 hover:bg-zinc-800 hover:text-white border border-zinc-800">
                                                <Avatar className="h-6 w-6">
                                                    <AvatarFallback className="text-xs bg-zinc-800 font-medium text-white">{user.primaryEmailAddress?.emailAddress?.charAt(0).toUpperCase() || "R"}</AvatarFallback>
                                                </Avatar>
                                                <span className="text-sm font-medium mr-1 truncate max-w-[120px]">{user.primaryEmailAddress?.emailAddress}</span>
                                            </Button>
                                        </DropdownMenuTrigger>
                                        <DropdownMenuContent align="end" className="w-56 bg-zinc-950 border-zinc-800 text-zinc-200">
                                            <div className="p-2 border-b border-zinc-800">
                                                <p className="font-medium text-sm truncate">{user.primaryEmailAddress?.emailAddress}</p>
                                            </div>
                                            <DropdownMenuItem onClick={() => signOut()} className="text-red-400 focus:bg-red-500/10 focus:text-red-400 cursor-pointer mt-1">
                                                <LogOut className="mr-2 h-4 w-4" />
                                                <span>Logout</span>
                                            </DropdownMenuItem>
                                        </DropdownMenuContent>
                                    </DropdownMenu>
                                )}
                            </div>
                        </header>

                        <div className="flex-1 overflow-auto p-6 bg-zinc-950 relative">
                            <Template>
                                {children}
                            </Template>
                        </div>
                    </main>
                </div>
            </SidebarProvider>
        </>
    );
}
