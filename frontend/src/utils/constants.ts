// API base URL — uses Vite proxy in dev mode
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// SSE base URL
export const SSE_BASE_URL = import.meta.env.VITE_SSE_BASE_URL || '/sse'

// Maximum undo/redo stack depth
export const MAX_UNDO_STACK = 20

// Shot parameters
export const SHOT_DURATION_MIN = 1
export const SHOT_DURATION_MAX = 30
export const SHOT_DURATION_DEFAULT = 5

// Shot types
export const SHOT_TYPES = [
  '远镜',
  '全景',
  '中景',
  '近景',
  '特写',
  '极特写',
] as const

// Camera movements
export const CAMERA_MOVEMENTS = [
  '固定',
  '推镜',
  '拉镜',
  '摇镜',
  '移镜',
  '跟镜',
  '升镜',
  '降镜',
] as const

// Moods
export const MOODS = [
  '平静',
  '激昂',
  '悲伤',
  '紧张',
  '温馨',
  '恐怖',
  '幽默',
  '庄严',
] as const

// Task status phases
export const TASK_PHASES = [
  { key: 'parse_story', label: '故事解析' },
  { key: 'generate_assets', label: '资产生成' },
  { key: 'generate_keyframes', label: '关键帧生成' },
  { key: 'generate_animation', label: '动画生成' },
  { key: 'generate_audio', label: '配音生成' },
  { key: 'compose_video', label: '视频合成' },
] as const

export type TaskPhase = (typeof TASK_PHASES)[number]['key']
