import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import type { Character, Scene } from '../types/asset'

interface AssetState {
  characters: Character[]
  scenes: Scene[]
  selectedCharacterId: string | null
  selectedSceneId: string | null
  isLoading: boolean
}

interface AssetActions {
  setCharacters: (chars: Character[]) => void
  setScenes: (scenes: Scene[]) => void
  addCharacter: (char: Character) => void
  addScene: (scene: Scene) => void
  updateCharacter: (id: string, updates: Partial<Character>) => void
  updateScene: (id: string, updates: Partial<Scene>) => void
  removeCharacter: (id: string) => void
  removeScene: (id: string) => void
  setSelectedCharacter: (id: string | null) => void
  setSelectedScene: (id: string | null) => void
  setLoading: (loading: boolean) => void
}

const useAssetStore = create<AssetState & AssetActions>()(
  immer((set) => ({
    characters: [],
    scenes: [],
    selectedCharacterId: null,
    selectedSceneId: null,
    isLoading: false,

    setCharacters: (chars) => {
      set((state) => {
        state.characters = chars
      })
    },

    setScenes: (scenes) => {
      set((state) => {
        state.scenes = scenes
      })
    },

    addCharacter: (char) => {
      set((state) => {
        state.characters.push(char)
      })
    },

    addScene: (scene) => {
      set((state) => {
        state.scenes.push(scene)
      })
    },

    updateCharacter: (id, updates) => {
      set((state) => {
        const char = state.characters.find((c) => c.id === id)
        if (char) Object.assign(char, updates)
      })
    },

    updateScene: (id, updates) => {
      set((state) => {
        const scene = state.scenes.find((s) => s.id === id)
        if (scene) Object.assign(scene, updates)
      })
    },

    removeCharacter: (id) => {
      set((state) => {
        state.characters = state.characters.filter((c) => c.id !== id)
      })
    },

    removeScene: (id) => {
      set((state) => {
        state.scenes = state.scenes.filter((s) => s.id !== id)
      })
    },

    setSelectedCharacter: (id) => {
      set((state) => {
        state.selectedCharacterId = id
      })
    },

    setSelectedScene: (id) => {
      set((state) => {
        state.selectedSceneId = id
      })
    },

    setLoading: (loading) => {
      set((state) => {
        state.isLoading = loading
      })
    },
  })),
)

export default useAssetStore
