/** Audio track tied to a project timeline */
export interface AudioTrack {
  id: string
  projectId: string
  shotId: string | null
  name: string
  type: 'voice' | 'bgm' | 'sfx'
  audioUrl: string
  duration: number
  volume: number
  startTime: number
  createdAt: string
}

/** Voice profile for a character */
export interface VoiceProfile {
  id: string
  characterId: string
  name: string
  provider: 'elevenlabs' | 'volcano'
  voiceId: string
  settings: VoiceSettings
  createdAt: string
}

export interface VoiceSettings {
  stability: number
  similarityBoost: number
  style: number
  speed: number
}
