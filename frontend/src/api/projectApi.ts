import client from './client'
import type { Project, ProjectCreateRequest, ProjectUpdateRequest } from '../types/project'

export const projectApi = {
  /** List all projects */
  list: async (): Promise<Project[]> => {
    const res = await client.get('/projects')
    return res.data as Project[]
  },

  /** Get project detail with all associations */
  get: async (id: string): Promise<Project> => {
    const res = await client.get(`/projects/${id}`)
    return res.data as Project
  },

  /** Create new project */
  create: async (body: ProjectCreateRequest): Promise<Project> => {
    const res = await client.post('/projects', body)
    return res.data as Project
  },

  /** Partial-update project */
  update: async (id: string, body: ProjectUpdateRequest): Promise<Project> => {
    const res = await client.patch(`/projects/${id}`, body)
    return res.data as Project
  },

  /** Delete project */
  delete: async (id: string): Promise<void> => {
    await client.delete(`/projects/${id}`)
  },

  /** Undo last operation on a project */
  undo: async (id: string): Promise<void> => {
    await client.post(`/projects/${id}/undo`)
  },

  /** Redo last undone operation */
  redo: async (id: string): Promise<void> => {
    await client.post(`/projects/${id}/redo`)
  },
}
