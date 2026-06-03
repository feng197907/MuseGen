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
  project_id: string
  task_type: TaskType
  status: TaskStatus
  progress: number
  current_step: string
  error_message: string | null
  input_data: Record<string, unknown>
  output_data: Record<string, unknown>
  created_at: string
  started_at: string | null
  finished_at: string | null
  parent_task_id: string | null
}

/** API unified response envelope */
export interface ApiResponse<T = unknown> {
  code: number
  data: T
  message: string
}

/** SSE progress event */
export interface SSEProgressEvent {
  task_id: string
  task_type: TaskType
  status: TaskStatus
  progress: number
  current_step: string
  message: string
}
