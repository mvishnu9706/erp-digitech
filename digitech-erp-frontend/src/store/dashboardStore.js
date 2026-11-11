import { create } from 'zustand';

export const useDashboardStore = create((set) => ({
  stats: {},
  setStats: (stats) => set({ stats }),
}));
