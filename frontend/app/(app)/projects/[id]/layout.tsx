"use client";

import { useEffect } from "react";
import { useParams, usePathname, useRouter } from "next/navigation";
import { useProject } from "@/hooks/useProjects";
import { useProjectStore } from "@/stores/projectStore";
import { SidebarProvider, Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent, SidebarHeader, SidebarMenu, SidebarMenuItem, SidebarMenuButton } from "@/components/ui/sidebar";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useUser } from "@/lib/demo-auth";
import Link from "next/link";
import {
    LayoutDashboard,
    FileText,
    MessageSquare,
    GitCompare,
    ScanSearch,
    ChevronLeft,
    Share2,
    Settings,
    Loader2
} from "lucide-react";

export default function ProjectLayout({ children }: { children: React.ReactNode }) {
    const params = useParams();
    const pathname = usePathname();
    const router = useRouter();
    const projectId = params.id as string;

    const { data: project, isLoading, isError } = useProject(projectId);
    const { setCurrentProject, currentProject } = useProjectStore();
    const { user } = useUser();

    useEffect(() => {
        if (project) {
            setCurrentProject(projectId, project);
        }
    }, [project, projectId, setCurrentProject]);

    if (isLoading && !currentProject) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-zinc-950">
                <div className="flex flex-col items-center space-y-4">
                    <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
                    <p className="text-zinc-500 text-sm font-medium">Mounting Workspace Environments...</p>
                </div>
            </div>
        );
    }

    if (isError) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-zinc-950 text-white">
                <h1 className="text-2xl font-bold mb-2">Workspace Isolation Fault</h1>
                <p className="text-zinc-500 mb-6 font-medium">Failed securely locking structural boundaries.</p>
                <Button variant="outline" onClick={() => router.push('/projects')} className="border-zinc-800 bg-zinc-900">
                    Return to Safe Mode
                </Button>
            </div>
        );
    }

    const navItems = [
        { label: "Overview", icon: LayoutDashboard, href: `/projects/${projectId}` },
        { label: "PDFs", icon: FileText, href: `/projects/${projectId}/pdfs` },
        { label: "Chat", icon: MessageSquare, href: `/projects/${projectId}/chat` },
        { label: "Reasoning", icon: GitCompare, href: `/projects/${projectId}/reasoning` },
        { label: "Gap Analysis", icon: ScanSearch, href: `/projects/${projectId}/gaps` },
    ];

    const currentNavLabel = navItems.find((item) => item.href === pathname)?.label || "Overview";

    return (
        <SidebarProvider>
            <div className="flex min-h-screen w-full bg-zinc-950 text-white">
                <Sidebar className="border-r border-zinc-800 bg-zinc-950 text-white">
                    <SidebarHeader className="border-b border-zinc-800/50 p-4">
                        <Link href="/projects" className="flex items-center text-xs font-semibold text-zinc-500 hover:text-cyan-400 mb-4 transition-colors">
                            <ChevronLeft className="w-3 h-3 mr-1" />
                            Back to Hub
                        </Link>
                        <h2 className="text-lg font-bold tracking-tight text-zinc-100 truncate pr-2">
                            {currentProject?.name || "Loading Context..."}
                        </h2>
                    </SidebarHeader>
                    <SidebarContent className="bg-zinc-950">
                        <SidebarGroup>
                            <SidebarGroupContent>
                                <SidebarMenu className="mt-4">
                                    {navItems.map((item) => {
                                        const isActive = pathname === item.href;
                                        return (
                                            <SidebarMenuItem key={item.label} className="px-2">
                                                <SidebarMenuButton
                                                    asChild
                                                    className={`w-full py-5 rounded-lg mb-1 transition-all ${isActive
                                                        ? 'bg-cyan-500/10 text-cyan-500 hover:bg-cyan-500/20 hover:text-cyan-400 font-bold'
                                                        : 'text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200'
                                                        }`}
                                                >
                                                    <Link href={item.href}>
                                                        <item.icon className={`h-4 w-4 ${isActive ? 'text-cyan-500' : 'text-zinc-500'}`} />
                                                        <span className="ml-2 font-medium">{item.label}</span>
                                                    </Link>
                                                </SidebarMenuButton>
                                            </SidebarMenuItem>
                                        )
                                    })}
                                </SidebarMenu>
                            </SidebarGroupContent>
                        </SidebarGroup>
                    </SidebarContent>
                </Sidebar>

                <main className="flex-1 flex flex-col min-w-0 bg-zinc-950">
                    <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center justify-between border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-md px-6">
                        <div className="flex items-center">
                            <Breadcrumb>
                                <BreadcrumbList>
                                    <BreadcrumbItem>
                                        <BreadcrumbLink href="/dashboard" className="text-zinc-500 hover:text-zinc-300">Dashboard</BreadcrumbLink>
                                    </BreadcrumbItem>
                                    <BreadcrumbSeparator className="text-zinc-600" />
                                    <BreadcrumbItem>
                                        <BreadcrumbLink href="/projects" className="text-zinc-500 hover:text-zinc-300">Projects</BreadcrumbLink>
                                    </BreadcrumbItem>
                                    <BreadcrumbSeparator className="text-zinc-600" />
                                    <BreadcrumbItem>
                                        <span className="text-zinc-400 max-w-[150px] truncate block">{currentProject?.name}</span>
                                    </BreadcrumbItem>
                                    <BreadcrumbSeparator className="text-zinc-600" />
                                    <BreadcrumbItem>
                                        <BreadcrumbPage className="text-zinc-100 font-bold">{currentNavLabel}</BreadcrumbPage>
                                    </BreadcrumbItem>
                                </BreadcrumbList>
                            </Breadcrumb>
                        </div>

                        <div className="flex flex-row items-center space-x-3">
                            <Button variant="outline" size="sm" className="hidden sm:flex bg-zinc-950 border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-white transition-colors">
                                <Share2 className="w-3.5 h-3.5 mr-2" /> Share Vault
                            </Button>

                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="outline" size="icon" className="bg-zinc-950 border-zinc-700 text-zinc-400 hover:text-white hover:bg-zinc-800">
                                        <Settings className="w-4 h-4" />
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="w-48 bg-zinc-950 border-zinc-800">
                                    <DropdownMenuItem className="text-zinc-300 hover:bg-zinc-900 cursor-pointer">
                                        Context Configurations
                                    </DropdownMenuItem>
                                    <DropdownMenuItem className="text-zinc-300 hover:bg-zinc-900 cursor-pointer">
                                        Vector Index Details
                                    </DropdownMenuItem>
                                    <DropdownMenuItem className="text-red-400 hover:bg-red-500/10 focus:text-red-400 focus:bg-red-500/10 cursor-pointer">
                                        Destructive Wipe
                                    </DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu>

                            <Avatar className="h-8 w-8 ml-2 border border-zinc-800 cursor-pointer shadow-sm">
                                <AvatarFallback className="bg-zinc-800 text-zinc-300 text-xs font-bold">
                                    {user?.primaryEmailAddress?.emailAddress?.charAt(0).toUpperCase() || 'R'}
                                </AvatarFallback>
                            </Avatar>
                        </div>
                    </header>

                    <div className="flex-1 overflow-auto bg-zinc-950 relative">
                        {children}
                    </div>
                </main>
            </div>
        </SidebarProvider>
    );
}
