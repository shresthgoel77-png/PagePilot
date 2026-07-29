import { useState } from 'react';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useDeleteProject } from '@/hooks/useProjects';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { EditProjectModal } from './edit-project-modal';

interface ProjectProps {
    id: string;
    name: string;
    description?: string | null;
    updated_at: string;
}

export function ProjectCard({ project }: { project: ProjectProps }) {
    const { mutate: deleteProject, isPending: isDeleting } = useDeleteProject();
    const [editOpen, setEditOpen] = useState(false);

    return (
        <Card className="flex flex-col shadow-sm hover:shadow-md transition-shadow bg-white">
            <CardHeader className="flex-1">
                <CardTitle className="line-clamp-1 text-lg">{project.name}</CardTitle>
                <CardDescription className="line-clamp-2 mt-2 h-10 text-xs">
                    {project.description || "No context descriptors injected."}
                </CardDescription>
            </CardHeader>
            <CardContent>
                <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-widest">
                    Refresh: {formatDistanceToNow(new Date(project.updated_at), { addSuffix: true })}
                </p>
            </CardContent>
            <CardFooter className="flex gap-2 justify-end border-t pt-4 bg-slate-50">
                <Link href={`/dashboard/projects/${project.id}`}>
                    <Button variant="outline" size="sm" className="font-semibold shadow-sm">Enter</Button>
                </Link>

                <Button variant="secondary" size="sm" onClick={() => setEditOpen(true)} className="shadow-sm">Edit</Button>

                <AlertDialog>
                    <AlertDialogTrigger asChild>
                        <Button variant="destructive" size="sm" disabled={isDeleting} className="shadow-sm font-bold">Wipe</Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                        <AlertDialogHeader>
                            <AlertDialogTitle>Destructive Constraint Notice</AlertDialogTitle>
                            <AlertDialogDescription className="text-slate-600">
                                This execution sequence obliterates the logical environment implicitly securely.
                                Project <strong>{project.name}</strong> alongside nested PDFs and decoupled Vector hashes will be eradicated totally naturally.
                            </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                            <AlertDialogCancel className="font-semibold">Bypass</AlertDialogCancel>
                            <AlertDialogAction
                                className="bg-red-600 hover:bg-red-700 text-white font-bold tracking-tight"
                                onClick={() => deleteProject(project.id)}
                            >
                                Execute Purge
                            </AlertDialogAction>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialog>

                <EditProjectModal project={project} open={editOpen} onClose={() => setEditOpen(false)} />
            </CardFooter>
        </Card>
    );
}
