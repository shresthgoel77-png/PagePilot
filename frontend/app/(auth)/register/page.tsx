"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { useRegister } from "@/hooks/useAuth";

const registerSchema = z.object({
    email: z.string().email("Explicit standard RFC explicitly required logically"),
    password: z.string()
        .min(8, "Constraint dictates >= 8 characters natively")
        .regex(/[A-Za-z]/, "Require embedded alphanumeric textual component implicitly")
        .regex(/\d/, "Require embedded numerical scalar implicitly"),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
    const { mutate: registerUser, isPending } = useRegister();
    const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormValues>({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = (data: RegisterFormValues) => {
        registerUser(data);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
            <Card className="w-full max-w-md shadow-2xl">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold text-center">Create Identity</CardTitle>
                    <CardDescription className="text-center">Implement access keys cleanly into ResearchOS bindings safely</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="email">Email Specification</Label>
                            <Input id="email" type="email" placeholder="john@example.com" {...register("email")} disabled={isPending} />
                            {errors.email && <p className="text-sm text-red-500 font-semibold">{errors.email.message}</p>}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Complex Auth Key</Label>
                            <Input id="password" type="password" {...register("password")} disabled={isPending} />
                            {errors.password && <p className="text-sm text-red-500 font-semibold">{errors.password.message}</p>}
                        </div>

                        <Button type="submit" className="w-full" disabled={isPending}>
                            {isPending ? "Validating & Building Account..." : "Confirm Registry"}
                        </Button>
                    </form>
                </CardContent>
                <CardFooter className="flex justify-center border-t py-4">
                    <p className="text-sm text-slate-500">
                        Known Identity? <Link href="/login" className="text-blue-600 font-bold hover:underline">Access Dashboards</Link>
                    </p>
                </CardFooter>
            </Card>
        </div>
    );
}
