import React from 'react'
import {
  Grid,
  Card,
  CardMedia,
  CardContent,
  Typography,
  Chip,
  Box,
  CardActionArea,
  Stack,
} from '@mui/material'
import type { Scene } from '../../types/asset'

interface SceneGridProps {
  scenes: Scene[]
  onSelect: (scene: Scene) => void
}

const STATUS_COLOR: Record<string, 'default' | 'warning' | 'success' | 'error'> = {
  pending: 'default',
  generating: 'warning',
  done: 'success',
  failed: 'error',
}

const SceneGrid: React.FC<SceneGridProps> = ({ scenes, onSelect }) => {
  if (scenes.length === 0) {
    return (
      <Box sx={{ py: 6, textAlign: 'center' }}>
        <Typography color="text.secondary">暂无场景资产</Typography>
      </Box>
    )
  }

  return (
    <Grid container spacing={2}>
      {scenes.map((scene) => (
        <Grid item key={scene.id} xs={12} sm={6} md={4} lg={3}>
          <Card
            sx={{
              height: '100%',
              transition: 'transform 0.15s, box-shadow 0.15s',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 24px rgba(139,92,246,0.15)',
              },
            }}
          >
            <CardActionArea onClick={() => onSelect(scene)}>
              <CardMedia
                component="img"
                height={140}
                image={scene.imageUrl || scene.thumbnailUrl || '/placeholder-scene.jpg'}
                alt={scene.name}
                sx={{ objectFit: 'cover', bgcolor: 'rgba(139,92,246,0.05)' }}
              />
              <CardContent sx={{ py: 1.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="subtitle2" fontWeight={700} noWrap>
                    {scene.name}
                  </Typography>
                  <Chip
                    label={scene.status}
                    color={STATUS_COLOR[scene.status] || 'default'}
                    size="small"
                    sx={{ height: 18, fontSize: 10 }}
                  />
                </Box>
                <Typography variant="caption" color="text.secondary" noWrap sx={{ display: 'block' }}>
                  {scene.setting}
                </Typography>
                <Stack direction="row" spacing={0.5} sx={{ mt: 0.75, flexWrap: 'wrap' }}>
                  {scene.timeOfDay && (
                    <Chip label={scene.timeOfDay} size="small" sx={{ height: 18, fontSize: 10 }} />
                  )}
                  {scene.weather && (
                    <Chip label={scene.weather} size="small" sx={{ height: 18, fontSize: 10 }} />
                  )}
                </Stack>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
      ))}
    </Grid>
  )
}

export default SceneGrid
