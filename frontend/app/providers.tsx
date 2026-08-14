'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { AxiosInterceptor } from '../components/AxiosInterceptor';

export default function Providers({ children }: { children: React.ReactNode }) {
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: {
                    queries: {
                        staleTime: 5 * 60 * 1000, // Explicitly bounded to 5 minutes 
                    },
                },
            })
    );

    return (
        <QueryClientProvider client={queryClient}>
            <AxiosInterceptor>
                {children}
            </AxiosInterceptor>
        </QueryClientProvider>
    );
}
