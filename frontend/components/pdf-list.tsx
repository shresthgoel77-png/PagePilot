"use client";

import { formatDistanceToNow } from 'date-fns';
import { usePdfs, useDeletePdf } from '@/hooks/usePdfs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";

export function PdfList({ projectId }: { projectId: string }) {
    const { data: pdfs, isLoading } = usePdfs(projectId);
    const { mutate: deletePdf, isPending: isDeleting } = useDeletePdf(projectId);

    if (isLoading) {
        return <div className="p-12 text-center text-sm font-bold opacity-70 animate-pulse tracking-widest text-slate-700">Connecting Database Contexts...</div>;
    }

    if (!pdfs || pdfs.length === 0) {
        return (
            <div className="p-16 text-center text-sm font-bold text-slate-500 border rounded-lg bg-slate-50 border-dashed tracking-tight transition-all duration-300 shadow-inner">
                <span className="text-4xl block mb-2 opacity-50">📂</span>
                Empty logical tables globally mapped natively.
            </div>
        );
    }

    const getStatusBadge = (pdf: any) => {
        const { status, progress, error_message } = pdf;
        switch (status) {
            case 'uploaded': return <Badge variant="secondary" className="bg-slate-200 text-slate-700 font-bold tracking-tight">Staged ({progress || 0}%)</Badge>;
            case 'queued': return <Badge variant="outline" className="text-blue-700 border-blue-700 font-bold bg-blue-50 animate-pulse tracking-tight">Queued ({progress || 0}%)</Badge>;
            case 'parsing': return <Badge variant="outline" className="text-yellow-700 border-yellow-700 font-bold bg-yellow-50 animate-pulse tracking-tight">Parsing text ({progress || 0}%)</Badge>;
            case 'ocr': return <Badge variant="outline" className="text-orange-700 border-orange-700 font-bold bg-orange-50 animate-pulse tracking-tight">Extracting OCR ({progress || 0}%)</Badge>;
            case 'embedding': return <Badge variant="outline" className="text-indigo-700 border-indigo-700 font-bold bg-indigo-50 animate-pulse tracking-tight">Executing LLM embedding ({progress || 0}%)</Badge>;
            case 'indexing': return <Badge variant="outline" className="text-purple-700 border-purple-700 font-bold bg-purple-50 animate-pulse tracking-tight">Vector Indexing ({progress || 0}%)</Badge>;
            case 'ready': return <Badge variant="default" className="bg-emerald-600 font-bold tracking-tight">Ready (100%)</Badge>;
            case 'error': return (
                <div className="flex flex-col gap-1 items-start">
                    <Badge variant="destructive" className="font-bold tracking-tight shadow-sm">Parsing Fault</Badge>
                    {error_message && <span className="text-xs text-red-600 font-medium max-w-[200px] truncate" title={error_message}>{error_message}</span>}
                </div>
            );
            default: return <Badge>{status}</Badge>;
        }
    };

    return (
        <Card className="shadow-sm border-0 bg-white">
            <CardHeader className="bg-slate-50 border-b pb-4">
                <CardTitle className="text-xl font-extrabold tracking-tight text-slate-800">Physical Artifact Layouts</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <Table>
                    <TableHeader className="bg-slate-100 text-slate-800">
                        <TableRow>
                            <TableHead className="w-[45%] font-extrabold tracking-tighter">Alias Architecture Object</TableHead>
                            <TableHead className="font-extrabold tracking-tighter">Injection Stream Timestamp</TableHead>
                            <TableHead className="font-extrabold tracking-tighter">State Bounds</TableHead>
                            <TableHead className="text-right font-extrabold tracking-tighter pr-4">Logic Primitives</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {pdfs.map((pdf: any) => (
                            <TableRow key={pdf.id} className="hover:bg-blue-50/50 transition-colors">
                                <TableCell className="font-bold text-slate-700 truncate max-w-[200px] border-r border-slate-50">{pdf.original_name}</TableCell>
                                <TableCell className="text-slate-500 text-xs font-semibold uppercase tracking-wider">
                                    {formatDistanceToNow(new Date(pdf.created_at), { addSuffix: true })}
                                </TableCell>
                                <TableCell>{getStatusBadge(pdf)}</TableCell>
                                <TableCell className="text-right pr-4">
                                    <AlertDialog>
                                        <AlertDialogTrigger asChild>
                                            <Button variant="ghost" size="sm" className="text-red-500 hover:text-white hover:bg-red-500 font-bold transition-all shadow-sm rounded-md" disabled={isDeleting}>Detatch Element</Button>
                                        </AlertDialogTrigger>
                                        <AlertDialogContent>
                                            <AlertDialogHeader>
                                                <AlertDialogTitle className="font-black text-xl">Sever Logical Bonds?</AlertDialogTitle>
                                                <AlertDialogDescription className="text-slate-700 font-medium">
                                                    Execution completely removes contextual bounds wrapping actual cached documents across Vector boundaries eliminating memory explicitly.
                                                </AlertDialogDescription>
                                            </AlertDialogHeader>
                                            <AlertDialogFooter>
                                                <AlertDialogCancel className="font-bold">Hold Bounds</AlertDialogCancel>
                                                <AlertDialogAction onClick={() => deletePdf(pdf.id)} className="bg-red-600 text-white font-extrabold tracking-tight border-2 border-red-700 shadow-md">Wipe Global Maps</AlertDialogAction>
                                            </AlertDialogFooter>
                                        </AlertDialogContent>
                                    </AlertDialog>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}
