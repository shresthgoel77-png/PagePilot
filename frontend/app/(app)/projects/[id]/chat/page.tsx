"use client";

import { MessageSquare } from "lucide-react";
import { motion } from "framer-motion";

export default function ChatEmptyState() {
    return (
        <div className="flex-1 flex flex-col items-center justify-center bg-zinc-950 p-8 h-full">
            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="flex flex-col items-center text-center max-w-sm"
            >
                <div className="w-20 h-20 bg-zinc-900 border border-zinc-800 rounded-3xl flex items-center justify-center mb-6 shadow-2xl shadow-cyan-500/10 rotate-3 hover:rotate-0 transition-all cursor-pointer">
                    <MessageSquare className="w-8 h-8 text-cyan-500" />
                </div>
                <h1 className="text-2xl font-black text-white tracking-tight leading-none mb-3">AI Engine Standby</h1>
                <p className="text-sm font-medium text-zinc-500 mb-8 leading-relaxed">
                    Select an active session mapping external bounded matrices securely or initialize a new analytical branch intrinsically.
                </p>
                <div className="w-24 h-1 bg-cyan-500/20 rounded-full overflow-hidden">
                    <motion.div
                        animate={{ x: [-100, 100] }}
                        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                        className="w-1/2 h-full bg-cyan-500 rounded-full"
                    />
                </div>
            </motion.div>
        </div>
    );
}
