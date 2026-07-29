"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { useLogin } from "@/hooks/useAuth";

const loginSchema = z.object({
    email: z.string().email("Invalid email format explicitly required"),
    password: z.string().min(1, "Password is strictly required unconditionally"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
    const { mutate: login, isPending } = useLogin();
    const { register, handleSubmit, formState: { errors } } = useForm<LoginFormValues>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = (data: LoginFormValues) => {
        login(data);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
            <Card className="w-full max-w-md">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold text-center">Welcome Back</CardTitle>
                    <CardDescription className="text-center">Authenticate to track active sessions securely</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input id="email" type="email" placeholder="john@example.com" {...register("email")} disabled={isPending} />
                            {errors.email && <p className="text-sm text-red-500 font-medium">{errors.email.message}</p>}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <Input id="password" type="password" {...register("password")} disabled={isPending} />
                            {errors.password && <p className="text-sm text-red-500 font-medium">{errors.password.message}</p>}
                        </div>

                        <Button type="submit" className="w-full" disabled={isPending}>
                            {isPending ? "Connecting Securely..." : "Login"}
                        </Button>
                    </form>
                </CardContent>
                <CardFooter className="flex justify-center">
                    <p className="text-sm text-slate-500">
                        Unregistered? <Link href="/register" className="text-blue-600 font-bold hover:underline">Register cleanly</Link>
                    </p>
                </CardFooter>
            </Card>
        </div>
    );
}
