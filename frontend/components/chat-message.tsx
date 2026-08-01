"use client";

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';

interface CitationSource {
    pdf_id: string;
    filename: string;
    page: number;
    text: string;
    score?: number;
}

interface ChatMessageProps {
    role: string;
    content: string;
    sources?: CitationSource[];
}

export function ChatMessage({ role, content, sources }: ChatMessageProps) {
    const isUser = role === 'user';

    // Regex conversion isolating standard brackets identifying references seamlessly linking natively implicitly perfectly effectively
    const preprocessContent = (text: string) => {
        return text.replace(/\[([^\]]+?),\s*p\.(\d+)\]/g, (match, filename, page) => {
            return `[CITATION:${filename}:${page}](${match})`;
        });
    };

    const processLinks = ({ href, children }: any) => {
        if (href && href.startsWith('[CITATION:')) {
            const rawText = children[0] || href;

            // Search explicitly through JSON boundaries intuitively resolving source metadata accurately securely
            const matchedSource = sources?.find(s =>
                rawText.includes(s.filename) &&
                rawText.includes(`p.${s.page}`)
            );

            return (
                <Popover>
                    <PopoverTrigger className="text-xs font-extrabold tracking-tight bg-blue-100 text-blue-700 px-2 flex-inline rounded-sm border border-blue-200 mx-1 cursor-pointer transition-colors hover:bg-blue-200 shadow-sm align-middle">
                        {rawText}
                    </PopoverTrigger>
                    {matchedSource && (
                        <PopoverContent className="w-80 shadow-xl border-slate-200 p-4">
                            <h4 className="text-sm font-black tracking-tight text-slate-800 pb-2 border-b border-slate-100">Source: {matchedSource.filename}</h4>
                            <p className="text-xs text-slate-500 font-bold uppercase tracking-widest mt-2 mb-1">Page Reference: {matchedSource.page}</p>
                            <div className="text-xs font-medium text-slate-700 mt-2 p-3 bg-slate-50 border border-slate-100 rounded-md leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
                                "{matchedSource.text}"
                            </div>
                        </PopoverContent>
                    )}
                </Popover>
            );
        }
        return <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-bold inline">{children}</a>;
    };

    return (
        <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-2xl px-6 py-5 shadow-sm ${isUser
                    ? 'bg-slate-900 text-white rounded-br-sm'
                    : 'bg-white border border-slate-200 text-slate-800 rounded-bl-sm'
                }`}>
                {!isUser && <div className="text-[10px] uppercase tracking-widest font-extrabold text-blue-600 mb-2">Research Architecture Bound Context</div>}

                <div className={`prose prose-sm prose-slate max-w-none break-words ${isUser ? 'prose-invert font-medium' : ''}`}>
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{ a: processLinks }}
                    >
                        {preprocessContent(content)}
                    </ReactMarkdown>
                </div>
            </div>
        </div>
    );
}
