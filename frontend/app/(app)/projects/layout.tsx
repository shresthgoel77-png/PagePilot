import { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'ResearchOS | Workspace',
    description: 'Analytical Project Hub bounding PDFs safely',
};

export default function ProjectsLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}
