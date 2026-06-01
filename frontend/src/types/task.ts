export type TaskStatus = 'queued' | 'running' | 'done' | 'failed'

export type TaskType =
  | 'parse_story'
  | 'generate_assets'
  | 'generate_keyframes'
  | 'generate_animation'
  | 'generate_audio'
  | 'compose_video'
  | 'full_pipeline'

export interface AsyncTask {
  id: string
  projectId: string
  taskType: TaskType
  status: TaskStatus
  progress: number
  currentStep: string
  errorMessage: string | null
  inputData: Record<string, unknown>
  outputData: Record<string, unknown>
  createdAt: string
  startedAt: string | null
  finishedAt: string | null
  parentTaskId: string | null
}

/** API unified response envelope */
export interface ApiResponse<T = unknown> {
  code: number
  data: T
  message: string
}

/** SSE progress event */
export interface SSEProgressEvent {
  taskId: string
  taskType: TaskType
  status: TaskStatus
  progress: number
  currentStep: string
  message: string
}
