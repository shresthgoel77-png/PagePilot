"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUIStore } from "@/stores/uiStore";
import {
    CommandDialog,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
    CommandSeparator,
    CommandShortcut,
} from "@/components/ui/command";
import { LayoutDashboard, Folder, Hexagon, Settings, Plus, UploadCloud } from "lucide-react";

export function CommandPalette() {
    const { commandPaletteOpen, setCommandPaletteOpen } = useUIStore();
    const router = useRouter();

    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const runCommand = (command: () => void) => {
        setCommandPaletteOpen(false);
        command();
    };

    if (!mounted) return null;

    return (
        <CommandDialog open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen}>
            <CommandInput placeholder="Type a command or search metrics..." className="h-14 font-medium" />
            <CommandList className="py-2">
                <CommandEmpty className="text-zinc-500 font-bold tracking-tight text-center p-6">No matching executions found natively.</CommandEmpty>

                <CommandGroup heading="System Views">
                    <CommandItem onSelect={() => runCommand(() => router.push("/dashboard"))} className="cursor-pointer aria-selected:bg-cyan-500/10 aria-selected:text-cyan-400 focus:bg-cyan-500/10 focus:text-cyan-400">
                        <LayoutDashboard className="mr-2 h-4 w-4" />
                        <span>Command Center</span>
                    </CommandItem>
                    <CommandItem onSelect={() => runCommand(() => router.push("/projects"))} className="cursor-pointer aria-selected:bg-cyan-500/10 aria-selected:text-cyan-400 focus:bg-cyan-500/10 focus:text-cyan-400">
                        <Folder className="mr-2 h-4 w-4" />
                        <span>Projects Hub</span>
                    </CommandItem>
                    <CommandItem onSelect={() => runCommand(() => router.push("/projects"))} className="cursor-pointer aria-selected:bg-cyan-500/10 aria-selected:text-cyan-400 focus:bg-cyan-500/10 focus:text-cyan-400">
                        <Hexagon className="mr-2 h-4 w-4" />
                        <span>Vault Configurations</span>
                    </CommandItem>
                </CommandGroup>

                <CommandSeparator className="bg-zinc-800/50 my-2" />

                <CommandGroup heading="Quick Execution Bounds">
                    <CommandItem onSelect={() => runCommand(() => router.push("/dashboard?new=true"))} className="cursor-pointer aria-selected:bg-cyan-500/10 aria-selected:text-cyan-400 focus:bg-cyan-500/10 focus:text-cyan-400">
                        <Plus className="mr-2 h-4 w-4" />
                        <span>Initialize Project Matrix</span>
                        <CommandShortcut>⌘N</CommandShortcut>
                    </CommandItem>
                    <CommandItem onSelect={() => runCommand(() => router.push("/projects"))} className="cursor-pointer aria-selected:bg-cyan-500/10 aria-selected:text-cyan-400 focus:bg-cyan-500/10 focus:text-cyan-400">
                        <UploadCloud className="mr-2 h-4 w-4" />
                        <span>Inject PDF Variables</span>
                        <CommandShortcut>⌘U</CommandShortcut>
                    </CommandItem>
                    <CommandItem onSelect={() => runCommand(() => console.log("Shortcuts Triggered"))} className="cursor-pointer aria-selected:bg-cyan-500/10 aria-selected:text-cyan-400 focus:bg-cyan-500/10 focus:text-cyan-400">
                        <Settings className="mr-2 h-4 w-4" />
                        <span>Access Global Preferences</span>
                        <CommandShortcut>⌘/</CommandShortcut>
                    </CommandItem>
                </CommandGroup>
            </CommandList>
        </CommandDialog>
    );
}
