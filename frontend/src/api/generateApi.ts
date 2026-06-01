import client from './client'
import type { AsyncTask } from '../types/task'

export interface ParseStoryRequest {
  projectId: string
  storyText: string
}

export interface GenerateAssetsRequest {
  projectId: string
  characterIds?: string[]
  sceneIds?: string[]
}

export interface GenerateKeyframesRequest {
  projectId: string
  shotIds?: string[]
}

export interface GenerateAnimationRequest {
  projectId: string
  shotIds?: string[]
}

export interface GenerateAudioRequest {
  projectId: string
  shotIds?: string[]
}

export interface FullPipelineRequest {
  projectId: string
  storyText: string
}

export const generateApi = {
  parseStory: async (body: ParseStoryRequest): Promise<AsyncTask> => {
    const res = await client.post('/generate/parse-story', body)
    return res.data as AsyncTask
  },

  generateAssets: async (body: GenerateAssetsRequest): Promise<AsyncTask> => {
    const res = await client.post('/generate/assets', body)
    return res.data as AsyncTask
  },

  generateKeyframes: async (body: GenerateKeyframesRequest): Promise<AsyncTask> => {
    const res = await client.post('/generate/keyframes', body)
    return res.data as AsyncTask
  },

  generateAnimation: async (body: GenerateAnimationRequest): Promise<AsyncTask> => {
    const res = await client.post('/generate/animation', body)
    return res.data as AsyncTask
  },

  generateAudio: async (body: GenerateAudioRequest): Promise<AsyncTask> => {
    const res = await client.post('/generate/audio', body)
    return res.data as AsyncTask
  },

  fullPipeline: async (body: FullPipelineRequest): Promise<AsyncTask> => {
    const res = await client.post('/generate/full-pipeline', body)
    return res.data as AsyncTask
  },
}
