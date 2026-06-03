"""LLM and SD prompt templates."""


STORY_PARSE_PROMPT = """You are an expert anime story analyst. Parse the given story text and extract structured data.

You MUST output a valid JSON object with the following structure:
{
  "characters": [
    {
      "name": "Character name",
      "description": "Brief character description",
      "appearance": "Detailed visual appearance for anime illustration (hair color, eye color, clothing, accessories, etc.)",
      "personality": "Character personality traits",
      "reference_prompt": "English prompt for SDXL character portrait generation. Include the global style: 'modern anime, cel shading, crisp lineart, vibrant colors, studio quality'"
    }
  ],
  "scenes": [
    {
      "name": "Scene name",
      "description": "Scene description",
      "setting": "Setting details (location, architecture, etc.)",
      "time_of_day": "Time of day (白天/黄昏/夜晚/黎明)",
      "weather": "Weather (晴朗/多云/雨天/雪天/雾天)",
      "reference_prompt": "English prompt for SDXL background generation. Include the global style: 'modern anime, cel shading, crisp lineart, vibrant colors, studio quality'"
    }
  ],
  "shots": [
    {
      "title": "Shot title",
      "description": "What happens in this shot (visual description)",
      "dialogue": "Character dialogue or narration in this shot",
      "character_names": ["Names of characters appearing in this shot"],
      "scene_name": "Name of the scene for this shot",
      "shot_type": "景别: 远镜/全景/中景/近景/特写/极特写",
      "camera_movement": "运镜: 固定/推镜/拉镜/摇镜/移镜/跟镜/升镜/降镜",
      "duration": 5.0,
      "mood": "情绪: 平静/激昂/悲伤/紧张/温馨/恐怖/幽默/庄严"
    }
  ]
}

IMPORTANT — Global visual style (applies to ALL reference_prompt fields above):
The entire project uses a single consistent visual style:
"modern anime, cel shading, crisp clean lineart, vibrant saturated colors, professional studio quality animation art, flat coloring with subtle gradients"

All reference_prompt fields MUST include this exact style phrase to ensure visual consistency across all generated images.

Important guidelines:
1. Break the story into 6-20 shots, each 3-10 seconds long
2. Each shot should have clear visual content and dialogue
3. Character appearances should be detailed enough for anime illustration
4. Scene descriptions should include atmosphere and lighting
5. Reference prompts should be in English, optimized for SDXL, and MUST include the global style phrase
6. Match shot types and camera movements to the emotional content
7. Distribute dialogue naturally across shots
"""

NEGATIVE_PROMPT_DEFAULT = (
    "low quality, blurry, bad anatomy, deformed, ugly, watermark, text, "
    "signature, nsfw, worst quality, jpeg artifacts, missing fingers, "
    "extra fingers, cropped, out of frame, multiple people, group shot, "
    "collage, crowd, more than one person, sketch, rough, unfinished, "
    "(3d:1.4), (realistic:1.4), (photorealism:1.4), (photo:1.4), "
    "(cgi:1.4), (render:1.4), (different art style:1.4), "
    "(inconsistent style:1.4), grainy, noise, messy, "
    "photograph, camera lens, bokeh depth of field, hyperrealism"
)

NEGATIVE_PROMPT_CHARACTER = (
    "low quality, blurry, bad anatomy, deformed, ugly, watermark, text, "
    "signature, nsfw, worst quality, jpeg artifacts, missing fingers, "
    "extra fingers, cropped, out of frame, multiple people, group shot, "
    "collage, crowd, more than one person, 2boys, 2girls, group, "
    "split screen, panel, comic page, sketch, rough, unfinished, "
    "(3d:1.4), (realistic:1.4), (photorealism:1.4), (photo:1.4), "
    "(cgi:1.4), (render:1.4), (different art style:1.4), "
    "(inconsistent style:1.4), (grainy:1.2), noise, messy, "
    "photograph, camera lens, bokeh depth of field, hyperrealism"
)

ANIME_STYLE_PREFIX = (
    "(masterpiece:1.3), (best quality:1.3), "
    "(anime style:1.4), (2d illustration:1.3), "
    "cel shading, crisp clean lineart, flat coloring, "
    "vibrant saturated colors, professional anime art, studio quality, "
    "soft gradients, (hand drawn:1.2), "
)
