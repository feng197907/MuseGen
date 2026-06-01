import React, { useMemo } from 'react'
import { Box, Typography, Tooltip } from '@mui/material'
import type { Shot } from '../../types/project'
import { formatSeconds } from '../../utils/formatTime'

interface TimelineClip {
  shotId: string
  startTime: number
  duration: number
  label: string
  color: string
  order: number
}

interface TimelineProps {
  shots: Shot[]
  totalDuration: number
  onSelectShot: (shotId: string) => void
  selectedShotId: string | null
}

const SHOT_COLORS = [
  '#8b5cf6', '#ec4899', '#06b6d4', '#f59e0b', '#10b981',
  '#ef4444', '#6366f1', '#14b8a6', '#f97316', '#8b5cf6',
]

const Timeline: React.FC<TimelineProps> = ({ shots, totalDuration, onSelectShot, selectedShotId }) => {
  const clips: TimelineClip[] = useMemo(() => {
    let cursor = 0
    return shots.map((shot, idx) => {
      const clip: TimelineClip = {
        shotId: shot.id,
        startTime: cursor,
        duration: shot.duration,
        label: `${shot.title || `镜头 ${idx + 1}`}`,
        color: SHOT_COLORS[idx % SHOT_COLORS.length],
        order: idx,
      }
      cursor += shot.duration
      return clip
    })
  }, [shots])

  const pixelsPerSecond = totalDuration > 0 ? 600 / totalDuration : 50

  if (shots.length === 0) {
    return (
      <Box sx={{ py: 4, textAlign: 'center' }}>
        <Typography color="text.secondary" variant="body2">
          暂无时间线数据
        </Typography>
      </Box>
    )
  }

  return (
    <Box>
      {/* Time ruler */}
      <Box sx={{ position: 'relative', height: 24, mb: 1 }}>
        {Array.from({ length: Math.ceil(totalDuration) + 1 }, (_, i) => (
          <Typography
            key={i}
            variant="caption"
            sx={{
              position: 'absolute',
              left: i * pixelsPerSecond,
              top: 0,
              color: 'text.disabled',
              fontSize: 10,
              transform: 'translateX(-50%)',
            }}
          >
            {formatSeconds(i)}
          </Typography>
        ))}
      </Box>

      {/* Tracks */}
      <Box
        sx={{
          position: 'relative',
          height: 52,
          bgcolor: 'rgba(30,30,50,0.8)',
          borderRadius: 1,
          overflow: 'hidden',
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        {clips.map((clip) => (
          <Tooltip key={clip.shotId} title={`${clip.label} (${clip.duration}s)`} arrow>
            <Box
              onClick={() => onSelectShot(clip.shotId)}
              sx={{
                position: 'absolute',
                left: clip.startTime * pixelsPerSecond,
                width: Math.max(clip.duration * pixelsPerSecond, 16),
                height: 'calc(100% - 8px)',
                top: 4,
                bgcolor: clip.color,
                borderRadius: 1,
                display: 'flex',
                alignItems: 'center',
                px: 1,
                cursor: 'pointer',
                opacity: selectedShotId && selectedShotId !== clip.shotId ? 0.5 : 1,
                border: selectedShotId === clip.shotId ? '2px solid #fff' : 'none',
                transition: 'opacity 0.15s, filter 0.15s',
                overflow: 'hidden',
                '&:hover': {
                  filter: 'brightness(1.2)',
                },
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  fontWeight: 600,
                  fontSize: 10,
                  color: '#fff',
                  textShadow: '0 1px 2px rgba(0,0,0,0.5)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {clip.label}
              </Typography>
            </Box>
          </Tooltip>
        ))}
      </Box>

      {/* Summary */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 0.5 }}>
        <Typography variant="caption" color="text.disabled">
          {shots.length} 个镜头 · 总时长 {totalDuration.toFixed(1)}s
        </Typography>
      </Box>
    </Box>
  )
}

export default Timeline
