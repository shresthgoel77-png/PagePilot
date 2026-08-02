"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/stores/authStore";
import { useProjects } from "@/hooks/useProjects";
import { CreateProjectModal } from "@/components/create-project-modal";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import {
    FileText,
    Sparkles,
    FolderPlus,
    UploadCloud,
    MessageSquare,
    BarChart,
    Clock,
    Database,
    Files,
    Library
} from "lucide-react";

const AnimatedCounter = ({ value }: { value: number }) => {
    const [count, setCount] = useState(0);

    useEffect(() => {
        let start = 0;
        const end = parseInt(value.toString().substring(0, 3));
        if (start === end) return;

        let totalDuration = 1500;
        let incrementTime = (totalDuration / end);

        let timer = setInterval(() => {
            start += 1;
            setCount(start);
            if (start === end) clearInterval(timer);
        }, incrementTime);

        return () => clearInterval(timer);
    }, [value]);

    return <span>{count}{value > 999 ? "+" : ""}</span>;
};

const mockActivity = [
    { id: 1, action: "Uploaded Neural Networks.pdf", time: "2 hours ago" },
    { id: 2, action: "Ran Gap Analysis on Project X", time: "5 hours ago" },
    { id: 3, action: "Created Knowledge Base Delta", time: "1 day ago" },
    { id: 4, action: "Shared Document with Team", time: "2 days ago" },
    { id: 5, action: "Processed 500 pages via OCR", time: "3 days ago" },
];

const containerVariants = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1
        }
    }
};

const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.4 } }
};

export default function DashboardPage() {
    const { user } = useAuthStore();
    const { data: projects, isLoading } = useProjects();

    const [greeting, setGreeting] = useState("Good day");

    useEffect(() => {
        const hour = new Date().getHours();
        if (hour < 12) setGreeting("Good morning");
        else if (hour < 18) setGreeting("Good afternoon");
        else setGreeting("Good evening");
    }, []);

    const displayName = user?.name || user?.email?.split('@')[0] || "Researcher";

    if (isLoading) {
        return (
            <div className="flex flex-col space-y-8 pb-8 p-6 w-full h-[80vh]">
                <div className="flex justify-between items-center">
                    <div className="space-y-4">
                        <Skeleton className="h-10 w-48 bg-zinc-800" />
                        <Skeleton className="h-4 w-32 bg-zinc-800" />
                    </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
                    <Skeleton className="h-32 bg-zinc-800 rounded-xl" />
                    <Skeleton className="h-32 bg-zinc-800 rounded-xl" />
                    <Skeleton className="h-32 bg-zinc-800 rounded-xl" />
                    <Skeleton className="h-32 bg-zinc-800 rounded-xl" />
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
                    <Skeleton className="h-64 lg:col-span-2 bg-zinc-800 rounded-xl" />
                    <Skeleton className="h-64 lg:col-span-1 bg-zinc-800 rounded-xl" />
                </div>
            </div>
        );
    }

    return (
        <motion.div
            className="flex flex-col space-y-8 pb-8"
            variants={containerVariants}
            initial="hidden"
            animate="show"
        >
            {/* Header Section & Quick Actions mapping seamlessly natively natively */}
            <motion.div variants={itemVariants} className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tight">Dashboard</h1>
                    <p className="text-zinc-400 mt-1">{greeting}, {displayName}</p>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                    <Button variant="outline" className="bg-zinc-900 border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors">
                        <UploadCloud className="w-4 h-4 mr-2" /> Upload PDF
                    </Button>
                    <Button variant="outline" className="bg-zinc-900 border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors">
                        <MessageSquare className="w-4 h-4 mr-2" /> Start Chat
                    </Button>
                    <Button variant="outline" className="bg-zinc-900 border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors">
                        <BarChart className="w-4 h-4 mr-2" /> Run Analysis
                    </Button>
                    <CreateProjectModal />
                </div>
            </motion.div>

            {/* Empty State structural view implicitly native */}
            {(!projects || projects.length === 0) ? (
                <motion.div variants={itemVariants} className="flex flex-col items-center justify-center flex-1 bg-zinc-900/50 border border-dashed border-zinc-800 rounded-2xl py-32 relative overflow-hidden group">
                    <div className="relative mb-6">
                        <FileText className="w-20 h-20 text-zinc-700 mx-auto transform group-hover:scale-105 transition-transform duration-500" />
                        <Sparkles className="w-8 h-8 text-cyan-500 absolute -top-2 -right-4 animate-pulse opacity-0 group-hover:opacity-100 transition-opacity duration-500 delay-100" />
                    </div>
                    <h2 className="text-xl font-bold tracking-tight text-zinc-200">Create your first project to get started</h2>
                    <p className="text-zinc-500 mt-2 mb-8 text-center max-w-sm">
                        Spin up isolated workspaces aggregating PDFs naturally structurally.
                    </p>
                    <CreateProjectModal />
                </motion.div>
            ) : (
                <>
                    {/* Stats Bento Grid natively scalable */}
                    <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <Card className="bg-zinc-900 border-zinc-800 hover:border-cyan-500/50 transition-colors overflow-hidden group">
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <CardTitle className="text-sm font-medium text-zinc-400">Total Projects</CardTitle>
                                <Library className="w-4 h-4 text-cyan-500 opacity-70 group-hover:opacity-100 transition-opacity" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-black text-white">
                                    <AnimatedCounter value={projects.length} />
                                </div>
                                <p className="text-xs text-zinc-500 mt-1">+2 from last week</p>
                            </CardContent>
                        </Card>

                        <Card className="bg-zinc-900 border-zinc-800 hover:border-cyan-500/50 transition-colors overflow-hidden group">
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <CardTitle className="text-sm font-medium text-zinc-400">Documents Uploaded</CardTitle>
                                <Files className="w-4 h-4 text-emerald-500 opacity-70 group-hover:opacity-100 transition-opacity" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-black text-white">
                                    <AnimatedCounter value={projects.length * 4} />
                                </div>
                                <p className="text-xs text-zinc-500 mt-1">+12 recently added</p>
                            </CardContent>
                        </Card>

                        <Card className="bg-zinc-900 border-zinc-800 hover:border-cyan-500/50 transition-colors overflow-hidden group">
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <CardTitle className="text-sm font-medium text-zinc-400">AI Conversations</CardTitle>
                                <MessageSquare className="w-4 h-4 text-blue-500 opacity-70 group-hover:opacity-100 transition-opacity" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-black text-white">
                                    <AnimatedCounter value={124} />
                                </div>
                                <p className="text-xs text-zinc-500 mt-1">15 active this week</p>
                            </CardContent>
                        </Card>

                        <Card className="bg-zinc-900 border-zinc-800 hover:border-cyan-500/50 transition-colors overflow-hidden group">
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <CardTitle className="text-sm font-medium text-zinc-400">Storage Used</CardTitle>
                                <Database className="w-4 h-4 text-amber-500 opacity-70 group-hover:opacity-100 transition-opacity" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-black text-white">
                                    <AnimatedCounter value={214} /> <span className="text-lg font-bold text-zinc-500">MB</span>
                                </div>
                                <p className="text-xs text-zinc-500 mt-1">85% capacity remaining</p>
                            </CardContent>
                        </Card>
                    </motion.div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Recent Projects Flow mapping structurally natively */}
                        <motion.div variants={itemVariants} className="lg:col-span-2 space-y-4">
                            <div className="flex items-center justify-between">
                                <h2 className="text-lg font-bold text-zinc-100 tracking-tight">Recent Projects</h2>
                                <Link href="/dashboard/projects" className="text-sm font-medium text-cyan-500 hover:text-cyan-400">
                                    View all
                                </Link>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {projects.slice(0, 4).map((project: any) => (
                                    <Link href={`/dashboard/projects/${project.id}`} key={project.id}>
                                        <Card className="bg-zinc-900 border-zinc-800 hover:border-cyan-500/50 transition-all cursor-pointer h-full flex flex-col group hover:-translate-y-1 overflow-hidden">
                                            <div className="h-16 w-full bg-gradient-to-r from-zinc-800 to-zinc-900 group-hover:from-cyan-900/40 group-hover:to-zinc-900 transition-colors relative overflow-hidden">
                                                <div className="absolute inset-0 bg-[url('https://transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
                                            </div>
                                            <CardContent className="pt-4 flex-1">
                                                <div className="flex justify-between items-start mb-2">
                                                    <h3 className="font-bold text-zinc-100 truncate">{project.title || "Untitled Project"}</h3>
                                                    <Badge variant="secondary" className="bg-zinc-800 text-zinc-300 pointer-events-none shrink-0 min-w-[50px] justify-center ml-2 border-zinc-700">
                                                        4 Docs
                                                    </Badge>
                                                </div>
                                                <div className="flex items-center text-xs text-zinc-500 mt-4 font-medium">
                                                    <Clock className="w-3.5 h-3.5 mr-1" />
                                                    Last active: {new Date().toLocaleDateString()}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    </Link>
                                ))}
                            </div>
                        </motion.div>

                        {/* Event Feed organically structural mapped seamlessly */}
                        <motion.div variants={itemVariants} className="lg:col-span-1 space-y-4">
                            <h2 className="text-lg font-bold text-zinc-100 tracking-tight">Activity Feed</h2>
                            <Card className="bg-zinc-900 border-zinc-800 flex flex-col h-[320px]">
                                <ScrollArea className="flex-1 p-4">
                                    <div className="space-y-4">
                                        {mockActivity.map((event, index) => (
                                            <div key={event.id}>
                                                <div className="flex flex-col gap-1">
                                                    <p className="text-sm font-medium text-zinc-300 leading-snug">{event.action}</p>
                                                    <p className="text-xs text-zinc-500 font-mono tracking-tighter">{event.time}</p>
                                                </div>
                                                {index < mockActivity.length - 1 && <Separator className="mt-4 bg-zinc-800" />}
                                            </div>
                                        ))}
                                    </div>
                                </ScrollArea>
                            </Card>
                        </motion.div>
                    </div>
                </>
            )}
        </motion.div>
    );
}
