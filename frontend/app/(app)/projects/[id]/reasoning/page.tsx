"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { usePdfs } from "@/hooks/usePdfs";
import { useReasoningStream } from "@/hooks/useAnalysis";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { CheckSquare, Square, FileText, BrainCircuit, Loader2, GitCompare, CheckCircle, Copy } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import { toast } from "sonner";

export default function ReasoningDashboard() {
    const params = useParams();
    const projectId = params.id as string;

    const { data: pdfs } = usePdfs(projectId);
    const { content, isStreaming, executeReasoning } = useReasoningStream(projectId);

    const [selectedPdfIds, setSelectedPdfIds] = useState<string[]>([]);
    const [query, setQuery] = useState("");

    const togglePdfSelection = (id: string) => {
        setSelectedPdfIds(prev =>
            prev.includes(id) ? prev.filter(pid => pid !== id) : [...prev, id]
        );
    };

    const handleExecute = () => {
        if (selectedPdfIds.length < 2) {
            toast.error("Reasoning comparisons specifically require 2 or more vectors active internally.");
            return;
        }
        if (!query.trim()) {
            toast.error("Research queries must exist intrinsically triggering logical structures.");
            return;
        }
        executeReasoning(query, selectedPdfIds, "compare");
    };

    const copyToClipboard = (text: string, title: string) => {
        navigator.clipboard.writeText(text);
        toast.success(`Copied ${title} bound securely to clipboard natively.`);
    };

    // Very naive streaming parser evaluating SSE boundaries dynamically breaking into sections.
    // In production, robust regex matching headers dynamically would apply elegantly here.
    const sections = {
        summary: content.split("## Differences")[0] || "",
        differences: content.includes("## Differences") ? content.split("## Differences")[1]?.split("## Agreements")[0] || "" : "",
        agreements: content.includes("## Agreements") ? content.split("## Agreements")[1] || "" : ""
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 pb-32">
            <div className="flex justify-between items-end">
                <div className="space-y-2">
                    <h1 className="text-3xl font-black text-white tracking-tight flex items-center">
                        <BrainCircuit className="w-8 h-8 mr-3 text-cyan-500" /> Multi-Paper Synthesis
                    </h1>
                    <p className="text-zinc-400 font-medium">Inject matrices scaling intelligent contextual evaluations bridging active vaults securely natively.</p>
                </div>
            </div>

            {/* Input Config bounds */}
            <div className="bg-zinc-950 border border-zinc-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-[100px] pointer-events-none"></div>

                <h3 className="text-sm font-black text-zinc-300 uppercase tracking-widest mb-4">1. Initialize Vault Matrix</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
                    {pdfs?.map((pdf: any) => {
                        const isSelected = selectedPdfIds.includes(pdf.id);
                        return (
                            <div
                                key={pdf.id}
                                onClick={() => togglePdfSelection(pdf.id)}
                                className={`flex items-start p-3 rounded-xl border cursor-pointer transition-all ${isSelected
                                        ? 'bg-cyan-500/10 border-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.1)] ring-1 ring-cyan-500/20'
                                        : 'bg-zinc-900 border-zinc-800 hover:border-zinc-700'
                                    }`}
                            >
                                <div className={`mt-0.5 mr-3 shrink-0 ${isSelected ? 'text-cyan-400' : 'text-zinc-500'}`}>
                                    {isSelected ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4" />}
                                </div>
                                <div className={`text-xs font-bold truncate ${isSelected ? 'text-zinc-100' : 'text-zinc-400'}`}>
                                    {pdf.filename}
                                </div>
                            </div>
                        );
                    })}
                    {pdfs?.length === 0 && (
                        <div className="col-span-full p-4 border border-zinc-800 border-dashed rounded-xl text-center text-xs text-zinc-500 font-bold uppercase tracking-widest">No Context Variables Present</div>
                    )}
                </div>

                <h3 className="text-sm font-black text-zinc-300 uppercase tracking-widest mb-4">2. Bounding Research Parameter</h3>
                <div className="relative mb-6 ring-1 ring-zinc-800 rounded-xl overflow-hidden focus-within:ring-cyan-500 transition-all bg-zinc-900 shadow-inner">
                    <Textarea
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Define rigid bounds explicitly resolving internal discrepancies actively mapping matrices securely..."
                        className="bg-transparent border-none focus-visible:ring-0 min-h-[120px] resize-none text-zinc-100 font-medium px-4 py-3 placeholder:text-zinc-600"
                    />
                </div>

                <Button
                    onClick={handleExecute}
                    disabled={isStreaming || selectedPdfIds.length < 2 || !query.trim()}
                    className="w-full md:w-auto md:px-12 h-12 rounded-xl bg-cyan-500 text-zinc-950 font-black tracking-tight hover:bg-cyan-400 disabled:bg-zinc-800 disabled:text-zinc-500 transition-all active:scale-95 shadow-[0_0_20px_rgba(6,182,212,0.3)] disabled:shadow-none"
                >
                    {isStreaming ? (
                        <><Loader2 className="w-5 h-5 mr-3 animate-spin" /> Cross-referencing documents...</>
                    ) : (
                        <><BrainCircuit className="w-5 h-5 mr-3" /> Initiate Synthesis Matrix</>
                    )}
                </Button>
            </div>

            {/* Results Bento Grid */}
            {(content || isStreaming) && (
                <div className="space-y-6 pt-4">
                    <h2 className="text-xl font-black text-white tracking-tight flex items-center mb-6">
                        <span className="w-2 h-2 rounded-full bg-cyan-500 mr-3 animate-pulse"></span>
                        Evaluated Output Constructs
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                        {/* Summary Card */}
                        <Card className="bg-zinc-950 border-zinc-800 md:col-span-3 lg:col-span-1 shadow-2xl relative transition-all group overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"></div>
                            <CardHeader className="border-b border-zinc-800/50 pb-4 relative z-10 flex flex-row items-center justify-between">
                                <div className="space-y-1">
                                    <CardTitle className="text-zinc-100 flex items-center font-black tracking-tight text-lg">
                                        <FileText className="w-5 h-5 mr-2 text-cyan-500" /> Synthesized Core
                                    </CardTitle>
                                    <CardDescription className="text-zinc-500 font-medium text-xs">Axiomatic foundation mapping dynamically.</CardDescription>
                                </div>
                                <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-500 hover:text-cyan-400" onClick={() => copyToClipboard(sections.summary, "Core Synthesis")}>
                                    <Copy className="w-4 h-4" />
                                </Button>
                            </CardHeader>
                            <CardContent className="pt-6 relative z-10">
                                {isStreaming && !sections.summary ? (
                                    <div className="space-y-2"><div className="h-4 bg-zinc-900 rounded animate-pulse w-full"></div><div className="h-4 bg-zinc-900 rounded animate-pulse w-5/6"></div></div>
                                ) : (
                                    <div className="prose prose-sm prose-invert max-w-none text-zinc-300 font-medium">
                                        <ReactMarkdown>{sections.summary.replace("## Summary", "")}</ReactMarkdown>
                                    </div>
                                )}
                            </CardContent>
                        </Card>

                        {/* Differences Card */}
                        <Card className="bg-zinc-950 border-zinc-800 md:col-span-2 lg:col-span-1 shadow-2xl relative transition-all group overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"></div>
                            <CardHeader className="border-b border-zinc-800/50 pb-4 relative z-10 flex flex-row items-center justify-between">
                                <div className="space-y-1">
                                    <CardTitle className="text-amber-50 flex items-center font-black tracking-tight text-lg">
                                        <GitCompare className="w-5 h-5 mr-2 text-amber-500" /> Bounded Divergence
                                    </CardTitle>
                                    <CardDescription className="text-zinc-500 font-medium text-xs">Methodological discrepancies mapped securely.</CardDescription>
                                </div>
                                <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-500 hover:text-amber-400" onClick={() => copyToClipboard(sections.differences, "Divergence")}>
                                    <Copy className="w-4 h-4" />
                                </Button>
                            </CardHeader>
                            <CardContent className="pt-6 relative z-10">
                                {isStreaming && !sections.differences ? (
                                    <div className="space-y-2"><div className="h-4 bg-zinc-900 rounded animate-pulse w-full"></div><div className="h-4 bg-zinc-900 rounded animate-pulse w-4/6"></div></div>
                                ) : (
                                    <div className="prose prose-sm prose-invert max-w-none text-zinc-300 font-medium">
                                        <ReactMarkdown>{sections.differences}</ReactMarkdown>
                                    </div>
                                )}
                            </CardContent>
                        </Card>

                        {/* Agreements Card */}
                        <Card className="bg-zinc-950 border-zinc-800 lg:col-span-1 shadow-2xl relative transition-all group overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"></div>
                            <CardHeader className="border-b border-zinc-800/50 pb-4 relative z-10 flex flex-row items-center justify-between">
                                <div className="space-y-1">
                                    <CardTitle className="text-green-50 flex items-center font-black tracking-tight text-lg">
                                        <CheckCircle className="w-5 h-5 mr-2 text-green-500" /> Empirical Consensus
                                    </CardTitle>
                                    <CardDescription className="text-zinc-500 font-medium text-xs">Convergent theories structurally evaluated.</CardDescription>
                                </div>
                                <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-500 hover:text-green-400" onClick={() => copyToClipboard(sections.agreements, "Consensus")}>
                                    <Copy className="w-4 h-4" />
                                </Button>
                            </CardHeader>
                            <CardContent className="pt-6 relative z-10">
                                {isStreaming && !sections.agreements ? (
                                    <div className="space-y-2"><div className="h-4 bg-zinc-900 rounded animate-pulse w-full"></div><div className="h-4 bg-zinc-900 rounded animate-pulse w-3/4"></div></div>
                                ) : (
                                    <div className="prose prose-sm prose-invert max-w-none text-zinc-300 font-medium">
                                        <ReactMarkdown>{sections.agreements}</ReactMarkdown>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </div>
            )}
        </div>
    );
}
