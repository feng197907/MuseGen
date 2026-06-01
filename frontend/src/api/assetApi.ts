import client from './client'
import type { Character, Scene } from '../types/asset'

export const assetApi = {
  /** Get characters for a project */
  listCharacters: async (projectId: string): Promise<Character[]> => {
    const res = await client.get(`/assets/characters?project_id=${projectId}`)
    return res.data as Character[]
  },

  /** Get scenes for a project */
  listScenes: async (projectId: string): Promise<Scene[]> => {
    const res = await client.get(`/assets/scenes?project_id=${projectId}`)
    return res.data as Scene[]
  },

  /** Regenerate a character portrait */
  regenerateCharacter: async (characterId: string): Promise<Character> => {
    const res = await client.post(`/assets/characters/${characterId}/regenerate`)
    return res.data as Character
  },
}
