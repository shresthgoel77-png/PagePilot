"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, GitCompare, AlertTriangle, FileText, Bot, User, CheckCircle2, ChevronRight, XCircle } from "lucide-react";

export function Showcase() {
    const [activeTab, setActiveTab] = useState<"chat" | "synthesis" | "gap">("chat");

    const tabs = [
        { id: "chat", label: "Chat with PDFs", icon: MessageSquare, desc: "Interact strictly with your documents." },
        { id: "synthesis", label: "Cross-Doc Reasoning", icon: GitCompare, desc: "Synthesize findings across sources." },
        { id: "gap", label: "Gap Analysis", icon: AlertTriangle, desc: "Spot contradictions instantly." }
    ];

    return (
        <section className="w-full max-w-6xl mx-auto py-24 px-6 relative" id="features">
            <div className="text-center mb-16 space-y-4">
                <h2 className="text-3xl md:text-5xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
                    Experience the Workspace
                </h2>
                <p className="text-zinc-500 dark:text-zinc-400 max-w-2xl mx-auto text-lg">
                    Everything you need to turn raw papers into coherent, cited arguments.
                </p>
            </div>

            <div className="flex flex-col lg:flex-row gap-8 items-start">
                {/* Tabs / Controllers */}
                <div className="flex flex-col gap-3 w-full lg:w-1/3">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={`flex flex-col items-start p-5 rounded-2xl transition-all border text-left
                            ${activeTab === tab.id
                                    ? "bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 shadow-xl shadow-zinc-200/50 dark:shadow-black/50 scale-[1.02]"
                                    : "bg-transparent border-transparent hover:bg-zinc-100 dark:hover:bg-zinc-900/50 hover:border-zinc-200 dark:hover:border-zinc-800"}`}
                        >
                            <div className="flex items-center gap-3 mb-2">
                                <span className={`p-2 rounded-lg ${activeTab === tab.id ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400" : "bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400"}`}>
                                    <tab.icon className="w-5 h-5" />
                                </span>
                                <h3 className={`font-semibold ${activeTab === tab.id ? "text-zinc-900 dark:text-zinc-50" : "text-zinc-600 dark:text-zinc-400"}`}>
                                    {tab.label}
                                </h3>
                            </div>
                            <p className="text-sm text-zinc-500 dark:text-zinc-400 pl-11">
                                {tab.desc}
                            </p>
                        </button>
                    ))}
                </div>

                {/* Display Panel */}
                <div className="w-full lg:w-2/3 h-[500px] bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-3xl overflow-hidden shadow-2xl relative flex flex-col">
                    <div className="h-12 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 flex items-center px-4 gap-2 shrink-0">
                        <div className="w-3 h-3 rounded-full bg-red-400/80"></div>
                        <div className="w-3 h-3 rounded-full bg-amber-400/80"></div>
                        <div className="w-3 h-3 rounded-full bg-green-400/80"></div>
                        <div className="ml-4 text-xs font-medium text-zinc-400 dark:text-zinc-500 px-3 py-1 bg-zinc-100 dark:bg-zinc-800 rounded-md">
                            workspace.researchos.app
                        </div>
                    </div>

                    <div className="flex-1 overflow-hidden relative">
                        <AnimatePresence mode="wait">
                            {activeTab === "chat" && <ChatMock key="chat" />}
                            {activeTab === "synthesis" && <SynthesisMock key="synth" />}
                            {activeTab === "gap" && <GapMock key="gap" />}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </section>
    );
}

// ─── MOCK COMPONENTS ─────────────────────────────────────────────────────────

function ChatMock() {
    const [messages, setMessages] = useState<number>(0);
    const [typedText, setTypedText] = useState("");
    const fullText = "Based on [Smith et al., 2023] and [Johnson, 2024], the proposed framework improves inference speed by 42%. [Smith] particularly emphasizes the attention bottleneck reduction.";

    useEffect(() => {
        let t1 = setTimeout(() => setMessages(1), 800);
        let t2 = setTimeout(() => setMessages(2), 1600);
        return () => { clearTimeout(t1); clearTimeout(t2); };
    }, []);

    useEffect(() => {
        if (messages === 2) {
            let i = 0;
            const interval = setInterval(() => {
                setTypedText(fullText.slice(0, i));
                i++;
                if (i > fullText.length) clearInterval(interval);
            }, 10);
            return () => clearInterval(interval);
        }
    }, [messages]);

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="w-full h-full p-6 flex flex-col gap-6"
        >
            {messages >= 1 && (
                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex justify-end gap-3">
                    <div className="bg-zinc-900 dark:bg-white text-zinc-50 dark:text-zinc-900 px-5 py-3 rounded-2xl rounded-tr-sm max-w-[80%] text-sm">
                        What does the literature say about inference speed improvements?
                    </div>
                </motion.div>
            )}
            {messages >= 2 && (
                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shrink-0">
                        <Bot size={16} />
                    </div>
                    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 px-5 py-4 rounded-2xl rounded-tl-sm max-w-[85%] text-sm text-zinc-700 dark:text-zinc-300 shadow-sm leading-relaxed">
                        {typedText}
                        {typedText.length < fullText.length && <span className="w-2 h-4 bg-cyan-500 inline-block ml-1 animate-pulse" />}

                        {typedText === fullText && (
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-4 flex gap-2">
                                <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-400 flex items-center gap-1 bg-zinc-100 dark:bg-zinc-800 px-2 py-1 rounded">
                                    <FileText size={12} /> Smith_2023.pdf
                                </span>
                                <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-400 flex items-center gap-1 bg-zinc-100 dark:bg-zinc-800 px-2 py-1 rounded">
                                    <FileText size={12} /> Johnson_2024.pdf
                                </span>
                            </motion.div>
                        )}
                    </div>
                </motion.div>
            )}
        </motion.div>
    );
}

function SynthesisMock() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="w-full h-full p-6 overflow-y-auto custom-scrollbar"
        >
            <div className="space-y-6">
                <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-3 flex items-center gap-2">
                        <CheckCircle2 size={14} className="text-green-500" /> Key Agreements
                    </h4>
                    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 space-y-3">
                        <p className="text-sm text-zinc-600 dark:text-zinc-300">
                            Both <span className="text-cyan-600 dark:text-cyan-400 font-medium cursor-pointer">PaperA.pdf</span> and <span className="text-cyan-600 dark:text-cyan-400 font-medium cursor-pointer">PaperB.pdf</span> conclude that transformer architectures require significant memory optimizations for edge devices.
                        </p>
                    </div>
                </div>

                <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-3 flex items-center gap-2">
                        <GitCompare size={14} className="text-cyan-500" /> Structural Synthesis
                    </h4>
                    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4">
                        <table className="w-full text-sm text-left">
                            <thead>
                                <tr className="border-b border-zinc-200 dark:border-zinc-800">
                                    <th className="pb-2 font-medium text-zinc-500">Metric</th>
                                    <th className="pb-2 font-medium text-zinc-500">Method X</th>
                                    <th className="pb-2 font-medium text-zinc-500">Method Y</th>
                                </tr>
                            </thead>
                            <tbody className="text-zinc-700 dark:text-zinc-300">
                                <tr className="border-b border-zinc-100 dark:border-zinc-800/50">
                                    <td className="py-2">Accuracy</td>
                                    <td className="py-2">94.2%</td>
                                    <td className="py-2">95.1%</td>
                                </tr>
                                <tr>
                                    <td className="py-2">Overhead</td>
                                    <td className="py-2 text-green-500">Low (12MB)</td>
                                    <td className="py-2 text-red-500">High (84MB)</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}

function GapMock() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="w-full h-full p-6 flex flex-col items-center justify-center bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-fixed"
        >
            <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-md border border-red-200 dark:border-red-900/50 rounded-2xl p-6 shadow-xl max-w-md w-full relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-red-500" />
                <div className="flex items-start gap-4 mb-4">
                    <div className="p-2 bg-red-100 dark:bg-red-500/20 rounded-full text-red-600 dark:text-red-400">
                        <AlertTriangle size={20} />
                    </div>
                    <div>
                        <h3 className="font-semibold text-zinc-900 dark:text-zinc-50">Methodological Discrepancy Found</h3>
                        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">Between Document A & C</p>
                    </div>
                </div>

                <div className="space-y-4 mb-4">
                    <div className="bg-zinc-100 dark:bg-zinc-950 p-3 rounded-lg border border-zinc-200 dark:border-zinc-800">
                        <p className="text-[11px] font-bold text-zinc-400 mb-1">DocA_Methodology.pdf (Pg 4)</p>
                        <p className="text-sm text-zinc-600 dark:text-zinc-300 text-strikethrough">"Samples were cryogenically frozen prior to sequencing."</p>
                    </div>
                    <div className="bg-zinc-100 dark:bg-zinc-950 p-3 rounded-lg border border-zinc-200 dark:border-zinc-800">
                        <p className="text-[11px] font-bold text-zinc-400 mb-1">DocC_Results.pdf (Pg 12)</p>
                        <p className="text-sm text-zinc-600 dark:text-zinc-300">"Room-temperature samples yielded the highest throughput."</p>
                    </div>
                </div>

                <button className="w-full py-2 bg-zinc-900 dark:bg-white text-zinc-50 dark:text-zinc-900 rounded-lg text-sm font-medium hover:opacity-90 transition-opacity">
                    Generate Full Gap Report
                </button>
            </div>
        </motion.div>
    );
}
