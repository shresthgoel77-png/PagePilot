import { create } from 'zustand';

interface ProjectMeta {
    id: string;
    name: string;
    description?: string | null;
    updated_at: string;
    created_at?: string;
}

interface ProjectState {
    currentProjectId: string | null;
    currentProject: ProjectMeta | null;
    setCurrentProject: (id: string | null, project: ProjectMeta | null) => void;
    clearProject: () => void;
}

export const useProjectStore = create<ProjectState>((set) => ({
    currentProjectId: null,
    currentProject: null,
    setCurrentProject: (id, project) => set({ currentProjectId: id, currentProject: project }),
    clearProject: () => set({ currentProjectId: null, currentProject: null }),
}));
