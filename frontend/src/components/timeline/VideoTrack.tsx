import React from 'react'
import { Box, Typography, Tooltip } from '@mui/material'
import type { Shot } from '../../types/project'

interface VideoTrackProps {
  shots: Shot[]
  totalDuration: number
  onSelectShot: (shotId: string) => void
  selectedShotId: string | null
}

const VideoTrack: React.FC<VideoTrackProps> = ({ shots, totalDuration, onSelectShot, selectedShotId }) => {
  const pixelsPerSecond = totalDuration > 0 ? 600 / totalDuration : 40
  let cursor = 0

  return (
    <Box sx={{ mb: 1 }}>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5, fontWeight: 600 }}>
        🎬 视频轨
      </Typography>
      <Box
        sx={{
          position: 'relative',
          height: 44,
          bgcolor: 'rgba(139,92,246,0.08)',
          border: '1px solid rgba(139,92,246,0.2)',
          borderRadius: 1,
          overflow: 'hidden',
        }}
      >
        {shots.map((shot, idx) => {
          const left = cursor
          cursor += shot.duration
          const width = Math.max(shot.duration * pixelsPerSecond, 12)

          return (
            <Tooltip key={shot.id} title={`${shot.title || `镜头${idx + 1}`} · ${shot.duration}s`} arrow>
              <Box
                onClick={() => onSelectShot(shot.id)}
                sx={{
                  position: 'absolute',
                  left,
                  width,
                  top: 4,
                  height: 'calc(100% - 8px)',
                  bgcolor: 'rgba(139,92,246,0.6)',
                  border: selectedShotId === shot.id ? '1px solid #fff' : '1px solid rgba(139,92,246,0.4)',
                  borderRadius: 0.5,
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'rgba(139,92,246,0.8)' },
                }}
              />
            </Tooltip>
          )
        })}
      </Box>
    </Box>
  )
}

export default VideoTrack
