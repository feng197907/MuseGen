import React, { useEffect, useRef } from 'react'
import { Box, Typography, Chip, IconButton, Slider, Tooltip } from '@mui/material'
import VolumeUpIcon from '@mui/icons-material/VolumeUp'
import VolumeOffIcon from '@mui/icons-material/VolumeOff'
import type { AudioTrack as AudioTrackType } from '../../types/audio'

interface AudioTrackProps {
  track: AudioTrackType
  totalDuration: number
  onVolumeChange: (trackId: string, volume: number) => void
}

const TRACK_TYPE_COLOR: Record<string, string> = {
  voice: 'rgba(236,72,153,0.5)',
  bgm: 'rgba(6,182,212,0.5)',
  sfx: 'rgba(245,158,11,0.5)',
}

const TRACK_TYPE_LABEL: Record<string, string> = {
  voice: '配音',
  bgm: 'BGM',
  sfx: '音效',
}

const AudioTrack: React.FC<AudioTrackProps> = ({ track, totalDuration, onVolumeChange }) => {
  const pixelsPerSecond = totalDuration > 0 ? 600 / totalDuration : 40

  const clipLeft = track.startTime * pixelsPerSecond
  const clipWidth = Math.max(track.duration * pixelsPerSecond, 20)

  const isMuted = track.volume === 0

  return (
    <Box sx={{ mb: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
        <Chip
          label={TRACK_TYPE_LABEL[track.type] || track.type}
          size="small"
          sx={{ height: 18, fontSize: 10 }}
        />
        <Typography variant="caption" color="text.secondary" noWrap sx={{ flex: 1 }}>
          {track.name}
        </Typography>
        <Tooltip title={isMuted ? '取消静音' : '静音'}>
          <IconButton
            size="small"
            onClick={() => onVolumeChange(track.id, isMuted ? 0.8 : 0)}
          >
            {isMuted ? <VolumeOffIcon fontSize="small" /> : <VolumeUpIcon fontSize="small" />}
          </IconButton>
        </Tooltip>
        <Slider
          size="small"
          value={track.volume * 100}
          onChange={(_, v) => onVolumeChange(track.id, (v as number) / 100)}
          min={0}
          max={100}
          sx={{ width: 80 }}
        />
      </Box>
      <Box
        sx={{
          position: 'relative',
          height: 32,
          bgcolor: 'rgba(255,255,255,0.03)',
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 1,
          overflow: 'hidden',
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            left: clipLeft,
            width: clipWidth,
            height: 'calc(100% - 6px)',
            top: 3,
            bgcolor: TRACK_TYPE_COLOR[track.type] || 'rgba(139,92,246,0.4)',
            borderRadius: 0.5,
            cursor: 'pointer',
            '&:hover': { filter: 'brightness(1.3)' },
          }}
        />
      </Box>
    </Box>
  )
}

export default AudioTrack
