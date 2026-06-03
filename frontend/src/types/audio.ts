/** Audio track tied to a project timeline */
export interface AudioTrack {
  id: string
  project_id: string
  shot_id: string | null
  name: string
  type: 'voice' | 'bgm' | 'sfx'
  audio_url: string
  duration: number
  volume: number
  start_time: number
  created_at: string
}

/** Voice profile for a character */
export interface VoiceProfile {
  id: string
  character_id: string
  name: string
  provider: 'elevenlabs' | 'volcano'
  voice_id: string
  settings: VoiceSettings
  created_at: string
}

export interface VoiceSettings {
  stability: number
  similarity_boost: number
  style: number
  speed: number
}
