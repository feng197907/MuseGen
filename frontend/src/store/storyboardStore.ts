import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import type { Storyboard, Shot, ShotUpdateRequest } from '../types/project'

interface StoryboardState {
  storyboard: Storyboard | null
  selectedShotId: string | null
  isLoading: boolean
}

interface StoryboardActions {
  setStoryboard: (sb: Storyboard | null) => void
  setSelectedShot: (id: string | null) => void
  updateShot: (shotId: string, updates: ShotUpdateRequest) => void
  reorderShots: (orderedIds: string[]) => void
  updateShotStatus: (shotId: string, status: Shot['status']) => void
  setLoading: (loading: boolean) => void
}

const useStoryboardStore = create<StoryboardState & StoryboardActions>()(
  immer((set) => ({
    storyboard: null,
    selectedShotId: null,
    isLoading: false,

    setStoryboard: (sb) => {
      set((state) => {
        state.storyboard = sb
      })
    },

    setSelectedShot: (id) => {
      set((state) => {
        state.selectedShotId = id
      })
    },

    updateShot: (shotId, updates) => {
      set((state) => {
        if (!state.storyboard) return
        const shot = state.storyboard.shots.find((s) => s.id === shotId)
        if (shot) {
          Object.assign(shot, updates)
        }
      })
    },

    reorderShots: (orderedIds) => {
      set((state) => {
        if (!state.storyboard) return
        const map = new Map(state.storyboard.shots.map((s) => [s.id, s]))
        state.storyboard.shots = orderedIds
          .filter((id) => map.has(id))
          .map((id, idx) => {
            const shot = map.get(id)!
            shot.order = idx
            return shot
          })
      })
    },

    updateShotStatus: (shotId, status) => {
      set((state) => {
        if (!state.storyboard) return
        const shot = state.storyboard.shots.find((s) => s.id === shotId)
        if (shot) {
          shot.status = status
        }
      })
    },

    setLoading: (loading) => {
      set((state) => {
        state.isLoading = loading
      })
    },
  })),
)

export default useStoryboardStore
