"use client";

import { useState } from "react";
import { useProjects } from "@/hooks/useProjects";
import { ProjectCard } from "@/components/project-card";
import { CreateProjectModal } from "@/components/create-project-modal";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, LayoutGrid, List as ListIcon, FolderOpen, ArrowUpDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { format } from "date-fns";
import { useDeleteProject } from "@/hooks/useProjects";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { EditProjectModal } from "@/components/edit-project-modal";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { MoreVertical, Edit2, Trash2, ExternalLink } from "lucide-react";

export default function ProjectsPage() {
    const { data: projects, isLoading } = useProjects();
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [searchQuery, setSearchQuery] = useState("");

    const filteredProjects = projects?.filter((p: any) =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()))
    ) || [];

    if (isLoading) {
        return (
            <div className="flex items-center justify-center p-24">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full space-y-6 pb-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tight">Projects Hub</h1>
                    <p className="text-zinc-400 mt-1">Manage and architect your functional workspaces.</p>
                </div>
                <CreateProjectModal />
            </div>

            <div className="flex flex-col sm:flex-row justify-between items-center gap-4 bg-zinc-900 border border-zinc-800 p-2 rounded-lg">
                <div className="relative w-full sm:w-96">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                    <Input
                        placeholder="Search projects..."
                        className="pl-9 bg-zinc-950 border-zinc-800 text-zinc-200 focus-visible:ring-cyan-500"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
                <div className="flex items-center space-x-1 shrink-0 bg-zinc-950 rounded-md p-1 border border-zinc-800">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setViewMode('grid')}
                        className={`h-8 w-8 p-0 rounded-sm ${viewMode === 'grid' ? 'bg-zinc-800 text-cyan-500' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        <LayoutGrid className="h-4 w-4" />
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setViewMode('list')}
                        className={`h-8 w-8 p-0 rounded-sm ${viewMode === 'list' ? 'bg-zinc-800 text-cyan-500' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        <ListIcon className="h-4 w-4" />
                    </Button>
                </div>
            </div>

            {filteredProjects.length === 0 ? (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex flex-col items-center justify-center flex-1 bg-zinc-900/40 border border-dashed border-zinc-800 rounded-2xl py-32"
                >
                    <FolderOpen className="w-20 h-20 text-zinc-700 mb-6" />
                    <h2 className="text-xl font-bold tracking-tight text-zinc-200">No projects found</h2>
                    <p className="text-zinc-500 mt-2 mb-8 text-center max-w-sm">
                        {"We couldn't track any projects under natural search constraints natively."}
                    </p>
                    {searchQuery ? (
                        <Button variant="outline" onClick={() => setSearchQuery("")} className="border-zinc-700 text-zinc-300">
                            Clear Search
                        </Button>
                    ) : (
                        <CreateProjectModal />
                    )}
                </motion.div>
            ) : (
                <AnimatePresence mode="wait">
                    {viewMode === 'grid' ? (
                        <motion.div
                            key="grid"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                        >
                            {filteredProjects.map((project: any) => (
                                <ProjectCard key={project.id} project={project} />
                            ))}
                        </motion.div>
                    ) : (
                        <motion.div
                            key="list"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden"
                        >
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left text-zinc-400">
                                    <thead className="text-xs text-zinc-500 uppercase bg-zinc-950/50 border-b border-zinc-800">
                                        <tr>
                                            <th scope="col" className="px-6 py-4">Workspace Identity</th>
                                            <th scope="col" className="px-6 py-4">Context Docs</th>
                                            <th scope="col" className="px-6 py-4">Generated Timestamp</th>
                                            <th scope="col" className="px-6 py-4 text-right">Access Routes</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredProjects.map((project: any) => (
                                            <ListViewRow key={project.id} project={project} />
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            )}
        </div>
    );
}

function ListViewRow({ project }: { project: any }) {
    const { mutate: deleteProject, isPending: isDeleting } = useDeleteProject();
    const [editOpen, setEditOpen] = useState(false);

    return (
        <tr className="border-b border-zinc-800/50 hover:bg-zinc-800/20 transition-colors">
            <td className="px-6 py-4 font-bold text-zinc-100 min-w-[200px]">
                <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 rounded-full bg-cyan-500 mr-1 shadow-[0_0_8px_rgba(6,182,212,0.5)]"></div>
                    <Link href={`/projects/${project.id}`} className="hover:text-cyan-400 transition-colors">
                        {project.name}
                    </Link>
                </div>
            </td>
            <td className="px-6 py-4 font-mono text-xs font-semibold text-zinc-300">
                4 PDF(s)
            </td>
            <td className="px-6 py-4">
                {format(new Date(project.updated_at), "MMM d, yyyy")}
            </td>
            <td className="px-6 py-4 text-right space-x-1">
                <Link href={`/projects/${project.id}`}>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-400 hover:text-cyan-400 hover:bg-cyan-500/10">
                        <ExternalLink className="h-4 w-4" />
                    </Button>
                </Link>
                <Button variant="ghost" size="sm" onClick={() => setEditOpen(true)} className="h-8 w-8 p-0 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800">
                    <Edit2 className="h-4 w-4" />
                </Button>

                <AlertDialog>
                    <AlertDialogTrigger asChild>
                        <Button variant="ghost" size="sm" disabled={isDeleting} className="h-8 w-8 p-0 text-zinc-400 hover:text-red-400 hover:bg-red-500/10">
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent className="bg-zinc-950 border-zinc-800">
                        <AlertDialogHeader>
                            <AlertDialogTitle className="text-zinc-100">Wipe Project Integrity?</AlertDialogTitle>
                            <AlertDialogDescription className="text-zinc-400">
                                Data mapping vector indexes for "{project.name}" will be obliterated securely entirely.
                            </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                            <AlertDialogCancel className="bg-zinc-900 text-zinc-300 border-zinc-800 hover:bg-zinc-800 hover:text-zinc-100">Abort</AlertDialogCancel>
                            <AlertDialogAction
                                className="bg-red-500/20 text-red-500 border border-red-500/50 hover:bg-red-500 hover:text-white"
                                onClick={() => deleteProject(project.id)}
                            >
                                Execute Purge
                            </AlertDialogAction>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialog>

                <EditProjectModal project={project} open={editOpen} onClose={() => setEditOpen(false)} />
            </td>
        </tr>
    );
}
