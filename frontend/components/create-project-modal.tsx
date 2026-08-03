import { useState } from 'react';
import { useCreateProject } from '@/hooks/useProjects';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Loader2 } from 'lucide-react';

export function CreateProjectModal({ children }: { children?: React.ReactNode }) {
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
                {children ? children : (
                    <Button className="bg-cyan-500 hover:bg-cyan-400 text-zinc-950 font-bold shadow-[0_0_10px_rgba(6,182,212,0.3)] hover:shadow-[0_0_20px_rgba(6,182,212,0.5)] transition-all duration-300">
                        <Plus className="w-4 h-4 mr-2" /> Create Project
                    </Button>
                )}
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px] bg-zinc-950 border-zinc-800 text-zinc-100 shadow-2xl">
                <DialogHeader>
                    <DialogTitle className="text-xl font-bold tracking-tight">Architect Workspace</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-6 pt-4">
                    <div className="space-y-2">
                        <label className="text-sm font-semibold text-zinc-300">Project Identity <span className="text-red-500">*</span></label>
                        <Input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Quantum Mechanics Corpus..."
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
                            placeholder="Optional metadata constraints embedding deeply natively..."
                            disabled={isPending}
                            maxLength={500}
                            className="bg-zinc-900 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-cyan-500 min-h-[100px] resize-none"
                        />
                    </div>
                    <Button
                        type="submit"
                        className="w-full bg-cyan-500 hover:bg-cyan-400 text-zinc-950 font-bold"
                        disabled={isPending || !name.trim()}
                    >
                        {isPending ? (
                            <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Provisioning Matrix...</>
                        ) : 'Deploy Architecture'}
                    </Button>
                </form>
            </DialogContent>
        </Dialog>
    );
}
