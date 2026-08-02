import { ScrollArea } from "@/components/ui/scroll-area";
import { ChevronRight, FileText, Search } from "lucide-react";

interface CitationSource {
    pdf_id: string;
    filename: string;
    page: number;
    text: string;
    score?: number;
}

interface CitationPanelProps {
    sources?: CitationSource[];
    selectedSource?: CitationSource | null;
}

export function CitationPanel({ sources, selectedSource }: CitationPanelProps) {
    if (!sources || sources.length === 0) {
        return (
            <div className="h-full w-full flex flex-col bg-zinc-950 border-l border-zinc-800 p-6 items-center justify-center opacity-60">
                <Search className="w-12 h-12 text-zinc-700 mb-4" />
                <p className="text-xs font-bold text-zinc-500 tracking-widest uppercase text-center">
                    Awaiting structural extracts mapping active variables explicitly
                </p>
            </div>
        );
    }

    return (
        <div className="h-full w-full flex flex-col bg-zinc-950 border-l border-zinc-800 shadow-2xl relative z-10 transition-all">
            <div className="px-4 py-4 border-b border-zinc-800 bg-zinc-950 sticky top-0 z-10 shadow-sm flex items-center justify-between">
                <div className="text-[10px] font-black tracking-widest uppercase text-cyan-400 flex items-center">
                    <span className="w-2 h-2 rounded-full bg-cyan-500 mr-2 shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>
                    Verification Vectors
                </div>
                <div className="text-xs font-bold text-zinc-500">{sources.length} Nodes</div>
            </div>
            <div className="flex-1 overflow-hidden">
                <ScrollArea className="h-full">
                    <div className="flex flex-col space-y-3 p-4">
                        {sources.map((src, i) => {
                            const isSelected = selectedSource &&
                                selectedSource.filename === src.filename &&
                                selectedSource.page === src.page;

                            return (
                                <div
                                    key={i}
                                    className={`relative group p-4 rounded-xl border text-sm transition-all overflow-hidden ${isSelected
                                            ? 'bg-cyan-500/10 border-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.15)] ring-1 ring-cyan-500/20'
                                            : 'bg-zinc-900 border-zinc-800 hover:border-zinc-700'
                                        }`}
                                >
                                    <div className="flex justify-between items-start mb-2 border-b border-zinc-800/50 pb-2">
                                        <div className="flex items-center text-zinc-100 font-bold overflow-hidden">
                                            <FileText className="w-4 h-4 mr-2 text-cyan-500 shrink-0" />
                                            <span className="truncate pr-4 leading-tight">{src.filename}</span>
                                        </div>
                                        <div className={`shrink-0 text-[10px] font-black tracking-widest uppercase px-2 py-0.5 rounded border shadow-inner ${isSelected ? 'bg-cyan-500 text-zinc-950 border-cyan-400' : 'bg-zinc-800 text-zinc-400 border-zinc-700 group-hover:bg-zinc-700 group-hover:text-zinc-300'
                                            }`}>
                                            PG {src.page}
                                        </div>
                                    </div>
                                    <div className={`text-xs font-medium leading-relaxed mt-2 p-3 rounded-lg break-words overflow-auto max-h-48 transition-colors ${isSelected ? 'bg-cyan-500/5 text-cyan-50 border border-cyan-500/20' : 'bg-zinc-950/50 text-zinc-400 border border-zinc-800/50 group-hover:text-zinc-300'
                                        }`}>
                                        "{src.text}"
                                    </div>
                                    {src.score !== undefined && (
                                        <div className="mt-3 flex justify-end">
                                            <span className={`text-[9px] font-black tracking-widest px-1.5 py-0.5 rounded uppercase ${isSelected ? 'text-cyan-400 bg-cyan-950' : 'text-zinc-500 bg-zinc-950'
                                                }`}>
                                                Rank: {(src.score * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </ScrollArea>
            </div>
        </div>
    );
}
