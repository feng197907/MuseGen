import { useQuery } from '@tanstack/react-query'
import client from '../api/client'
import type { AsyncTask } from '../types/task'

interface UseTaskPollingOptions {
  taskId: string | null
  onDone?: (task: AsyncTask) => void
  onFailed?: (task: AsyncTask) => void
  /** Polling interval in ms, default 2000 */
  interval?: number
  enabled?: boolean
}

/**
 * Polls a Celery async task until it reaches terminal status (done/failed).
 */
const useTaskPolling = ({
  taskId,
  onDone,
  onFailed,
  interval = 2000,
  enabled = true,
}: UseTaskPollingOptions) => {
  return useQuery<AsyncTask>({
    queryKey: ['task', taskId],
    queryFn: async () => {
      const res = await client.get(`/tasks/${taskId}`)
      return res.data as AsyncTask
    },
    enabled: Boolean(taskId) && enabled,
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data) return interval
      if (data.status === 'done') {
        onDone?.(data)
        return false
      }
      if (data.status === 'failed') {
        onFailed?.(data)
        return false
      }
      return interval
    },
    staleTime: 0,
  })
}

export default useTaskPolling
