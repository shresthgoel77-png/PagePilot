"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogin } from "@/hooks/useAuth";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { useState } from "react";

const loginSchema = z.object({
    email: z.string().email("Invalid email format"),
    password: z.string().min(1, "Password is required"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
    const { mutate: login, isPending, isError, error } = useLogin();
    const [showPassword, setShowPassword] = useState(false);
    const { register, handleSubmit, formState: { errors } } = useForm<LoginFormValues>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = (data: LoginFormValues) => {
        login(data);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-zinc-950 relative overflow-hidden text-zinc-100 p-4">
            {/* Top-center radial gradient */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none" />

            {/* Subtle Noise Texture Mapping Gracefully */}
            <div className="absolute inset-0 z-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] pointer-events-none mix-blend-overlay"></div>

            <div className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl relative z-10 overflow-hidden flex flex-col p-8">

                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Welcome back to ResearchOS</h1>
                    <p className="text-sm text-zinc-400">Authenticate securely to access your workspace</p>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    <div className="space-y-2">
                        <Label htmlFor="email" className="text-zinc-300">Email Address</Label>
                        <Input
                            id="email"
                            type="email"
                            placeholder="john@example.com"
                            className="bg-zinc-950 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-cyan-500 focus-visible:border-cyan-500"
                            {...register("email")}
                            disabled={isPending}
                        />
                        {errors.email && <p className="text-xs text-red-500 font-medium">{errors.email.message}</p>}
                    </div>

                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <Label htmlFor="password" className="text-zinc-300">Password</Label>
                            <Link href="#" className="text-xs font-medium text-cyan-500 hover:text-cyan-400 hover:underline">
                                Forgot password?
                            </Link>
                        </div>
                        <div className="relative">
                            <Input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                className="bg-zinc-950 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-cyan-500 focus-visible:border-cyan-500 pr-10"
                                {...register("password")}
                                disabled={isPending}
                            />
                            <button
                                type="button"
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 focus:outline-none"
                                onClick={() => setShowPassword(!showPassword)}
                                aria-label={showPassword ? "Hide password" : "Show password"}
                            >
                                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                        </div>
                        {errors.password && <p className="text-xs text-red-500 font-medium">{errors.password.message}</p>}
                    </div>

                    <div className="flex items-center space-x-2">
                        <div className="flex items-center h-5">
                            <input
                                id="remember_me"
                                type="checkbox"
                                className="w-4 h-4 border-zinc-800 rounded bg-zinc-950 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-zinc-900"
                            />
                        </div>
                        <Label htmlFor="remember_me" className="text-sm font-normal text-zinc-400 cursor-pointer">
                            Remember me for 30 days
                        </Label>
                    </div>

                    {isError && (
                        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                            <p className="text-sm text-red-400 font-medium text-center">
                                {/* @ts-ignore */}
                                {error?.response?.data?.detail || "Invalid login credentials."}
                            </p>
                        </div>
                    )}

                    <Button
                        type="submit"
                        className="w-full bg-cyan-500 text-zinc-950 font-semibold hover:bg-cyan-400 hover:shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300"
                        disabled={isPending}
                    >
                        {isPending ? (
                            <div className="flex items-center justify-center space-x-2">
                                <Loader2 className="h-4 w-4 animate-spin text-zinc-950" />
                                <span>Authenticating...</span>
                            </div>
                        ) : "Login to Workspace"}
                    </Button>
                </form>

                <div className="mt-8 text-center text-sm text-zinc-500">
                    New to ResearchOS?{" "}
                    <Link href="/register" className="text-cyan-500 font-semibold hover:text-cyan-400 hover:underline transition-colors">
                        Create an account
                    </Link>
                </div>
            </div>
        </div>
    );
}
