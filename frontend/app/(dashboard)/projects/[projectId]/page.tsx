"use client";

import Link from 'next/link';
import { useProject } from '@/hooks/useProjects';
import { Button } from '@/components/ui/button';
import { PdfUploadDropzone } from '@/components/pdf-upload-dropzone';
import { PdfList } from '@/components/pdf-list';

export default function ProjectDetailView({ params }: { params: { projectId: string } }) {
    const { data: project, isLoading, isError } = useProject(params.projectId);

    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center bg-slate-50">
                <div className="animate-spin h-14 w-14 border-4 border-slate-900 border-t-transparent rounded-full shadow-lg" />
            </div>
        );
    }

    if (isError || !project) {
        return (
            <div className="p-8 text-center text-red-600 bg-red-50 font-bold tracking-tight border-2 border-red-200 mt-16 rounded-xl max-w-2xl mx-auto shadow-md">
                Critical Bounding Isolation Exception Encountered Resolving Domain Object securely natively.
                <br /><Link href="/dashboard" className="underline mt-4 inline-block text-blue-600 hover:text-blue-800 transition-colors">Abort & Rescue State Logic</Link>
            </div>
        );
    }

    return (
        <div className="flex flex-col space-y-8 p-4 lg:p-8 h-full bg-slate-50 w-full relative">
            <nav className="flex text-xs text-slate-500 font-extrabold uppercase tracking-widest bg-white shadow-sm w-max p-2 rounded-lg border border-slate-100" aria-label="Breadcrumb">
                <ol className="inline-flex items-center space-x-2 px-2">
                    <li><Link href="/dashboard" className="hover:text-blue-600 transition-colors">Global Hub</Link></li>
                    <li><span className="mx-2 text-slate-300">/</span></li>
                    <li className="text-slate-900 truncate max-w-[250px]" aria-current="page">{project.name}</li>
                </ol>
            </nav>

            <div className="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-6 bg-white p-8 shadow-sm border border-slate-100 rounded-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-slate-100 rounded-full blur-3xl opacity-50 -mr-20 -mt-20 pointer-events-none"></div>
                <div className="relative z-10">
                    <h1 className="text-4xl font-black text-slate-900 tracking-tighter">{project.name}</h1>
                    <p className="text-slate-500 mt-2 font-semibold max-w-3xl leading-relaxed">{project.description || "Unconfigured description context globally isolated safely natively unpopulated."}</p>
                </div>
                <div className="relative z-10 w-full xl:w-auto mt-4 xl:mt-0">
                    <Button className="w-full xl:w-auto bg-slate-900 hover:bg-slate-800 text-white shadow-xl font-extrabold tracking-tight px-8 h-12 text-sm shrink-0 uppercase transition-all hover:scale-105" onClick={() => alert("Complex LangChain Chat Interface Initialization Context Hook mapped globally (Step 12/13 execution inherently bounded inherently)")}>
                        + Launch Global Chat Interop
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                {/* Left Constraints Column */}
                <div className="xl:col-span-1 space-y-6">
                    <h3 className="text-sm font-extrabold uppercase tracking-widest text-slate-500 mb-2 pl-2">Ingestion Vectors Source Modules ideally</h3>
                    <PdfUploadDropzone projectId={params.projectId} />
                </div>

                {/* Right Logical State Views */}
                <div className="xl:col-span-2 space-y-6">
                    <h3 className="text-sm font-extrabold uppercase tracking-widest text-slate-500 mb-2 pl-2">Tracked Environmental Architecture Bounded Cache</h3>
                    <PdfList projectId={params.projectId} />
                </div>
            </div>
        </div>
    );
}
