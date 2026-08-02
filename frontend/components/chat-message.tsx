"use client";

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Sparkles } from 'lucide-react';
import { PrismLight as SyntaxHighlighter } from 'react-syntax-highlighter';
import ts from 'react-syntax-highlighter/dist/cjs/languages/prism/typescript';
import py from 'react-syntax-highlighter/dist/cjs/languages/prism/python';
import js from 'react-syntax-highlighter/dist/cjs/languages/prism/javascript';
import bash from 'react-syntax-highlighter/dist/cjs/languages/prism/bash';
import json from 'react-syntax-highlighter/dist/cjs/languages/prism/json';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';

SyntaxHighlighter.registerLanguage('typescript', ts);
SyntaxHighlighter.registerLanguage('python', py);
SyntaxHighlighter.registerLanguage('javascript', js);
SyntaxHighlighter.registerLanguage('bash', bash);
SyntaxHighlighter.registerLanguage('json', json);

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
    onCitationClick?: (source: CitationSource) => void;
    isStreaming?: boolean;
}

export function ChatMessage({ role, content, sources, onCitationClick, isStreaming }: ChatMessageProps) {
    const isUser = role === 'user';

    const preprocessContent = (text: string) => {
        return text.replace(/\[([^\]]+?),\s*p\.(\d+)\]/g, (match, filename, page) => {
            return `[CITATION:${filename}:${page}](${match})`;
        });
    };

    const processLinks = ({ href, children }: any) => {
        if (href && href.startsWith('[CITATION:')) {
            const rawText = children[0] || href;

            const matchedSource = sources?.find(s =>
                rawText.includes(s.filename) &&
                rawText.includes(`p.${s.page}`)
            );

            return (
                <span
                    onClick={() => onCitationClick && matchedSource && onCitationClick(matchedSource)}
                    className="text-xs font-black tracking-tight text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded cursor-pointer hover:bg-cyan-500/20 transition-colors mx-0.5 align-super hover:underline decoration-cyan-500/50"
                >
                    {rawText}
                </span>
            );
        }
        return <a href={href} target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline font-bold">{children}</a>;
    };

    return (
        <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-end max-w-[85%] gap-2`}>

                {/* Avatar */}
                <div className="shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-zinc-900 border border-zinc-800">
                    {isUser ? <User className="w-5 h-5 text-zinc-400" /> : <Sparkles className="w-4 h-4 text-cyan-500" />}
                </div>

                {/* Message Bubble */}
                <div className={`p-4 shadow-sm relative ${isUser
                        ? 'bg-zinc-800 text-zinc-100 rounded-2xl rounded-br-sm'
                        : 'bg-zinc-950 border border-zinc-800 text-zinc-200 rounded-2xl rounded-bl-sm'
                    }`}>
                    <div className={`prose prose-sm max-w-none break-words prose-invert ${isUser ? 'font-medium' : ''}`}>
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                                a: processLinks,
                                p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
                                code({ node, inline, className, children, ...props }: any) {
                                    const match = /language-(\w+)/.exec(className || '');
                                    const isCodeBlock = !inline && match;

                                    if (isCodeBlock) {
                                        return (
                                            <div className="relative mt-4 mb-4 rounded-xl overflow-hidden border border-zinc-800 bg-zinc-950 shadow-2xl">
                                                <div className="flex items-center px-4 py-2 bg-zinc-900 border-b border-zinc-800">
                                                    <div className="text-[10px] font-black tracking-widest uppercase text-zinc-500">{match[1]}</div>
                                                </div>
                                                <SyntaxHighlighter
                                                    {...props}
                                                    style={vscDarkPlus as any}
                                                    language={match[1]}
                                                    PreTag="div"
                                                    customStyle={{ margin: 0, background: 'transparent', padding: '1rem', fontSize: '13px' }}
                                                >
                                                    {String(children).replace(/\n$/, '')}
                                                </SyntaxHighlighter>
                                            </div>
                                        );
                                    }
                                    return (
                                        <code {...props} className="bg-zinc-800 text-cyan-200 px-1.5 py-0.5 rounded font-mono text-sm border border-zinc-700/50">
                                            {children}
                                        </code>
                                    );
                                }
                            }}
                        >
                            {preprocessContent(content)}
                        </ReactMarkdown>
                    </div>

                    {isStreaming && (
                        <div className="inline-block mt-1">
                            <div className="w-2.5 h-4 bg-cyan-500 animate-pulse rounded-sm opacity-80" />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
