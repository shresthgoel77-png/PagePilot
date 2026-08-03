"use client";

import { useProjectStore } from "@/stores/projectStore";
import { motion } from "framer-motion";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { LayoutDashboard, Target, Gauge, Network } from "lucide-react";

export default function ProjectOverviewPage() {
    const { currentProject } = useProjectStore();

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="p-8 max-w-6xl mx-auto space-y-8"
        >
            <div className="space-y-2">
                <h1 className="text-4xl font-black text-white tracking-tight">System Overview</h1>
                <p className="text-zinc-400 font-medium">Control the contextual parameters bounding "{currentProject?.name || "Initializing..."}" dynamically natively.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="bg-zinc-900 border-zinc-800 shadow-[0_0_20px_rgba(0,0,0,0.5)] cursor-default hover:border-cyan-500/50 transition-colors">
                    <CardHeader className="flex flex-row space-y-0 justify-between items-center pb-2">
                        <CardTitle className="text-zinc-400 text-sm font-bold tracking-tight">Linked Context</CardTitle>
                        <Network className="w-4 h-4 text-cyan-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white">12,410</div>
                        <p className="text-xs text-zinc-500 mt-1 font-mono">vector_nodes_indexed</p>
                    </CardContent>
                </Card>

                <Card className="bg-zinc-900 border-zinc-800 shadow-[0_0_20px_rgba(0,0,0,0.5)] cursor-default hover:border-blue-500/50 transition-colors">
                    <CardHeader className="flex flex-row space-y-0 justify-between items-center pb-2">
                        <CardTitle className="text-zinc-400 text-sm font-bold tracking-tight">Active PDFs</CardTitle>
                        <LayoutDashboard className="w-4 h-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white">4</div>
                        <p className="text-xs text-zinc-500 mt-1 font-mono">structural_docs_found</p>
                    </CardContent>
                </Card>

                <Card className="bg-zinc-900 border-zinc-800 shadow-[0_0_20px_rgba(0,0,0,0.5)] cursor-default hover:border-emerald-500/50 transition-colors">
                    <CardHeader className="flex flex-row space-y-0 justify-between items-center pb-2">
                        <CardTitle className="text-zinc-400 text-sm font-bold tracking-tight">Performance Rating</CardTitle>
                        <Gauge className="w-4 h-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white">99.8%</div>
                        <p className="text-xs text-zinc-500 mt-1 font-mono">retrieval_acc_binding</p>
                    </CardContent>
                </Card>

                <Card className="bg-zinc-900 border-zinc-800 shadow-[0_0_20px_rgba(0,0,0,0.5)] cursor-default hover:border-amber-500/50 transition-colors">
                    <CardHeader className="flex flex-row space-y-0 justify-between items-center pb-2">
                        <CardTitle className="text-zinc-400 text-sm font-bold tracking-tight">Gap Vulnerabilities</CardTitle>
                        <Target className="w-4 h-4 text-amber-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white">2</div>
                        <p className="text-xs text-zinc-500 mt-1 font-mono">architectural_blindspots</p>
                    </CardContent>
                </Card>
            </div>

            <div className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-2xl flex flex-col items-center justify-center min-h-[300px]">
                <p className="text-zinc-500 font-medium text-center max-w-lg mb-4">
                    Extensive data projections and graph topology renderings mapping to {currentProject?.name} dependencies natively scale outwards inside analytical views globally.
                </p>
                <code className="text-xs font-mono text-cyan-500 bg-cyan-500/10 px-4 py-2 rounded-md">
                    Execute Analysis structurally to populate metric sets implicitly.
                </code>
            </div>
        </motion.div>
    );
}
