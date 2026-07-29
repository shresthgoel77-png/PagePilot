import { useState, useEffect } from 'react';
import { useUpdateProject } from '@/hooks/useProjects';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

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
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle className="text-xl">Reconfigure Boundaries</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 pt-2">
                    <div className="space-y-2">
                        <label className="text-sm font-semibold text-slate-700">Project Descriptor</label>
                        <Input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                            disabled={isPending}
                            maxLength={100}
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-semibold text-slate-700">Scope Overview</label>
                        <Textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            disabled={isPending}
                            maxLength={500}
                        />
                    </div>
                    <Button type="submit" className="w-full" disabled={isPending || !name.trim()}>
                        {isPending ? 'Propagating Variables...' : 'Confirm Overrides'}
                    </Button>
                </form>
            </DialogContent>
        </Dialog>
    );
}
