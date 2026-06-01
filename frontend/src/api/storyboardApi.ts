import client from './client'
import type { Storyboard, Shot, ShotUpdateRequest, ShotReorderRequest } from '../types/project'

export const storyboardApi = {
  /** Get the storyboard (with shots) for a project */
  getByProject: async (projectId: string): Promise<Storyboard> => {
    const res = await client.get(`/storyboards/${projectId}`)
    return res.data as Storyboard
  },

  /** Update a single shot's parameters */
  updateShot: async (shotId: string, body: ShotUpdateRequest): Promise<Shot> => {
    const res = await client.patch(`/storyboards/shots/${shotId}`, body)
    return res.data as Shot
  },

  /** Reorder shots by submitting ordered shot IDs */
  reorderShots: async (body: ShotReorderRequest): Promise<void> => {
    await client.post('/storyboards/shots/reorder', body)
  },
}
