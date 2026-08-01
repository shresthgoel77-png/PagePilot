"use client";

import { useProjects } from '@/hooks/useProjects';
import { ProjectCard } from '@/components/project-card';
import { CreateProjectModal } from '@/components/create-project-modal';

export default function DashboardPage() {
    const { data: projects, isLoading, isError } = useProjects();

    return (
        <div className="flex flex-col h-full space-y-6">
            <div className="flex justify-between items-center bg-white p-6 rounded-lg shadow-sm border border-slate-100 relative overflow-hidden">
                <div className="absolute top-0 right-0 -mt-16 -mr-16 bg-blue-50 w-48 h-48 rounded-full opacity-50 pointer-events-none"></div>
                <div className="relative z-10">
                    <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Active Workspaces</h1>
                    <p className="text-slate-500 mt-2 font-medium">Control unified boundaries across embedded environments.</p>
                </div>
                <div className="relative z-10">
                    <CreateProjectModal />
                </div>
            </div>

            {isLoading && (
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-blue-600 border-solid"></div>
                </div>
            )}

            {isError && (
                <div className="p-6 bg-red-50 text-red-700 flex flex-col justify-center items-center font-bold tracking-tight rounded-md border border-red-200">
                    <span>Critical Fetch Interruption</span>
                    <span className="text-sm font-medium opacity-80 mt-1">Unable to traverse network bindings natively securely.</span>
                </div>
            )}

            {!isLoading && !isError && projects?.length === 0 && (
                <div className="flex flex-col items-center justify-center flex-1 bg-white border border-dashed border-slate-300 rounded-lg py-32 shadow-sm relative overflow-hidden group hover:border-slate-400 transition-colors">
                    <div className="text-7xl mb-4 opacity-30 transform group-hover:scale-110 group-hover:opacity-60 transition-all duration-300">🧊</div>
                    <h2 className="text-2xl font-bold tracking-tight text-slate-700">Empty State Encountered</h2>
                    <p className="text-slate-500 mt-2 mb-6 font-medium text-center px-4">Generate localized boundaries executing vector mappings implicitly across the stack reliably.</p>
                    <CreateProjectModal />
                </div>
            )}

            {!isLoading && projects && projects.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-max">
                    {projects.map((project: any) => (
                        <ProjectCard key={project.id} project={project} />
                    ))}
                </div>
            )}
        </div>
    );
}
