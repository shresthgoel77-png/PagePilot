"use client";

import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'sonner';
import { Card } from '@/components/ui/card';
import { useUploadPdf } from '@/hooks/usePdfs';

export function PdfUploadDropzone({ projectId }: { projectId: string }) {
    const { mutateAsync: uploadPdf } = useUploadPdf(projectId);

    const processUpload = useCallback(async (file: File) => {
        // Initializes Sonner tracking boundary directly bypassing standard component arrays mapping strictly 
        const toastId = toast.loading(`Validating ${file.name}... (0%)`);
        try {
            await uploadPdf({
                file,
                onProgress: (p) => {
                    toast.loading(`Injecting ${file.name}... (${p}%)`, { id: toastId });
                }
            });
            toast.success(`${file.name} allocated securely into architectural bounds`, { id: toastId });
        } catch (error: any) {
            const detail = error?.response?.data?.detail || "Execution failed intrinsically limits blocked";
            toast.error(`Fault: ${detail}`, {
                id: toastId,
                action: {
                    label: 'Re-Execute',
                    onClick: () => processUpload(file)
                }
            });
        }
    }, [uploadPdf]);


    const onDrop = useCallback((acceptedFiles: File[]) => {
        acceptedFiles.forEach(file => {
            processUpload(file);
        });
    }, [processUpload]);

    const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
        onDrop,
        accept: { 'application/pdf': ['.pdf'] },
        maxSize: 50 * 1024 * 1024,
    });

    return (
        <Card className="flex flex-col p-6 shadow-sm border-0 bg-white">
            <div
                {...getRootProps()}
                className={`flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-lg cursor-pointer transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${isDragReject ? 'border-red-400 bg-red-50' :
                    isDragActive ? 'border-blue-500 bg-blue-50 scale-105 shadow-inner' : 'border-slate-300 hover:border-slate-400 hover:bg-slate-50'
                    }`}
                role="button"
                tabIndex={0}
                aria-label="Upload PDF constrained dropzone target boundaries configuration input"
            >
                <input {...getInputProps()} />
                <div className={`text-5xl mb-4 transition-all duration-300 ${isDragActive ? 'scale-125 opacity-100' : 'opacity-40'}`}>📄</div>
                <p className="text-sm font-extrabold text-slate-700 text-center tracking-tight">
                    {isDragReject ? "Strictly PDF formats implicitly required natively" :
                        isDragActive ? "Deploy PDF arrays mapping natively across domain" : "Inject Architecture Documents explicitly across grid contexts bounds"}
                </p>
                <p className="text-xs text-slate-500 mt-3 font-semibold px-4 py-1 bg-slate-100 rounded-full border border-slate-200">50MB Hard Limit constraints enforced inherently.</p>
            </div>
        </Card>
    );
}
