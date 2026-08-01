import { create } from 'zustand';

interface UIState {
    sidebarCollapsed: boolean;
    commandPaletteOpen: boolean;
    theme: 'light' | 'dark' | 'system';
    setSidebarCollapsed: (collapsed: boolean) => void;
    setCommandPaletteOpen: (open: boolean) => void;
    setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

export const useUIStore = create<UIState>((set) => ({
    sidebarCollapsed: false,
    commandPaletteOpen: false,
    theme: 'dark',
    setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
    setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
    setTheme: (theme) => set({ theme }),
}));
