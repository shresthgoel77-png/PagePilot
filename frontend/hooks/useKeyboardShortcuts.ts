import { useEffect } from 'react';
import { useUiStore } from '@/stores/uiStore';
import { useRouter, usePathname } from 'next/navigation';

export function useKeyboardShortcuts() {
    const { toggleCommandPalette } = useUiStore();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
            const modifier = isMac ? e.metaKey : e.ctrlKey;

            if (modifier && e.key === 'k') {
                e.preventDefault();
                toggleCommandPalette();
            } else if (modifier && e.key === 'n') {
                e.preventDefault();
                // If we are in Dashboard / Projects, maybe open the New Project modal natively
                // Currently, we'll route to projects hub which manages the Create modal implicitly
                router.push('/dashboard?new=true');
            } else if (modifier && e.key === 'u' && pathname.includes('/pdfs')) {
                e.preventDefault();
                // Focus upload zone: Trigger click on dropzone implicitly or open the zone programmatically.
                // Naively binding to a generic document id hook natively:
                const uploadZone = document.getElementById('pdf-upload-zone');
                if (uploadZone) uploadZone.click();
            } else if (modifier && e.key === '/') {
                e.preventDefault();
                // Show Shortcuts help modal natively (can bind via uiStore similarly mapping properly).
                console.log("Shortcut modal triggered implicitly.");
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [toggleCommandPalette, router, pathname]);
}
