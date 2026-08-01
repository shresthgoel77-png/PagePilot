import { useState, useMemo } from 'react';
import Link from 'next/link';
import { formatDistanceToNow, format } from 'date-fns';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useDeleteProject } from '@/hooks/useProjects';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { EditProjectModal } from './edit-project-modal';
import { MoreVertical, ExternalLink, Edit2, Trash2, FileText, CalendarClock } from 'lucide-react';

interface ProjectProps {
    id: string;
    name: string;
    description?: string | null;
    updated_at: string;
    created_at?: string;
}

const getGradient = (name: string) => {
    let hash = 0;
    for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    const h = Math.abs(hash) % 360;
    return `linear-gradient(135deg, hsl(${h}, 70%, 50%, 0.15) 0%, hsl(${(h + 40) % 360}, 70%, 60%, 0.4) 100%)`;
};

export function ProjectCard({ project }: { project: ProjectProps }) {
    const { mutate: deleteProject, isPending: isDeleting } = useDeleteProject();
    const [editOpen, setEditOpen] = useState(false);

    const gradient = useMemo(() => getGradient(project.name), [project.name]);

    return (
        <Card className="flex flex-col bg-zinc-900 border-zinc-800 transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_0_20px_rgba(6,182,212,0.1)] hover:border-cyan-500/30 overflow-hidden relative group">
            {/* Gradient Header Overlay */}
            <div
                className="h-20 w-full relative"
                style={{ background: gradient }}
            >
                <div className="absolute inset-0 bg-gradient-to-b from-transparent to-zinc-900 border-b border-zinc-800/50" />
            </div>

            <CardContent className="pt-4 flex-1 pb-4">
                <div className="flex justify-between items-start">
                    <h3 className="font-bold text-lg text-zinc-100 tracking-tight leading-tight mb-2 line-clamp-1">{project.name}</h3>
                </div>
                <p className="text-sm text-zinc-400 line-clamp-2 h-10 mb-4">
                    {project.description || "Initialize descriptions safely bridging logic metadata."}
                </p>

                <div className="flex items-center space-x-4 text-xs font-semibold text-zinc-500">
                    <div className="flex items-center">
                        <FileText className="w-3.5 h-3.5 mr-1.5 text-cyan-500/70" />
                        4 PDFs
                    </div>
                    <div className="flex items-center">
                        <CalendarClock className="w-3.5 h-3.5 mr-1.5 text-cyan-500/70" />
                        {format(new Date(project.updated_at || Date.now()), "MMM d, yyyy")}
                    </div>
                </div>
            </CardContent>

            <CardFooter className="flex justify-between items-center border-t border-zinc-800/50 bg-zinc-950/30 py-3">
                <Link href={`/dashboard/projects/${project.id}`}>
                    <Button variant="ghost" size="sm" className="text-cyan-500 hover:text-cyan-400 hover:bg-cyan-500/10 font-bold px-3">
                        <ExternalLink className="w-4 h-4 mr-2" /> Open Hub
                    </Button>
                </Link>

                <div className="flex items-center">
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-500 hover:text-zinc-300">
                                <MoreVertical className="h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="bg-zinc-950 border-zinc-800">
                            <DropdownMenuItem onClick={() => setEditOpen(true)} className="text-zinc-300 focus:bg-zinc-900 focus:text-zinc-100 cursor-pointer">
                                <Edit2 className="w-4 h-4 mr-2" /> Rename Context
                            </DropdownMenuItem>
                            <AlertDialog>
                                <AlertDialogTrigger asChild>
                                    <DropdownMenuItem onSelect={(e) => e.preventDefault()} className="text-red-400 focus:bg-red-500/10 focus:text-red-400 cursor-pointer">
                                        <Trash2 className="w-4 h-4 mr-2" /> Obliterate Identity
                                    </DropdownMenuItem>
                                </AlertDialogTrigger>
                                <AlertDialogContent className="bg-zinc-950 border-zinc-800">
                                    <AlertDialogHeader>
                                        <AlertDialogTitle className="text-zinc-100">Destructive Sequence Blocked</AlertDialogTitle>
                                        <AlertDialogDescription className="text-zinc-400">
                                            This execution securely obliterates "{project.name}" decoupling embedded native indexing vectors aggressively tracking natively over context chains.
                                        </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                        <AlertDialogCancel className="bg-zinc-900 border-zinc-800 text-zinc-300 hover:bg-zinc-800 hover:text-white">Bypass</AlertDialogCancel>
                                        <AlertDialogAction
                                            className="bg-red-500/20 text-red-500 border border-red-500/50 hover:bg-red-500 hover:text-white font-bold"
                                            onClick={() => deleteProject(project.id)}
                                        >
                                            Execute Purge
                                        </AlertDialogAction>
                                    </AlertDialogFooter>
                                </AlertDialogContent>
                            </AlertDialog>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>

                {/* Invisible Modal mapping securely */}
                <EditProjectModal project={project} open={editOpen} onClose={() => setEditOpen(false)} />
            </CardFooter>
        </Card>
    );
}
