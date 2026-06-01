import React, { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Slider,
  Stack,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material'
import VolumeUpIcon from '@mui/icons-material/VolumeUp'
import VolumeOffIcon from '@mui/icons-material/VolumeOff'
import type { AudioTrack } from '../../types/audio'

interface AudioMixerPanelProps {
  tracks: AudioTrack[]
  onVolumeChange: (trackId: string, volume: number) => void
}

const TRACK_TYPE_COLOR: Record<string, string> = {
  voice: '#ec4899',
  bgm: '#06b6d4',
  sfx: '#f59e0b',
}

const TRACK_TYPE_LABEL: Record<string, string> = {
  voice: '配音',
  bgm: 'BGM',
  sfx: '音效',
}

const AudioMixerPanel: React.FC<AudioMixerPanelProps> = ({ tracks, onVolumeChange }) => {
  const [masterVolume, setMasterVolume] = useState(1.0)

  if (tracks.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary" variant="body2">
          暂无音频轨道
        </Typography>
      </Paper>
    )
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="subtitle2" fontWeight={700} mb={2}>
        混音控制台
      </Typography>

      {/* Master volume */}
      <Box sx={{ mb: 2, p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 1 }}>
        <Typography variant="caption" color="text.secondary" fontWeight={600}>
          主音量
        </Typography>
        <Stack direction="row" spacing={1} alignItems="center">
          <VolumeUpIcon fontSize="small" sx={{ color: 'primary.main' }} />
          <Slider
            value={masterVolume * 100}
            onChange={(_, v) => setMasterVolume((v as number) / 100)}
            min={0}
            max={100}
            size="small"
            sx={{ flex: 1 }}
          />
          <Typography variant="caption" sx={{ minWidth: 32 }}>
            {Math.round(masterVolume * 100)}%
          </Typography>
        </Stack>
      </Box>

      {/* Individual tracks */}
      <Stack spacing={1.5}>
        {tracks.map((track) => (
          <Box key={track.id} sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.75, gap: 1 }}>
              <Chip
                label={TRACK_TYPE_LABEL[track.type] || track.type}
                size="small"
                sx={{
                  height: 18,
                  fontSize: 10,
                  bgcolor: TRACK_TYPE_COLOR[track.type],
                  color: '#fff',
                }}
              />
              <Typography variant="caption" noWrap sx={{ flex: 1 }}>
                {track.name}
              </Typography>
              <Tooltip title={track.volume === 0 ? '取消静音' : '静音'}>
                <IconButton
                  size="small"
                  onClick={() => onVolumeChange(track.id, track.volume === 0 ? 0.8 : 0)}
                >
                  {track.volume === 0 ? (
                    <VolumeOffIcon fontSize="small" />
                  ) : (
                    <VolumeUpIcon fontSize="small" />
                  )}
                </IconButton>
              </Tooltip>
            </Box>
            <Stack direction="row" spacing={1} alignItems="center">
              <Slider
                value={track.volume * 100}
                onChange={(_, v) => onVolumeChange(track.id, (v as number) / 100)}
                min={0}
                max={100}
                size="small"
                sx={{ flex: 1, color: TRACK_TYPE_COLOR[track.type] || 'primary.main' }}
              />
              <Typography variant="caption" sx={{ minWidth: 32 }}>
                {Math.round(track.volume * 100)}%
              </Typography>
            </Stack>
          </Box>
        ))}
      </Stack>
    </Paper>
  )
}

export default AudioMixerPanel
