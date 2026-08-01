"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

function SplashScreen() {
    return (
        <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5, ease: "easeInOut" }}
            className="fixed inset-0 flex items-center justify-center bg-zinc-950 z-50"
        >
            <motion.h1
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="text-4xl md:text-6xl font-black tracking-tighter text-cyan-500"
            >
                ResearchOS
            </motion.h1>
        </motion.div>
    );
}

export default function Home() {
    const [showSplash, setShowSplash] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const timer = setTimeout(() => {
            setShowSplash(false);
        }, 1500);

        return () => clearTimeout(timer);
    }, []);

    useEffect(() => {
        if (!showSplash) {
            router.push("/dashboard");
        }
    }, [showSplash, router]);

    return (
        <AnimatePresence>
            {showSplash && <SplashScreen />}
        </AnimatePresence>
    );
}
