import { useState } from 'react';
import { useCreateProject } from '@/hooks/useProjects';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';


export function CreateProjectModal() {
    const [open, setOpen] = useState(false);
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const { mutate: createProject, isPending } = useCreateProject();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        createProject(
            { name, description },
            {
                onSuccess: () => {
                    setName('');
                    setDescription('');
                    setOpen(false);
                }
            }
        );
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700 font-semibold shadow-sm">+ Launch New Project</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle className="text-xl">Architect New Research</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 pt-2">
                    <div className="space-y-2">
                        <label className="text-sm font-semibold text-slate-700">Project Descriptor</label>
                        <Input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Enter bounded parameter context..."
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
                            placeholder="Optional metadata extending architectural intents..."
                            disabled={isPending}
                            maxLength={500}
                        />
                    </div>
                    <Button type="submit" className="w-full" disabled={isPending || !name.trim()}>
                        {isPending ? 'Syncing Configurations...' : 'Deploy Initialization'}
                    </Button>
                </form>
            </DialogContent>
        </Dialog>
    );
}
