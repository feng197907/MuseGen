import React from 'react'
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Stack,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import ShotParamForm from './ShotParamForm'
import type { Shot } from '../../types/project'
import type { Character, Scene } from '../../types/asset'

interface ShotDetailPanelProps {
  shot: Shot | null
  characters: Character[]
  scenes: Scene[]
  onClose: () => void
  onUpdate: (shotId: string, updates: Partial<Shot>) => void
}

const ShotDetailPanel: React.FC<ShotDetailPanelProps> = ({ shot, characters, scenes, onClose, onUpdate }) => {
  if (!shot) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography color="text.secondary">选择一个分镜查看详情</Typography>
      </Paper>
    )
  }

  const handleUpdate = (updates: Partial<Shot>) => {
    onUpdate(shot.id, updates)
  }

  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 2,
          py: 1.5,
          borderBottom: '1px solid',
          borderColor: 'divider',
          flexShrink: 0,
        }}
      >
        <Stack direction="row" alignItems="center" spacing={1}>
          <Typography variant="subtitle1" fontWeight={600}>
            #{shot.order + 1} 分镜详情
          </Typography>
        </Stack>
        <IconButton size="small" onClick={onClose}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {/* Keyframe preview */}
        {shot.keyframe_id ? (
          <Box
            sx={{
              width: '100%',
              aspectRatio: '16/9',
              borderRadius: 2,
              overflow: 'hidden',
              mb: 2,
              bgcolor: 'rgba(0,0,0,0.3)',
            }}
          >
            <img
              src={`/api/v1/assets/keyframes/${shot.keyframe_id}/image`}
              alt={`Shot ${shot.order + 1}`}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none'
              }}
            />
          </Box>
        ) : (
          <Box
            sx={{
              width: '100%',
              aspectRatio: '16/9',
              borderRadius: 2,
              mb: 2,
              bgcolor: 'rgba(139,92,246,0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px dashed',
              borderColor: 'divider',
            }}
          >
            <Typography variant="caption" color="text.disabled">
              尚未生成关键帧
            </Typography>
          </Box>
        )}

        {/* Shot parameter form */}
        <ShotParamForm
          shot={shot}
          characters={characters}
          scenes={scenes}
          onUpdate={handleUpdate}
        />
      </Box>
    </Paper>
  )
}

export default ShotDetailPanel
