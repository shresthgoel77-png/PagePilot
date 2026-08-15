'use client';

import { useEffect, useRef } from 'react';
import { useAuth } from '@clerk/nextjs';
import api from '../lib/api';

export function AxiosInterceptor({ children }: { children: React.ReactNode }) {
    const { getToken } = useAuth();
    const interceptorId = useRef<number | null>(null);

    useEffect(() => {
        // Clear existing interceptor if any
        if (interceptorId.current !== null) {
            api.interceptors.request.eject(interceptorId.current);
        }

        const id = api.interceptors.request.use(async (config) => {
            try {
                if (process.env.NEXT_PUBLIC_BYPASS_CLERK === 'true') {
                    config.headers.set('Authorization', `Bearer MOCK_TOKEN`);
                } else {
                    const token = await getToken();
                    if (token) {
                        config.headers.set('Authorization', `Bearer ${token}`);
                    }
                }
            } catch (error) {
                console.error('Error fetching Clerk token within interceptor:', error);
            }
            return config;
        }, (error) => {
            return Promise.reject(error);
        });

        interceptorId.current = id;

        return () => {
            if (interceptorId.current !== null) {
                api.interceptors.request.eject(interceptorId.current);
                interceptorId.current = null;
            }
        };
    }, [getToken]);

    return <>{children}</>;
}
