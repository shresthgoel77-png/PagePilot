import { useState, useEffect } from 'react';
import { useUpdateProject } from '@/hooks/useProjects';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Loader2 } from 'lucide-react';

interface EditProjectModalProps {
    project: { id: string; name: string; description?: string | null };
    open: boolean;
    onClose: () => void;
}

export function EditProjectModal({ project, open, onClose }: EditProjectModalProps) {
    const [name, setName] = useState(project.name);
    const [description, setDescription] = useState(project.description || '');
    const { mutate: updateProject, isPending } = useUpdateProject();

    useEffect(() => {
        if (open) {
            setName(project.name);
            setDescription(project.description || '');
        }
    }, [open, project]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        updateProject(
            { id: project.id, data: { name, description } },
            {
                onSuccess: () => {
                    onClose();
                }
            }
        );
    };

    return (
        <Dialog open={open} onOpenChange={(val) => !val && onClose()}>
            <DialogContent className="sm:max-w-[425px] bg-zinc-950 border-zinc-800 text-zinc-100 shadow-2xl">
                <DialogHeader>
                    <DialogTitle className="text-xl font-bold tracking-tight">Reconfigure Workspace</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-6 pt-4">
                    <div className="space-y-2">
                        <label className="text-sm font-semibold text-zinc-300">Project Identity</label>
                        <Input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                            disabled={isPending}
                            maxLength={100}
                            className="bg-zinc-900 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-cyan-500"
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-semibold text-zinc-300">Contextual Descriptor</label>
                        <Textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            disabled={isPending}
                            maxLength={500}
                            className="bg-zinc-900 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-cyan-500 min-h-[100px] resize-none"
                        />
                    </div>
                    <Button type="submit" className="w-full bg-cyan-500 hover:bg-cyan-400 text-zinc-950 font-bold" disabled={isPending || !name.trim()}>
                        {isPending ? (
                            <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Saving Configurations...</>
                        ) : 'Confirm Overrides'}
                    </Button>
                </form>
            </DialogContent>
        </Dialog>
    );
}
