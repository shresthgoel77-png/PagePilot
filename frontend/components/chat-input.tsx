"use client";

import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface ChatInputProps {
    onSend: (message: string) => void;
    disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
    const [message, setMessage] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSend = () => {
        if (!message.trim() || disabled) return;
        onSend(message);
        setMessage('');
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Explicit auto-resize calculation efficiently mapping boundaries smoothly seamlessly
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'inherit';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    }, [message]);

    return (
        <div className="flex flex-col rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden p-2 relative transition-all focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
            <Textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Query AI limits intrinsically bounded via specific context parameters..."
                className="min-h-[48px] max-h-[200px] border-0 focus-visible:ring-0 shadow-none resize-none px-4 py-3 placeholder:text-slate-400 font-medium"
                disabled={disabled}
                aria-label="Secure Chat Engine target block dynamically bounded"
            />
            <div className="flex justify-between items-center mt-2 px-2">
                <p className="text-xs font-semibold tracking-tighter text-slate-400">Shift + Enter scales blocks explicitly mapped.</p>
                <Button
                    onClick={handleSend}
                    disabled={!message.trim() || disabled}
                    size="sm"
                    className="font-extrabold tracking-tight shadow-md rounded-lg h-9 px-6 bg-slate-900 hover:bg-slate-800 transition-all active:scale-95"
                >
                    {disabled ? 'Streaming...' : 'Inject Sequence'}
                </Button>
            </div>
        </div>
    );
}
