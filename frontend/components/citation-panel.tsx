import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

interface CitationSource {
    pdf_id: string;
    filename: string;
    page: number;
    text: string;
    score?: number;
}

export function CitationPanel({ sources }: { sources?: CitationSource[] }) {
    if (!sources || sources.length === 0) {
        return (
            <Card className="h-full border-0 shadow-sm bg-slate-50 flex flex-col items-center justify-center p-8">
                <div className="text-4xl opacity-30 mb-4">🔍</div>
                <p className="text-sm font-bold text-slate-400 tracking-tight text-center leading-relaxed">
                    Awaiting generation execution resolving explicit extraction bounds uniquely mapping inherently...
                </p>
            </Card>
        );
    }

    return (
        <Card className="h-full border-0 rounded-none shadow-none flex flex-col bg-slate-50">
            <CardHeader className="border-b py-4 bg-white sticky top-0 z-10 shadow-sm">
                <CardTitle className="text-xs font-extrabold tracking-widest uppercase text-slate-600 flex items-center">
                    <span className="w-2 h-2 rounded-full bg-blue-500 mr-2 animate-pulse"></span>
                    Extracted Active Bounds
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0 flex-1 overflow-hidden">
                <ScrollArea className="h-full">
                    <div className="flex flex-col space-y-4 p-4">
                        {sources.map((src, i) => (
                            <div key={i} className="bg-white border text-sm border-slate-200 p-4 rounded-lg shadow-sm relative group hover:border-blue-400 transition-colors">
                                <h3 className="font-bold text-slate-800 border-b border-slate-50 pb-2 mb-2 break-all pr-12 line-clamp-1">{src.filename}</h3>
                                <div className="absolute top-3 right-4 text-[10px] font-black tracking-widest uppercase bg-slate-100 text-slate-600 px-2 py-1 rounded-sm border border-slate-200 shadow-inner group-hover:bg-blue-100 group-hover:text-blue-800 transition-colors">
                                    PG {src.page}
                                </div>
                                <div className="text-xs font-medium leading-relaxed text-slate-500 bg-slate-50 p-3 rounded-md break-words overflow-hidden text-ellipsis line-clamp-[8] group-hover:text-slate-700 transition-colors">
                                    "{src.text}"
                                </div>
                            </div>
                        ))}
                    </div>
                </ScrollArea>
            </CardContent>
        </Card>
    );
}
