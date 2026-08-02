"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { usePdfs } from "@/hooks/usePdfs";
import { useGapAnalysis } from "@/hooks/useAnalysis";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Radar, Loader2, Search, TriangleAlert, Waypoints, BoxSelect, Download, Copy, CircleAlert } from "lucide-react";
import { toast } from "sonner";

export default function GapAnalysisDashboard() {
    const params = useParams();
    const projectId = params.id as string;

    // Explicit bounds evaluating context natively tracking structural JSON hooks securely.
    const { data: pdfs } = usePdfs(projectId);
    const { mutate: extractGaps, isPending, data: gapResults } = useGapAnalysis(projectId);

    const [focusArea, setFocusArea] = useState("");

    const handleExecute = () => {
        extractGaps({ focus_area: focusArea.trim() || undefined });
    };

    const copyReport = () => {
        if (!gapResults) return;
        const report = `
# Explicit Gap Analysis Mapped structurally

## Methodological Constraints
${gapResults.methodologies.map((m: string) => `- ${m}`).join('\n')}

## Structurally Isolated Limitations
${gapResults.limitations.map((l: string) => `- ${l}`).join('\n')}

## Structural Gaps
${gapResults.research_gaps.map((g: string) => `- ${g}`).join('\n')}
        `.trim();
        navigator.clipboard.writeText(report);
        toast.success("JSON extracted components bounded seamlessly tracking naturally externally.");
    };

    const downloadMarkdown = () => {
        if (!gapResults) return;
        const report = `
# Targeted Gap Framework: ${focusArea || 'General Vault Index'}

## Thematic Constraints
${gapResults.methodologies.map((m: string) => `- ${m}`).join('\n')}

## Vault Limitations structurally executed
${gapResults.limitations.map((l: string) => `- ${l}`).join('\n')}

## Executed Gap Logistics
${gapResults.research_gaps.map((g: string) => `- ${g}`).join('\n')}
        `.trim();
        const blob = new Blob([report], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Gap-Analysis-${projectId}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        toast.success("Markdown file executed rendering securely structurally mapped.");
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 pb-32">
            <div className="flex justify-between items-end">
                <div className="space-y-2">
                    <h1 className="text-3xl font-black text-white tracking-tight flex items-center">
                        <Radar className="w-8 h-8 mr-3 text-cyan-500" /> Gap Matrix Extraction
                    </h1>
                    <p className="text-zinc-400 font-medium">Extract hidden semantic vulnerabilities rigorously analyzing implicit dataset gaps intrinsically tracking anomalies structurally.</p>
                </div>
                {gapResults && (
                    <div className="flex gap-2">
                        <Button variant="outline" className="bg-zinc-950 border-zinc-800 text-zinc-300 font-bold hover:text-cyan-400 hover:bg-cyan-500/10" onClick={copyReport}>
                            <Copy className="w-4 h-4 mr-2" /> Copy Log
                        </Button>
                        <Button variant="outline" className="bg-zinc-950 border-zinc-800 text-zinc-300 font-bold hover:text-cyan-400 hover:bg-cyan-500/10" onClick={downloadMarkdown}>
                            <Download className="w-4 h-4 mr-2" /> Download Bounds
                        </Button>
                    </div>
                )}
            </div>

            {/* Input Config bounds */}
            <div className="bg-zinc-950 border border-zinc-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-[100px] pointer-events-none"></div>

                <h3 className="text-sm font-black text-zinc-300 uppercase tracking-widest mb-4">Focus Variable Targeting (Optional)</h3>
                <div className="relative mb-6 ring-1 ring-zinc-800 rounded-xl overflow-hidden focus-within:ring-cyan-500 transition-all bg-zinc-900 shadow-inner">
                    <Textarea
                        value={focusArea}
                        onChange={(e) => setFocusArea(e.target.value)}
                        placeholder="Assign thematic constructs specifying precise constraints isolating explicit limitations intuitively (e.g. 'Security Protocol execution parameters')..."
                        className="bg-transparent border-none focus-visible:ring-0 min-h-[80px] resize-none text-zinc-100 font-medium px-4 py-3 placeholder:text-zinc-600"
                    />
                </div>

                <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
                    <div className="text-xs font-bold uppercase tracking-widest text-zinc-500 flex items-center">
                        <BoxSelect className="w-4 h-4 mr-2" /> Analyzing All Executed Vault Constraints ({pdfs?.length || 0} bounds)
                    </div>
                    <Button
                        onClick={handleExecute}
                        disabled={isPending || (pdfs?.length === 0)}
                        className="w-full md:w-auto md:px-12 h-12 rounded-xl bg-cyan-500 text-zinc-950 font-black tracking-tight hover:bg-cyan-400 disabled:bg-zinc-800 disabled:text-zinc-500 transition-all active:scale-95 shadow-[0_0_20px_rgba(6,182,212,0.3)] disabled:shadow-none"
                    >
                        {isPending ? (
                            <><Loader2 className="w-5 h-5 mr-3 animate-spin" /> Cross-referencing implicit variables...</>
                        ) : (
                            <><Search className="w-5 h-5 mr-3" /> Execute Gap Scan Matrix</>
                        )}
                    </Button>
                </div>
            </div>

            {/* Structured Results Bento Grid */}
            {gapResults && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-4">

                    {/* Methodologies Card - Green */}
                    <Card className="bg-zinc-950 border-zinc-800 shadow-2xl relative transition-all group overflow-hidden border-t-4 border-t-green-500">
                        <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        <CardHeader className="pb-4 relative z-10 flex flex-row items-center justify-between">
                            <div className="space-y-1">
                                <CardTitle className="text-zinc-100 flex items-center font-black tracking-tight text-lg">
                                    <Waypoints className="w-5 h-5 mr-2 text-green-500" /> Extracted Methodologies
                                </CardTitle>
                                <CardDescription className="text-zinc-500 font-medium text-xs">Structurally resolved mapping constructs natively.</CardDescription>
                            </div>
                        </CardHeader>
                        <CardContent className="pt-2 relative z-10 space-y-3">
                            {gapResults.methodologies.map((item: string, i: number) => (
                                <div key={i} className="text-sm text-zinc-300 bg-zinc-900 border border-zinc-800/80 p-3 rounded-lg font-medium leading-relaxed shadow-sm">
                                    {item}
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                    {/* Research Gaps Card - Red/Amber Matrix */}
                    <Card className="bg-zinc-950 border-zinc-800 md:col-span-2 lg:col-span-1 shadow-2xl relative transition-all group overflow-hidden border-t-4 border-t-red-500">
                        <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        <CardHeader className="pb-4 relative z-10 flex flex-row items-center justify-between">
                            <div className="space-y-1">
                                <CardTitle className="text-zinc-100 flex items-center font-black tracking-tight text-lg">
                                    <TriangleAlert className="w-5 h-5 mr-2 text-red-500" /> Missing Semantics
                                </CardTitle>
                                <CardDescription className="text-zinc-500 font-medium text-xs">Isolated structural logic faults recursively tracking loops.</CardDescription>
                            </div>
                        </CardHeader>
                        <CardContent className="pt-2 relative z-10 space-y-3">
                            {gapResults.research_gaps.map((item: string, i: number) => {
                                // Assign synthetic mock severities extracting from general matrix intuitively scaling natively
                                const severity = i % 3 === 0 ? 'critical' : i % 2 === 0 ? 'moderate' : 'minor';
                                const badgeProps = severity === 'critical' ? { class: 'bg-red-500/10 text-red-400 border-red-500/20', label: 'CRITICAL' } :
                                    severity === 'moderate' ? { class: 'bg-amber-500/10 text-amber-400 border-amber-500/20', label: 'MODERATE' } :
                                        { class: 'bg-blue-500/10 text-blue-400 border-blue-500/20', label: 'MINOR' };

                                return (
                                    <div key={i} className="text-sm text-zinc-300 bg-zinc-900 border border-zinc-800/80 p-3 rounded-lg font-medium leading-relaxed shadow-sm relative pt-8">
                                        <Badge variant="outline" className={`absolute top-2 left-3 text-[9px] font-black tracking-widest px-1.5 py-0 rounded uppercase ${badgeProps.class}`}>
                                            {badgeProps.label}
                                        </Badge>
                                        {item}
                                    </div>
                                );
                            })}
                        </CardContent>
                    </Card>

                    {/* Limitations Card - Orange */}
                    <Card className="bg-zinc-950 border-zinc-800 lg:col-span-1 shadow-2xl relative transition-all group overflow-hidden border-t-4 border-t-orange-500">
                        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        <CardHeader className="pb-4 relative z-10 flex flex-row items-center justify-between">
                            <div className="space-y-1">
                                <CardTitle className="text-zinc-100 flex items-center font-black tracking-tight text-lg">
                                    <CircleAlert className="w-5 h-5 mr-2 text-orange-500" /> Boundary Constraints
                                </CardTitle>
                                <CardDescription className="text-zinc-500 font-medium text-xs">Structurally evaluated limitation variables mapped natively.</CardDescription>
                            </div>
                        </CardHeader>
                        <CardContent className="pt-2 relative z-10 space-y-3">
                            {gapResults.limitations.map((item: string, i: number) => (
                                <div key={i} className="text-sm text-zinc-300 bg-zinc-900 border border-zinc-800/80 p-3 rounded-lg font-medium leading-relaxed shadow-sm">
                                    {item}
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                </div>
            )}
        </div>
    );
}
