import React from 'react'
import {
  Grid,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Typography,
  Chip,
  IconButton,
  Button,
  Box,
  Tooltip,
  CircularProgress,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'
import type { Character } from '../../types/asset'
import { assetApi } from '../../api/assetApi'
import useAssetStore from '../../store/assetStore'

interface CharacterGridProps {
  characters: Character[]
  onSelect: (char: Character) => void
}

const STATUS_COLOR: Record<string, 'default' | 'warning' | 'success' | 'error'> = {
  pending: 'default',
  generating: 'warning',
  done: 'success',
  failed: 'error',
}

const CharacterGrid: React.FC<CharacterGridProps> = ({ characters, onSelect }) => {
  const updateCharacter = useAssetStore((s) => s.updateCharacter)

  const handleRegenerate = async (charId: string) => {
    updateCharacter(charId, { status: 'generating' })
    try {
      const updated = await assetApi.regenerateCharacter(charId)
      updateCharacter(charId, updated)
    } catch {
      updateCharacter(charId, { status: 'failed' })
    }
  }

  if (characters.length === 0) {
    return (
      <Box sx={{ py: 6, textAlign: 'center' }}>
        <Typography color="text.secondary">暂无角色资产</Typography>
      </Box>
    )
  }

  return (
    <Grid container spacing={2}>
      {characters.map((char) => (
        <Grid item key={char.id} xs={12} sm={6} md={4} lg={3}>
          <Card
            sx={{
              height: '100%',
              cursor: 'pointer',
              transition: 'transform 0.15s, box-shadow 0.15s',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 24px rgba(139,92,246,0.15)',
              },
            }}
          >
            <CardMedia
              component="img"
              height={180}
              image={char.imageUrl || char.thumbnailUrl || '/placeholder-char.jpg'}
              alt={char.name}
              sx={{ objectFit: 'cover', bgcolor: 'rgba(139,92,246,0.1)' }}
            />
            <CardContent sx={{ py: 1.5, pb: 0 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="subtitle2" fontWeight={700} noWrap>
                  {char.name}
                </Typography>
                <Chip
                  label={char.status}
                  color={STATUS_COLOR[char.status] || 'default'}
                  size="small"
                  sx={{ height: 18, fontSize: 10 }}
                />
              </Box>
              <Typography variant="caption" color="text.secondary" noWrap sx={{ display: 'block', mt: 0.25 }}>
                {char.appearance}
              </Typography>
            </CardContent>
            <CardActions sx={{ px: 1.5, pb: 1 }}>
              <Tooltip title="查看详情">
                <IconButton size="small" onClick={() => onSelect(char)}>
                  <InfoOutlinedIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="重新生成">
                <span>
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => handleRegenerate(char.id)}
                    disabled={char.status === 'generating'}
                  >
                    {char.status === 'generating' ? (
                      <CircularProgress size={14} />
                    ) : (
                      <RefreshIcon fontSize="small" />
                    )}
                  </IconButton>
                </span>
              </Tooltip>
            </CardActions>
          </Card>
        </Grid>
      ))}
    </Grid>
  )
}

export default CharacterGrid
