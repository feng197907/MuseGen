import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Chip,
  Stack,
  Divider,
  IconButton,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import RefreshIcon from '@mui/icons-material/Refresh'
import type { Character, Scene } from '../../types/asset'

type Asset = Character | Scene

interface AssetDetailModalProps {
  asset: Asset | null
  type: 'character' | 'scene'
  open: boolean
  onClose: () => void
  onRegenerate?: (id: string) => void
}

const isCharacter = (asset: Asset): asset is Character =>
  (asset as Character).appearance !== undefined

const AssetDetailModal: React.FC<AssetDetailModalProps> = ({
  asset,
  type,
  open,
  onClose,
  onRegenerate,
}) => {
  if (!asset) return null

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ pr: 5, fontWeight: 700 }}>
        {type === 'character' ? '角色详情' : '场景详情'} — {asset.name}
        <IconButton
          size="small"
          onClick={onClose}
          sx={{ position: 'absolute', right: 12, top: 12 }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        {/* Image preview */}
        {asset.imageUrl && (
          <Box
            sx={{
              width: '100%',
              maxHeight: 280,
              overflow: 'hidden',
              borderRadius: 2,
              mb: 2,
              bgcolor: 'rgba(0,0,0,0.3)',
            }}
          >
            <img
              src={asset.imageUrl}
              alt={asset.name}
              style={{ width: '100%', height: 280, objectFit: 'cover' }}
            />
          </Box>
        )}

        <Stack spacing={1.5}>
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={600}>
              描述
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.25 }}>
              {asset.description || '暂无描述'}
            </Typography>
          </Box>

          {isCharacter(asset) && (
            <>
              <Box>
                <Typography variant="caption" color="text.secondary" fontWeight={600}>
                  外貌特征
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.25 }}>
                  {asset.appearance}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary" fontWeight={600}>
                  性格特点
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.25 }}>
                  {asset.personality}
                </Typography>
              </Box>
            </>
          )}

          {!isCharacter(asset) && (
            <>
              <Box>
                <Typography variant="caption" color="text.secondary" fontWeight={600}>
                  场景设定
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.25 }}>
                  {(asset as Scene).setting}
                </Typography>
              </Box>
              <Stack direction="row" spacing={1}>
                {(asset as Scene).timeOfDay && (
                  <Chip label={(asset as Scene).timeOfDay} size="small" />
                )}
                {(asset as Scene).weather && (
                  <Chip label={(asset as Scene).weather} size="small" />
                )}
              </Stack>
            </>
          )}

          <Divider />

          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={600}>
              参考 Prompt
            </Typography>
            <Typography
              variant="body2"
              sx={{
                mt: 0.5,
                p: 1,
                bgcolor: 'rgba(255,255,255,0.04)',
                borderRadius: 1,
                fontFamily: 'monospace',
                fontSize: 12,
                wordBreak: 'break-all',
              }}
            >
              {asset.referencePrompt || '待生成'}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip label={`状态: ${asset.status}`} size="small" />
          </Box>
        </Stack>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} color="inherit">
          关闭
        </Button>
        {onRegenerate && (
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={() => {
              onRegenerate(asset.id)
              onClose()
            }}
            disabled={asset.status === 'generating'}
          >
            重新生成
          </Button>
        )}
      </DialogActions>
    </Dialog>
  )
}

export default AssetDetailModal
