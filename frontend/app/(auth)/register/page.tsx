"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRegister } from "@/hooks/useAuth";
import { Loader2 } from "lucide-react";

const registerSchema = z.object({
    email: z.string().email("Invalid email format"),
    password: z.string()
        .min(8, "Password must be at least 8 characters")
        .regex(/[A-Za-z]/, "Must contain at least one letter")
        .regex(/\d/, "Must contain at least one number"),
    confirmPassword: z.string().min(1, "Please confirm your password")
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
    const { mutate: registerUser, isPending, isError, error } = useRegister();
    const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterFormValues>({
        resolver: zodResolver(registerSchema),
    });

    const currentPassword = watch("password", "");

    const onSubmit = (data: RegisterFormValues) => {
        // Drop confirmPassword before sending to API
        const { confirmPassword, ...apiData } = data;
        registerUser(apiData);
    };

    // Calculate dummy password strength (1-4)
    const getStrength = (pwd: string) => {
        if (!pwd) return 0;
        let score = 0;
        if (pwd.length >= 8) score += 1;
        if (/[A-Z]/.test(pwd)) score += 1;
        if (/[0-9]/.test(pwd)) score += 1;
        if (/[^A-Za-z0-9]/.test(pwd)) score += 1;
        return score;
    };

    const strength = getStrength(currentPassword);

    return (
        <div className="min-h-screen flex items-center justify-center bg-zinc-950 relative overflow-hidden text-zinc-100 p-4">
            {/* Top-center radial gradient */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none" />

            {/* Subtle Noise Texture Mapping Gracefully */}
            <div className="absolute inset-0 z-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] pointer-events-none mix-blend-overlay"></div>

            <div className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl relative z-10 overflow-hidden flex flex-col p-8 my-8">

                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold tracking-tight text-white mb-2">Start your research journey</h1>
                    <p className="text-sm text-zinc-400">Join ResearchOS and accelerate your workflows</p>
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
                        <Label htmlFor="password" className="text-zinc-300">Password</Label>
                        <Input
                            id="password"
                            type="password"
                            className="bg-zinc-950 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-cyan-500 focus-visible:border-cyan-500"
                            {...register("password")}
                            disabled={isPending}
                        />
                        {errors.password && <p className="text-xs text-red-500 font-medium">{errors.password.message}</p>}

                        {/* Dummy Password Strength Component */}
                        {currentPassword.length > 0 && (
                            <div className="pt-2 flex flex-col space-y-1.5">
                                <div className="flex items-center space-x-1 w-full h-1.5 rounded-full overflow-hidden">
                                    <div className={`h-full flex-1 transition-colors duration-300 ${strength >= 1 ? 'bg-red-500' : 'bg-zinc-800'}`} />
                                    <div className={`h-full flex-1 transition-colors duration-300 ${strength >= 2 ? 'bg-yellow-500' : 'bg-zinc-800'}`} />
                                    <div className={`h-full flex-1 transition-colors duration-300 ${strength >= 3 ? 'bg-amber-500' : 'bg-zinc-800'}`} />
                                    <div className={`h-full flex-1 transition-colors duration-300 ${strength >= 4 ? 'bg-emerald-500' : 'bg-zinc-800'}`} />
                                </div>
                                <p className="text-[10px] text-zinc-500 text-right uppercase tracking-wider font-semibold">
                                    {strength === 0 ? "" : strength === 1 ? "Weak" : strength === 2 ? "Fair" : strength === 3 ? "Good" : "Strong"}
                                </p>
                            </div>
                        )}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="confirmPassword" className="text-zinc-300">Confirm Password</Label>
                        <Input
                            id="confirmPassword"
                            type="password"
                            className="bg-zinc-950 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-cyan-500 focus-visible:border-cyan-500"
                            {...register("confirmPassword")}
                            disabled={isPending}
                        />
                        {errors.confirmPassword && <p className="text-xs text-red-500 font-medium">{errors.confirmPassword.message}</p>}
                    </div>

                    {isError && (
                        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                            <p className="text-sm text-red-400 font-medium text-center">
                                {/* @ts-ignore */}
                                {error?.response?.data?.detail || "Registration failed. Try again."}
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
                                <span>Registering...</span>
                            </div>
                        ) : "Create Account"}
                    </Button>
                </form>

                <div className="mt-8 text-center text-sm text-zinc-500">
                    Already have an account?{" "}
                    <Link href="/login" className="text-cyan-500 font-semibold hover:text-cyan-400 hover:underline transition-colors">
                        Sign In
                    </Link>
                </div>
            </div>
        </div>
    );
}
