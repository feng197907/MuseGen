import React from 'react'
import {
  Box,
  Typography,
  Paper,
  Stack,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Button,
  Chip,
} from '@mui/material'
import { useForm, Controller } from 'react-hook-form'
import type { VoiceProfile, VoiceSettings } from '../../types/audio'
import type { Character } from '../../types/asset'

interface VoiceProfileEditorProps {
  character: Character
  voiceProfile: VoiceProfile | null
  onSave: (profile: Partial<VoiceProfile>) => void
}

interface VoiceFormValues {
  provider: 'elevenlabs' | 'volcano'
  voiceId: string
  stability: number
  similarityBoost: number
  style: number
  speed: number
}

const PRESET_ELEVENLABS_VOICES = [
  { id: 'EXAVITQu4vr4xnSDxMaL', label: '女声 · 温柔' },
  { id: 'N2lVS1w4EtoT3dr4eOWO', label: '男声 · 成熟' },
  { id: '21m00Tcm4TlvDq8ikWAM', label: '女声 · 活泼' },
  { id: 'AZnzlk1XvdvUeBnXmlld', label: '男声 · 正太' },
]

const VoiceProfileEditor: React.FC<VoiceProfileEditorProps> = ({ character, voiceProfile, onSave }) => {
  const { control, handleSubmit } = useForm<VoiceFormValues>({
    defaultValues: {
      provider: voiceProfile?.provider || 'elevenlabs',
      voiceId: voiceProfile?.voice_id || '',
      stability: voiceProfile?.settings.stability ?? 0.5,
      similarityBoost: voiceProfile?.settings.similarity_boost ?? 0.75,
      style: voiceProfile?.settings.style ?? 0,
      speed: voiceProfile?.settings.speed ?? 1,
    },
  })

  const onSubmit = (values: VoiceFormValues) => {
    const { provider, voiceId, ...settings } = values
    onSave({
      character_id: character.id,
      provider,
      voiceId,
      settings: settings as VoiceSettings,
    })
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Typography variant="subtitle2" fontWeight={700}>
          {character.name} — 声线配置
        </Typography>
        {voiceProfile && <Chip label="已配置" color="success" size="small" sx={{ height: 18, fontSize: 10 }} />}
      </Box>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Stack spacing={2}>
          <Controller
            name="provider"
            control={control}
            render={({ field }) => (
              <FormControl size="small" fullWidth>
                <InputLabel>TTS 服务</InputLabel>
                <Select {...field} label="TTS 服务">
                  <MenuItem value="elevenlabs">ElevenLabs</MenuItem>
                  <MenuItem value="volcano">火山引擎 TTS</MenuItem>
                </Select>
              </FormControl>
            )}
          />

          <Controller
            name="voiceId"
            control={control}
            render={({ field }) => (
              <FormControl size="small" fullWidth>
                <InputLabel>音色 ID / 预设</InputLabel>
                <Select {...field} label="音色 ID / 预设">
                  {PRESET_ELEVENLABS_VOICES.map((v) => (
                    <MenuItem key={v.id} value={v.id}>{v.label}</MenuItem>
                  ))}
                  <MenuItem value="custom">自定义 ID</MenuItem>
                </Select>
              </FormControl>
            )}
          />

          <Box>
            <Controller
              name="stability"
              control={control}
              render={({ field }) => (
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    稳定性: {field.value.toFixed(2)}
                  </Typography>
                  <Slider value={field.value} onChange={(_, v) => field.onChange(v)} min={0} max={1} step={0.01} size="small" />
                </Box>
              )}
            />
            <Controller
              name="similarityBoost"
              control={control}
              render={({ field }) => (
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    相似度增强: {field.value.toFixed(2)}
                  </Typography>
                  <Slider value={field.value} onChange={(_, v) => field.onChange(v)} min={0} max={1} step={0.01} size="small" />
                </Box>
              )}
            />
            <Controller
              name="speed"
              control={control}
              render={({ field }) => (
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    语速: {field.value.toFixed(1)}x
                  </Typography>
                  <Slider value={field.value} onChange={(_, v) => field.onChange(v)} min={0.5} max={2} step={0.1} size="small" />
                </Box>
              )}
            />
          </Box>

          <Button type="submit" variant="contained" size="small">
            保存声线配置
          </Button>
        </Stack>
      </form>
    </Paper>
  )
}

export default VoiceProfileEditor
