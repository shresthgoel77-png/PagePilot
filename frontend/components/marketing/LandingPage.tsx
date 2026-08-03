import Link from "next/link";
import { Showcase } from "./Showcase";
import { ArrowRight, CheckCircle2, Search, BrainCircuit, LineChart, Lock } from "lucide-react";

export function LandingPage() {
    return (
        <div className="min-h-screen bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50 selection:bg-cyan-500/30 font-sans">
            <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-xl border-b border-zinc-200 dark:border-zinc-900 shadow-sm transition-all duration-300">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-zinc-900 dark:bg-white flex items-center justify-center text-white dark:text-zinc-900 font-bold text-xl leading-none shadow-md">R</div>
                        <span className="font-bold text-lg tracking-tight">ResearchOS</span>
                    </div>
                    <div className="hidden md:flex gap-8 text-sm font-medium text-zinc-600 dark:text-zinc-400">
                        <Link href="/dashboard" className="hover:text-cyan-500 transition-colors">Dashboard</Link>
                        <Link href="/projects" className="hover:text-cyan-500 transition-colors">Projects</Link>
                        <Link href="/resources" className="hover:text-cyan-500 transition-colors">Resources</Link>
                        <Link href="#features" className="hover:text-cyan-500 transition-colors">Features</Link>
                    </div>
                    <div className="flex items-center gap-4">
                        <Link href="/login" className="text-sm font-medium hover:text-cyan-500 transition-colors">
                            Sign In
                        </Link>
                        <Link href="/dashboard" className="text-sm font-medium bg-cyan-500 hover:bg-cyan-400 text-zinc-950 px-5 py-2.5 rounded-lg shadow-[0_0_15px_rgba(6,182,212,0.4)] hover:shadow-[0_0_25px_rgba(6,182,212,0.6)] font-semibold transition-all">
                            Get Started
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <header className="relative pt-32 pb-20 md:pt-48 md:pb-32 px-6 overflow-hidden">
                <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-cyan-900/20 via-zinc-950/0 to-zinc-950/0 dark:from-cyan-900/20 dark:via-zinc-950/0 dark:to-zinc-950/0"></div>
                <div className="max-w-4xl mx-auto text-center space-y-8 relative z-10">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 text-xs font-semibold tracking-wide border border-cyan-500/20">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                        </span>
                        NEW: MULTI-DOCUMENT GAP ANALYSIS
                    </div>
                    <h1 className="text-5xl md:text-7xl font-bold tracking-tighter leading-[1.1]">
                        The AI operating system for <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-blue-500">deep research.</span>
                    </h1>
                    <p className="text-lg md:text-xl text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto leading-relaxed">
                        Chat with papers, synthesize findings across sources, and surface critical research gaps before reviewers do. Your entire workspace, grounded in real citations.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
                        <Link href="/dashboard" className="w-full sm:w-auto flex items-center justify-center gap-2 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 px-8 py-3.5 rounded-xl font-medium hover:scale-[1.02] active:scale-95 transition-all shadow-xl shadow-zinc-900/10 dark:shadow-white/10">
                            Get Started Free
                            <ArrowRight size={18} />
                        </Link>
                        <Link href="/login" className="w-full sm:w-auto flex items-center justify-center px-8 py-3.5 rounded-xl font-medium border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors text-zinc-700 dark:text-zinc-300">
                            Sign In
                        </Link>
                    </div>
                </div>
            </header>

            {/* Social Proof */}
            <div className="border-t border-b border-zinc-200 dark:border-zinc-900 bg-zinc-50 dark:bg-zinc-950/50 py-10 px-6">
                <div className="max-w-6xl mx-auto text-center">
                    <p className="text-sm font-semibold uppercase tracking-widest text-zinc-400 mb-8">Trusted by researchers worldwide</p>
                    <div className="flex flex-wrap justify-center gap-8 md:gap-16 opacity-40 grayscale">
                        {/* Generic Placeholder Marks */}
                        <div className="text-xl font-black tracking-tighter flex items-center gap-2"><div className="w-6 h-6 border-4 border-current rounded-sm"></div> UNIVERSAL</div>
                        <div className="text-xl font-black tracking-tighter flex items-center gap-2"><div className="w-6 h-6 rounded-full bg-current"></div> QUANTUM</div>
                        <div className="text-xl font-black tracking-tighter flex items-center gap-2"><div className="w-6 h-6 border-t-4 border-l-4 border-current"></div> FRONTIER</div>
                        <div className="text-xl font-black tracking-tighter flex items-center gap-2"><div className="w-0 h-0 border-l-[12px] border-l-transparent border-t-[20px] border-current border-r-[12px] border-r-transparent"></div> APEX</div>
                    </div>
                </div>
            </div>

            {/* Interactive Showcase */}
            <Showcase />

            {/* Feature Grid */}
            <section className="bg-zinc-50 dark:bg-zinc-900/30 py-24 px-6 border-y border-zinc-200 dark:border-zinc-900">
                <div className="max-w-6xl mx-auto">
                    <div className="mb-16">
                        <h2 className="text-3xl font-semibold tracking-tight mb-4">Unmatched capabilities for serious work.</h2>
                        <p className="text-zinc-500 dark:text-zinc-400">Purpose-built to handle dense, academic, and technical material securely.</p>
                    </div>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                        <FeatureCard icon={Search} title="Citation-Grounded" desc="Every claim is strictly backed by inline citations linking directly to your source text." />
                        <FeatureCard icon={BrainCircuit} title="Project Workspaces" desc="Isolate different research domains safely. Compare distinct documents side by side." />
                        <FeatureCard icon={LineChart} title="Structured Exports" desc="Transform sprawling PDFs into strictly structured JSON or markdown synthesis reports." />
                        <FeatureCard icon={Lock} title="Secure Infrastructure" desc="JWT authenticated sessions and enterprise-grade isolation for your sensitive PDFs." />
                        <FeatureCard icon={CheckCircle2} title="Persistent History" desc="Never lose a train of thought. Infinite scroll chat histories strictly bound to your account." />
                        <FeatureCard icon={Search} title="Multi-PDF Vector Search" desc="Powered by Qdrant. Semantically query thousands of pages in milliseconds." />
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="py-24 px-6 relative" id="how-it-works">
                <div className="max-w-5xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-semibold tracking-tight">From PDF to synthesis in 3 steps.</h2>
                    </div>
                    <div className="grid md:grid-cols-3 gap-12 relative">
                        <div className="hidden md:block absolute top-[20%] left-[15%] right-[15%] h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent dashed" />
                        <Step number="01" title="Upload your PDFs" desc="Drag and drop your papers securely into isolated project workspaces." />
                        <Step number="02" title="Interrogate & Compare" desc="Run cross-document analysis, chat with sources, and identify knowledge gaps." />
                        <Step number="03" title="Review Cited Answers" desc="Get definitive, structured outputs with clickable citations pointing to the exact page." />
                    </div>
                </div>
            </section>

            {/* Final CTA */}
            <section className="py-24 px-6 bg-zinc-950 dark:bg-zinc-900 text-white text-center">
                <div className="max-w-3xl mx-auto space-y-8">
                    <h2 className="text-4xl md:text-5xl font-bold tracking-tight">Ready to streamline your literature review?</h2>
                    <p className="text-zinc-400 text-lg">Join forward-thinking researchers building better arguments faster.</p>
                    <Link href="/dashboard" className="inline-block bg-white text-zinc-950 px-8 py-4 rounded-xl font-bold hover:scale-[1.02] transition-transform">
                        Start your first research project
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 border-t border-zinc-200 dark:border-zinc-900 px-6">
                <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="flex items-center gap-2 font-bold opacity-70">
                        <div className="w-6 h-6 rounded bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 flex items-center justify-center text-xs">R</div>
                        ResearchOS
                    </div>
                    <div className="flex gap-6 text-sm text-zinc-500 dark:text-zinc-400">
                        <Link href="/login" className="hover:text-zinc-900 dark:hover:text-zinc-50 transition-colors">Sign In</Link>
                        <Link href="/register" className="hover:text-zinc-900 dark:hover:text-zinc-50 transition-colors">Register</Link>
                        <Link href="#features" className="hover:text-zinc-900 dark:hover:text-zinc-50 transition-colors">Features</Link>
                    </div>
                </div>
            </footer>
        </div>
    );
}

function FeatureCard({ icon: Icon, title, desc }: { icon: any, title: string, desc: string }) {
    return (
        <div className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 hover:border-cyan-500/30 transition-colors group">
            <div className="w-10 h-10 rounded-lg bg-zinc-100 dark:bg-zinc-900 flex items-center justify-center text-zinc-900 dark:text-zinc-50 mb-4 group-hover:bg-cyan-500/10 group-hover:text-cyan-600 transition-colors">
                <Icon size={20} />
            </div>
            <h3 className="font-semibold mb-2">{title}</h3>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed">{desc}</p>
        </div>
    );
}

function Step({ number, title, desc }: { number: string, title: string, desc: string }) {
    return (
        <div className="flex flex-col items-center text-center space-y-4 relative z-10">
            <div className="w-12 h-12 rounded-full bg-white dark:bg-zinc-950 border-2 border-zinc-200 dark:border-zinc-800 flex items-center justify-center text-sm font-bold text-cyan-600 dark:text-cyan-400">
                {number}
            </div>
            <h3 className="font-semibold text-lg">{title}</h3>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 max-w-sm">{desc}</p>
        </div>
    );
}
