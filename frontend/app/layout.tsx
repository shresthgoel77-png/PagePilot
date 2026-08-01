import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Providers from './providers';
import { RouteGuard } from '@/components/route-guard';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'ResearchOS Frontend',
    description: 'ResearchOS frontend client application',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <Providers>
                    <RouteGuard>{children}</RouteGuard>
                </Providers>
            </body>
        </html>
    );
}
