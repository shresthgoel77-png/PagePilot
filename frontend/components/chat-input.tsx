"use client";

import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Paperclip, CheckSquare, Square, Send, Loader2 } from 'lucide-react';
import { usePdfs } from '@/hooks/usePdfs';

interface ChatInputProps {
    projectId: string;
    onSend: (message: string, contextPdfIds: string[]) => void;
    disabled?: boolean;
}

export function ChatInput({ projectId, onSend, disabled }: ChatInputProps) {
    const [message, setMessage] = useState('');
    const [selectedPdfIds, setSelectedPdfIds] = useState<string[]>([]);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const { data: pdfs } = usePdfs(projectId);

    const handleSend = () => {
        if (!message.trim() || disabled) return;
        onSend(message, selectedPdfIds);
        setMessage('');
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const togglePdfSelection = (id: string) => {
        setSelectedPdfIds(prev =>
            prev.includes(id) ? prev.filter(pid => pid !== id) : [...prev, id]
        );
    };

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'inherit';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
        }
    }, [message]);

    return (
        <div className="flex flex-col bg-zinc-900 border border-zinc-800 rounded-2xl shadow-xl overflow-hidden p-3 transition-all focus-within:ring-1 focus-within:ring-cyan-500/50">
            {selectedPdfIds.length > 0 && (
                <div className="flex items-center gap-2 mb-2 px-2 overflow-x-auto">
                    {selectedPdfIds.map(id => {
                        const pdf = pdfs?.find((p: any) => p.id === id);
                        return pdf ? (
                            <div key={id} className="text-[10px] bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-1 rounded truncate max-w-[150px] shrink-0 font-bold tracking-tight">
                                {pdf.filename}
                            </div>
                        ) : null;
                    })}
                </div>
            )}

            <Textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about your contextual project constraints..."
                className="min-h-[48px] max-h-[120px] bg-transparent border-0 focus-visible:ring-0 shadow-none resize-none px-2 py-1 text-zinc-100 placeholder:text-zinc-600 font-medium"
                disabled={disabled}
            />

            <div className="flex justify-between items-center mt-2 px-1">
                <Popover>
                    <PopoverTrigger asChild>
                        <Button variant="ghost" size="sm" className="h-8 px-2 text-zinc-400 hover:text-cyan-400 hover:bg-cyan-500/10 rounded-lg">
                            <Paperclip className="w-4 h-4 mr-1.5" />
                            <span className="text-xs font-bold">Context ({selectedPdfIds.length})</span>
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent side="top" align="start" className="w-72 bg-zinc-950 border-zinc-800 p-2 shadow-2xl">
                        <div className="text-xs font-black text-white px-2 py-1 mb-2 border-b border-zinc-800 uppercase tracking-widest">Select Indexed Vaults</div>
                        <div className="space-y-1 max-h-48 overflow-y-auto">
                            {pdfs?.length === 0 && <p className="text-xs text-zinc-600 px-2 py-4">No PDFs structured within project naturally.</p>}
                            {pdfs?.map((pdf: any) => (
                                <div
                                    key={pdf.id}
                                    onClick={() => togglePdfSelection(pdf.id)}
                                    className="flex items-center px-2 py-2 hover:bg-zinc-900 rounded cursor-pointer group"
                                >
                                    <div className="text-cyan-500 mr-2 shrink-0">
                                        {selectedPdfIds.includes(pdf.id) ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity" />}
                                    </div>
                                    <div className="truncate text-xs font-medium text-zinc-300 group-hover:text-cyan-400 transition-colors">
                                        {pdf.filename}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </PopoverContent>
                </Popover>

                <Button
                    onClick={handleSend}
                    disabled={!message.trim() || disabled}
                    size="sm"
                    className="font-black tracking-tight rounded-xl h-10 px-6 bg-cyan-500 text-zinc-950 hover:bg-cyan-400 transition-all active:scale-95 disabled:bg-zinc-800 disabled:text-zinc-600 shadow-[0_0_15px_rgba(6,182,212,0.3)] disabled:shadow-none"
                >
                    {disabled ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4 mr-2" /> Inject</>}
                </Button>
            </div>
        </div>
    );
}
