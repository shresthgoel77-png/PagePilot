import { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'ResearchOS | Register',
    description: 'Create an account to accelerate your workflows',
};

export default function RegisterLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}
