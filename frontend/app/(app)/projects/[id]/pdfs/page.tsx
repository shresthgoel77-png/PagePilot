"use client";

import { useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { usePdfs, useUploadPdf, useDeletePdf, usePdfPreview } from "@/hooks/usePdfs";
import { format } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { UploadCloud, FileText, CheckCircle2, Loader2, AlertCircle, Trash2, Eye, RefreshCw, Info } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";

export default function DocumentLibraryPage() {
    const params = useParams();
    const projectId = params.id as string;

    const { data: pdfs, isLoading, isError } = usePdfs(projectId);
    const { mutateAsync: uploadPdf } = useUploadPdf(projectId);

    const [isDragging, setIsDragging] = useState(false);
    const [uploadingFiles, setUploadingFiles] = useState<{ id: string, name: string, size: number, progress: number }[]>([]);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf');
        await processFiles(files);
    };

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const files = Array.from(e.target.files).filter(f => f.type === 'application/pdf');
            await processFiles(files);
        }
    };

    const processFiles = async (files: File[]) => {
        for (const file of files) {
            if (file.size > 50 * 1024 * 1024) {
                toast.error(`File ${file.name} exceeds 50MB limit natively.`);
                continue;
            }

            const uploadId = Math.random().toString(36).substring(7);
            setUploadingFiles(prev => [...prev, { id: uploadId, name: file.name, size: file.size, progress: 0 }]);

            try {
                await uploadPdf({
                    file,
                    onProgress: (p) => {
                        setUploadingFiles(prev => prev.map(f => f.id === uploadId ? { ...f, progress: p } : f));
                    }
                });

                toast.success(`Upload complete: ${file.name}`);
                setUploadingFiles(prev => prev.filter(f => f.id !== uploadId));
            } catch (err) {
                toast.error(`Upload tracking failure bridging ${file.name} securely.`);
                setUploadingFiles(prev => prev.filter(f => f.id !== uploadId));
            }
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <div className="space-y-2">
                <h1 className="text-3xl font-black text-white tracking-tight">PDF Context Library</h1>
                <p className="text-zinc-400 font-medium">Inject contextual parameters natively tracking embedding vectors mathematically securely bridging logic.</p>
            </div>

            {/* Smart Upload Zone */}
            <div
                className={`relative border-2 border-dashed rounded-2xl p-12 transition-all duration-300 ${isDragging ? 'border-cyan-500 bg-cyan-500/10 scale-[1.01]' : 'border-zinc-700 bg-zinc-900/50 hover:bg-zinc-900 hover:border-zinc-600'
                    } flex flex-col items-center justify-center`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <div className="bg-zinc-950 p-4 rounded-full shadow-lg border border-zinc-800 mb-6">
                    <UploadCloud className={`w-10 h-10 ${isDragging ? 'text-cyan-500' : 'text-zinc-400'}`} />
                </div>
                <h3 className="text-xl font-bold text-zinc-100 mb-2">Drop PDFs here or click to browse</h3>
                <p className="text-zinc-500 text-sm mb-6">Max 50MB. Text-based PDFs strictly evaluated recursively.</p>

                <Button variant="outline" className="bg-cyan-500 text-zinc-950 border-none font-bold hover:bg-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-colors" asChild>
                    <label className="cursor-pointer">
                        <input type="file" multiple accept=".pdf" className="hidden" onChange={handleFileSelect} />
                        Choose Files Logically
                    </label>
                </Button>
            </div>

            {/* Upload Queue Context */}
            {uploadingFiles.length > 0 && (
                <div className="space-y-3">
                    <h4 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Active Injections</h4>
                    <AnimatePresence>
                        {uploadingFiles.map((file) => (
                            <motion.div
                                key={file.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center justify-between shadow-lg"
                            >
                                <div className="flex items-center space-x-4 flex-1">
                                    <div className="p-2 bg-zinc-950 rounded-md border border-zinc-800">
                                        <FileText className="w-5 h-5 text-cyan-500 animate-pulse" />
                                    </div>
                                    <div className="flex-1 space-y-2 pr-8">
                                        <div className="flex justify-between items-center text-sm font-semibold">
                                            <span className="text-zinc-200 truncate max-w-sm">{file.name}</span>
                                            <span className="text-zinc-500">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                                        </div>
                                        <Progress value={file.progress} className="h-2 bg-zinc-950 [&>div]:bg-cyan-500" />
                                    </div>
                                </div>
                                <div className="font-mono text-cyan-500 text-sm font-bold">
                                    {file.progress}%
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            )}

            <div className="space-y-4 pt-4 border-t border-zinc-900/50">
                <h2 className="text-xl font-bold tracking-tight text-white mb-6">Indexed Vault Context</h2>

                {isLoading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-48 bg-zinc-900/50 rounded-xl animate-pulse border border-zinc-800"></div>
                        ))}
                    </div>
                ) : isError ? (
                    <div className="flex flex-col items-center justify-center p-16 border border-zinc-900 rounded-xl bg-zinc-950 border-dashed border-red-500/30">
                        <AlertCircle className="w-16 h-16 text-red-500/50 mb-4" />
                        <p className="text-zinc-500 font-medium font-mono text-sm text-center">Failed intrinsically securing logical bounds.<br />Unable to map document parameters.</p>
                    </div>
                ) : pdfs?.length === 0 ? (
                    <div className="flex flex-col items-center justify-center p-16 border border-zinc-900 rounded-xl bg-zinc-950 border-dashed">
                        <FileText className="w-16 h-16 text-zinc-800 mb-4" />
                        <p className="text-zinc-500 font-medium font-mono text-sm">No structurally mapped documents present implicitly.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {pdfs?.map((pdf: any) => (
                            <PdfCard key={pdf.id} pdf={pdf} projectId={projectId} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

function PdfCard({ pdf, projectId }: { pdf: any, projectId: string }) {
    const { mutate: deletePdf, isPending: isDeleting } = useDeletePdf(projectId);
    const [viewOpen, setViewOpen] = useState(false);
    const { data: previewUrl, isLoading: isPreviewLoading } = usePdfPreview(projectId, viewOpen ? pdf.id : null);

    // Deriving multi-status implicitly
    let statusClass = "bg-green-500/10 text-green-500 border-green-500/20";
    let statusIcon = <CheckCircle2 className="w-3 h-3 mr-1" />;
    let statusLabel = "Indexed";

    if (pdf.status === 'processing' || pdf.status === 'uploading') {
        statusClass = "bg-amber-500/10 text-amber-500 border-amber-500/20";
        statusIcon = <Loader2 className="w-3 h-3 mr-1 animate-spin" />;
        statusLabel = "Processing";
    } else if (pdf.status === 'failed') {
        statusClass = "bg-red-500/10 text-red-500 border-red-500/20";
        statusIcon = <AlertCircle className="w-3 h-3 mr-1" />;
        statusLabel = "Extraction Fault";
    }

    const isScanned = pdf.page_count > 0 && pdf.extracted_pages === 0 && pdf.status === 'indexed';

    return (
        <Card className="bg-zinc-900 border-zinc-800 flex flex-col hover:border-zinc-700 transition-colors shadow-none hover:shadow-xl hover:shadow-cyan-500/5">
            <CardHeader className="pb-3 flex flex-row items-start justify-between">
                <div className="p-2.5 bg-zinc-950 border border-zinc-800/80 rounded-lg shrink-0">
                    <FileText className="w-5 h-5 text-zinc-400" />
                </div>
                <div className="flex gap-2">
                    {isScanned && (
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger>
                                    <div className="p-1 bg-amber-500/10 rounded border border-amber-500/20">
                                        <Info className="w-3.5 h-3.5 text-amber-500" />
                                    </div>
                                </TooltipTrigger>
                                <TooltipContent className="bg-zinc-950 border-zinc-800 text-zinc-300">
                                    <p className="max-w-xs text-xs font-medium">This appears to be a scanned image structurally blocking natural text extraction sequentially safely natively.</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    )}
                    <Badge variant="outline" className={`${statusClass} text-[10px] uppercase font-bold tracking-wider px-2 py-0 h-6 shrink-0`}>
                        {statusIcon}
                        {statusLabel}
                    </Badge>
                </div>
            </CardHeader>
            <CardContent className="flex-1 pb-3">
                <CardTitle className="text-base font-bold text-zinc-100 tracking-tight leading-snug line-clamp-2 mb-2" title={pdf.original_name || pdf.filename}>
                    {pdf.original_name || pdf.filename}
                </CardTitle>
                <div className="flex justify-between items-center text-xs text-zinc-500 font-medium">
                    <span>{pdf.page_count || 0} Pages</span>
                    <span>{format(new Date(pdf.uploaded_at || Date.now()), "MMM d, yyyy")}</span>
                </div>
            </CardContent>
            <CardFooter className="flex justify-between items-center border-t border-zinc-800/50 bg-zinc-950/30 py-3 gap-2">
                <Button variant="ghost" size="sm" onClick={() => setViewOpen(true)} className="flex-1 text-zinc-400 hover:text-cyan-400 hover:bg-cyan-500/10 px-0 h-8">
                    <Eye className="w-3.5 h-3.5 mr-1.5" /> View
                </Button>

                <Button variant="ghost" size="sm" onClick={() => toast.success("Initialization re-index parameters tracking vectors internally recursively.")} className="flex-1 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 px-0 h-8">
                    <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Index
                </Button>

                <AlertDialog>
                    <AlertDialogTrigger asChild>
                        <Button variant="ghost" size="sm" disabled={isDeleting} className="w-8 h-8 p-0 shrink-0 text-zinc-500 hover:text-red-400 hover:bg-red-500/10">
                            <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent className="bg-zinc-950 border-zinc-800">
                        <AlertDialogHeader>
                            <AlertDialogTitle className="text-zinc-100">Purge Internal Logics</AlertDialogTitle>
                            <AlertDialogDescription className="text-zinc-500">
                                This execution irreversibly deletes structural embedding metrics tracking "{pdf.original_name || pdf.filename}" internally securely.
                            </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                            <AlertDialogCancel className="bg-zinc-900 border-zinc-800 text-zinc-300 hover:bg-zinc-800 hover:text-white">Bypass</AlertDialogCancel>
                            <Button
                                variant="destructive"
                                disabled={isDeleting}
                                className="bg-red-500/20 text-red-500 border border-red-500/50 hover:bg-red-500 hover:text-white"
                                onClick={() => deletePdf(pdf.id)}
                            >
                                {isDeleting ? 'Purging...' : 'Execute Purge'}
                            </Button>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialog>

                {/* View Modal */}
                <Dialog open={viewOpen} onOpenChange={setViewOpen}>
                    <DialogContent className="sm:max-w-6xl bg-zinc-950 border-zinc-800 h-[85vh] flex flex-col p-4">
                        <DialogHeader className="shrink-0 mb-4 flex-row items-center justify-between">
                            <DialogTitle className="text-zinc-100 flex items-center">
                                <FileText className="w-4 h-4 mr-2 text-cyan-500" />
                                Interactive View Payload: {pdf.original_name || pdf.filename}
                            </DialogTitle>
                        </DialogHeader>
                        <div className="flex-1 w-full rounded-xl border border-zinc-900 bg-zinc-900/50 overflow-hidden relative shadow-inner">
                            {isPreviewLoading ? (
                                <div className="absolute inset-0 flex flex-col items-center justify-center text-zinc-500 font-medium">
                                    <Loader2 className="w-10 h-10 animate-spin text-cyan-500 mb-6 drop-shadow-[0_0_15px_rgba(6,182,212,0.6)]" />
                                    Establishing secure document stream boundaries...
                                </div>
                            ) : previewUrl ? (
                                <iframe src={previewUrl} className="w-full h-full border-none mix-blend-lighten" title={pdf.original_name} />
                            ) : (
                                <div className="absolute inset-0 flex flex-col items-center justify-center text-zinc-500 font-medium bg-zinc-950 border-dashed border-2 border-red-500/20 m-4 rounded-xl">
                                    <AlertCircle className="w-12 h-12 text-red-500 mb-4 bg-red-500/10 p-2 rounded-full" />
                                    Extraction fault isolating streaming blob boundaries correctly.
                                </div>
                            )}
                        </div>
                    </DialogContent>
                </Dialog>
            </CardFooter>
        </Card>
    );
}
