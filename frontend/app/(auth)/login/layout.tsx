import { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'ResearchOS | Login',
    description: 'Authenticate securely to access your workspace',
};

export default function LoginLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}
