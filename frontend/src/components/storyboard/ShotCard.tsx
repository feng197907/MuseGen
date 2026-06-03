import React from 'react'
import { Box, Typography, Chip, IconButton, Paper, Tooltip } from '@mui/material'
import DragIndicatorIcon from '@mui/icons-material/DragIndicator'
import EditIcon from '@mui/icons-material/Edit'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import type { Shot } from '../../types/project'

interface ShotCardProps {
  shot: Shot
  selected: boolean
  onSelect: () => void
}

const STATUS_COLOR: Record<string, string> = {
  pending: '#64748b',
  generating: '#f59e0b',
  done: '#10b981',
  failed: '#ef4444',
}

const ShotCard: React.FC<ShotCardProps> = ({ shot, selected, onSelect }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: shot.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <Paper
      ref={setNodeRef}
      style={style}
      onClick={onSelect}
      sx={{
        p: 1.5,
        mb: 1,
        cursor: 'pointer',
        border: '1px solid',
        borderColor: selected ? 'primary.main' : 'divider',
        borderRadius: 2,
        bgcolor: selected ? 'rgba(139,92,246,0.1)' : 'background.paper',
        position: 'relative',
        transition: 'border-color 0.15s, background-color 0.15s',
        '&:hover': {
          borderColor: 'primary.light',
          bgcolor: 'rgba(139,92,246,0.05)',
        },
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
        {/* Drag handle */}
        <IconButton
          size="small"
          {...attributes}
          {...listeners}
          sx={{ cursor: 'grab', p: 0.25, color: 'text.disabled', flexShrink: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          <DragIndicatorIcon fontSize="small" />
        </IconButton>

        {/* Shot thumbnail or placeholder */}
        <Box
          sx={{
            width: 56,
            height: 40,
            borderRadius: 1,
            overflow: 'hidden',
            flexShrink: 0,
            bgcolor: 'rgba(255,255,255,0.05)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {shot.keyframe_id ? (
            <img
              src={`/api/v1/assets/keyframes/${shot.keyframe_id}/thumbnail`}
              alt="keyframe"
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              onError={(e) => ((e.target as HTMLImageElement).style.display = 'none')}
            />
          ) : (
            <AutoFixHighIcon sx={{ fontSize: 18, color: 'text.disabled' }} />
          )}
        </Box>

        {/* Shot info */}
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.25 }}>
            <Typography
              variant="caption"
              sx={{ fontWeight: 600, color: 'text.secondary', mr: 0.5 }}
            >
              #{shot.order + 1}
            </Typography>
            <Typography variant="body2" noWrap sx={{ fontWeight: 500 }}>
              {shot.title || `镜头 ${shot.order + 1}`}
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary" noWrap sx={{ display: 'block' }}>
            {shot.description || '暂无描述'}
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5, flexWrap: 'wrap' }}>
            <Chip label={shot.shot_type || '中景'} size="small" sx={{ height: 18, fontSize: 10 }} />
            <Chip label={`${shot.duration}s`} size="small" sx={{ height: 18, fontSize: 10 }} />
          </Box>
        </Box>

        {/* Status indicator */}
        <Box sx={{ flexShrink: 0, display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Tooltip title={shot.status}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: STATUS_COLOR[shot.status] || '#64748b',
              }}
            />
          </Tooltip>
          <IconButton size="small" color="primary" onClick={(e) => { e.stopPropagation(); onSelect() }}>
            <EditIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>
    </Paper>
  )
}

export default ShotCard
