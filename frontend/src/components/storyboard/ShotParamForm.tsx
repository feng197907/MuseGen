import React, { useEffect } from 'react'
import {
  Stack,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Typography,
  Box,
  Chip,
  Autocomplete,
} from '@mui/material'
import { useForm, Controller } from 'react-hook-form'
import type { Shot } from '../../types/project'
import type { Character, Scene } from '../../types/asset'
import { SHOT_TYPES, CAMERA_MOVEMENTS, MOODS, SHOT_DURATION_MIN, SHOT_DURATION_MAX } from '../../utils/constants'

interface ShotParamFormProps {
  shot: Shot
  characters: Character[]
  scenes: Scene[]
  onUpdate: (updates: Partial<Shot>) => void
}

type FormValues = {
  title: string
  description: string
  dialogue: string
  shotType: string
  cameraMovement: string
  duration: number
  mood: string
  promptOverride: string
  characterIds: string[]
  sceneId: string
}

const ShotParamForm: React.FC<ShotParamFormProps> = ({ shot, characters, scenes, onUpdate }) => {
  const { control, handleSubmit, reset, watch } = useForm<FormValues>({
    defaultValues: {
      title: shot.title,
      description: shot.description,
      dialogue: shot.dialogue,
      shotType: shot.shot_type,
      cameraMovement: shot.camera_movement,
      duration: shot.duration,
      mood: shot.mood,
      promptOverride: shot.prompt_override || '',
      characterIds: shot.character_ids,
      sceneId: shot.scene_id || '',
    },
  })

  // Reset form when shot changes
  useEffect(() => {
    reset({
      title: shot.title,
      description: shot.description,
      dialogue: shot.dialogue,
      shotType: shot.shot_type,
      cameraMovement: shot.camera_movement,
      duration: shot.duration,
      mood: shot.mood,
      promptOverride: shot.prompt_override || '',
      characterIds: shot.character_ids,
      sceneId: shot.scene_id || '',
    })
  }, [shot.id, reset])

  const onSubmit = (values: FormValues) => {
    onUpdate({ ...values, sceneId: values.sceneId || null })
  }

  return (
    <form onBlur={handleSubmit(onSubmit)}>
      <Stack spacing={2}>
        <Controller
          name="title"
          control={control}
          render={({ field }) => (
            <TextField {...field} label="镜头标题" size="small" fullWidth />
          )}
        />
        <Controller
          name="description"
          control={control}
          render={({ field }) => (
            <TextField {...field} label="画面描述" size="small" fullWidth multiline rows={2} />
          )}
        />
        <Controller
          name="dialogue"
          control={control}
          render={({ field }) => (
            <TextField {...field} label="对白 / 旁白" size="small" fullWidth multiline rows={2} />
          )}
        />

        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5 }}>
          <Controller
            name="shotType"
            control={control}
            render={({ field }) => (
              <FormControl size="small" fullWidth>
                <InputLabel>景别</InputLabel>
                <Select {...field} label="景别">
                  {SHOT_TYPES.map((t) => (
                    <MenuItem key={t} value={t}>{t}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
          />
          <Controller
            name="cameraMovement"
            control={control}
            render={({ field }) => (
              <FormControl size="small" fullWidth>
                <InputLabel>运镜</InputLabel>
                <Select {...field} label="运镜">
                  {CAMERA_MOVEMENTS.map((m) => (
                    <MenuItem key={m} value={m}>{m}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
          />
          <Controller
            name="mood"
            control={control}
            render={({ field }) => (
              <FormControl size="small" fullWidth>
                <InputLabel>情绪基调</InputLabel>
                <Select {...field} label="情绪基调">
                  {MOODS.map((m) => (
                    <MenuItem key={m} value={m}>{m}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
          />
        </Box>

        {/* Duration slider */}
        <Controller
          name="duration"
          control={control}
          render={({ field }) => (
            <Box>
              <Typography variant="caption" color="text.secondary">
                时长: {field.value}秒
              </Typography>
              <Slider
                value={field.value}
                onChange={(_, v) => field.onChange(v)}
                min={SHOT_DURATION_MIN}
                max={SHOT_DURATION_MAX}
                step={0.5}
                size="small"
                valueLabelDisplay="auto"
                valueLabelFormat={(v) => `${v}s`}
              />
            </Box>
          )}
        />

        {/* Characters */}
        <Controller
          name="characterIds"
          control={control}
          render={({ field }) => (
            <Autocomplete
              multiple
              size="small"
              options={characters}
              getOptionLabel={(o) => o.name}
              value={characters.filter((c) => field.value.includes(c.id))}
              onChange={(_, vals) => field.onChange(vals.map((v) => v.id))}
              renderInput={(params) => <TextField {...params} label="出场角色" />}
              renderTags={(vals, getTagProps) =>
                vals.map((opt, idx) => (
                  <Chip key={opt.id} label={opt.name} size="small" {...getTagProps({ index: idx })} />
                ))
              }
            />
          )}
        />

        {/* Scene */}
        <Controller
          name="sceneId"
          control={control}
          render={({ field }) => (
            <FormControl size="small" fullWidth>
              <InputLabel>场景</InputLabel>
              <Select {...field} label="场景">
                <MenuItem value="">无</MenuItem>
                {scenes.map((s) => (
                  <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
        />

        {/* Prompt override */}
        <Controller
          name="promptOverride"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Prompt 覆写（可选）"
              size="small"
              fullWidth
              multiline
              rows={2}
              placeholder="留空则自动生成..."
            />
          )}
        />
      </Stack>
    </form>
  )
}

export default ShotParamForm
