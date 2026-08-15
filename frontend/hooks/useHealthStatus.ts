import { useState, useEffect } from 'react';

export type HealthStatusType = 'green' | 'yellow' | 'red';

export function useHealthStatus(intervalMs: number = 10000) {
    const [status, setStatus] = useState<HealthStatusType>('yellow');

    useEffect(() => {
        let isMounted = true;

        const checkHealth = async () => {
            try {
                const res = await fetch('http://localhost:8000/health');
                if (res.ok) {
                    const data = await res.json();
                    if (isMounted) {
                        setStatus(data.status === 'ok' ? 'green' : 'yellow');
                    }
                } else {
                    if (isMounted) setStatus('red');
                }
            } catch (err) {
                if (isMounted) setStatus('red');
            }
        };

        checkHealth();
        const intervalId = setInterval(checkHealth, intervalMs);

        return () => {
            isMounted = false;
            clearInterval(intervalId);
        };
    }, [intervalMs]);

    return status;
}
