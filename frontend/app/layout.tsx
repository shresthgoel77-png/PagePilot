import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Providers from './providers';
import { ClerkProvider } from '@/lib/demo-auth';

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
        <ClerkProvider>
            <html lang="en">
                <body className={inter.className}>
                    <Providers>
                        {children}
                    </Providers>
                </body>
            </html>
        </ClerkProvider>
    );
}
