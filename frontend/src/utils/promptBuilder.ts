import type { Shot } from '../types/project'
import type { Character, Scene } from '../types/asset'

/**
 * Build an SDXL image generation prompt from shot + character + scene context.
 */
export function buildShotPrompt(
  shot: Shot,
  characters: Character[],
  scene: Scene | null,
): string {
  const parts: string[] = []

  // Anime style prefix
  parts.push('anime style, high quality, detailed illustration')

  // Characters
  const shotChars = characters.filter((c) => shot.character_ids.includes(c.id))
  if (shotChars.length > 0) {
    const charDescs = shotChars.map((c) => c.appearance).join(', ')
    parts.push(charDescs)
  }

  // Scene
  if (scene) {
    parts.push(scene.reference_prompt || scene.description)
    if (scene.time_of_day) parts.push(scene.time_of_day)
    if (scene.weather) parts.push(scene.weather)
  }

  // Shot description
  if (shot.description) {
    parts.push(shot.description)
  }

  // Shot type → framing hint
  const shotTypeMap: Record<string, string> = {
    远镜: 'extreme wide shot',
    全景: 'full shot',
    中景: 'medium shot',
    近景: 'medium close-up',
    特写: 'close-up',
    极特写: 'extreme close-up',
  }
  if (shotTypeMap[shot.shot_type]) {
    parts.push(shotTypeMap[shot.shot_type])
  }

  // Mood → lighting hint
  const moodMap: Record<string, string> = {
    激昂: 'dynamic lighting, vibrant colors',
    悲伤: 'melancholic, muted tones, soft shadows',
    紧张: 'dramatic lighting, high contrast',
    温馨: 'warm lighting, soft glow',
    恐怖: 'dark atmosphere, eerie shadows',
    幽默: 'bright colors, playful style',
    庄严: 'epic lighting, cinematic',
    平静: 'peaceful, natural lighting',
  }
  if (moodMap[shot.mood]) {
    parts.push(moodMap[shot.mood])
  }

  return parts.join(', ')
}

/**
 * Build the negative prompt used for SDXL generation.
 */
export function buildNegativePrompt(): string {
  return [
    'low quality',
    'blurry',
    'bad anatomy',
    'deformed',
    'ugly',
    'watermark',
    'text',
    'signature',
    'nsfw',
    'worst quality',
    'jpeg artifacts',
  ].join(', ')
}

/**
 * Build a TTS prompt by adding narration markers.
 */
export function buildTTSPrompt(dialogue: string, characterName: string): string {
  return `[${characterName}]: ${dialogue}`
}
