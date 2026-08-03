import { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'ResearchOS | Dashboard',
    description: 'SaaS Command Center parsing projects effectively',
};

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}
