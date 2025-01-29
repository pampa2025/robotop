import { create } from 'zustand'

interface StoreState {
  rotation: number
  setRotation: (rotation: number) => void
}

export const useStore = create<StoreState>((set) => ({
  rotation: 0,
  setRotation: (rotation: number) => set({ rotation }),
}))