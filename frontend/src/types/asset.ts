/** Character asset — an anime character with reference image */
export interface Character {
  id: string
  projectId: string
  name: string
  description: string
  appearance: string
  personality: string
  imageUrl: string | null
  thumbnailUrl: string | null
  referencePrompt: string
  voiceProfileId: string | null
  status: 'pending' | 'generating' | 'done' | 'failed'
  createdAt: string
  updatedAt: string
}

/** Scene / background asset */
export interface Scene {
  id: string
  projectId: string
  name: string
  description: string
  setting: string
  timeOfDay: string
  weather: string
  imageUrl: string | null
  thumbnailUrl: string | null
  referencePrompt: string
  status: 'pending' | 'generating' | 'done' | 'failed'
  createdAt: string
  updatedAt: string
}

/** Keyframe generated for a shot */
export interface KeyFrame {
  id: string
  shotId: string
  imageUrl: string
  thumbnailUrl: string
  prompt: string
  width: number
  height: number
  createdAt: string
}

/** Animation clip generated from a keyframe */
export interface Animation {
  id: string
  keyframeId: string
  videoUrl: string
  duration: number
  fps: number
  createdAt: string
}

export type AssetStatus = 'pending' | 'generating' | 'done' | 'failed'
