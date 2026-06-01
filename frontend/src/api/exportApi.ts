import client from './client'
import type { AsyncTask } from '../types/task'

export const exportApi = {
  /** Trigger video composition export */
  compose: async (projectId: string): Promise<AsyncTask> => {
    const res = await client.post('/export/compose', { projectId })
    return res.data as AsyncTask
  },

  /** Get download URL for the final video */
  getDownloadUrl: (taskId: string): string => {
    return `/api/v1/export/${taskId}/download`
  },
}
