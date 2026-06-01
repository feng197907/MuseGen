import React, { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Stack,
} from '@mui/material'
import UndoIcon from '@mui/icons-material/Undo'
import RedoIcon from '@mui/icons-material/Redo'
import { useQuery } from '@tanstack/react-query'
import { storyboardApi } from '../api/storyboardApi'
import { assetApi } from '../api/assetApi'
import useStoryboardStore from '../store/storyboardStore'
import useAssetStore from '../store/assetStore'
import useProjectStore from '../store/projectStore'
import useUndoRedo from '../hooks/useUndoRedo'
import ShotList from '../components/storyboard/ShotList'
import ShotDetailPanel from '../components/storyboard/ShotDetailPanel'
import GenerationPanel from '../components/generation/GenerationPanel'
import type { Shot } from '../types/project'

const StoryboardEditorPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>()
  const {
    storyboard,
    selectedShotId,
    setStoryboard,
    setSelectedShot,
    updateShot,
    reorderShots,
    setLoading: setSLoading,
  } = useStoryboardStore()
  const {
    characters,
    scenes,
    setCharacters,
    setScenes,
  } = useAssetStore()
  const { canUndo, canRedo, handleUndo, handleRedo } = useUndoRedo()
  const currentProject = useProjectStore((s) => s.currentProject)
  const updateProject = useProjectStore((s) => s.updateProject)

  // Fetch storyboard
  const { isLoading: sbLoading, error: sbError } = useQuery({
    queryKey: ['storyboard', projectId],
    queryFn: async () => {
      if (!projectId) return null
      const sb = await storyboardApi.getByProject(projectId)
      setStoryboard(sb)
      return sb
    },
    enabled: !!projectId,
  })

  // Fetch assets for this project
  useQuery({
    queryKey: ['assets', projectId],
    queryFn: async () => {
      if (!projectId) return null
      const [chars, scns] = await Promise.all([
        assetApi.listCharacters(projectId),
        assetApi.listScenes(projectId),
      ])
      setCharacters(chars)
      setScenes(scns)
      return { chars, scns }
    },
    enabled: !!projectId,
  })

  useEffect(() => {
    setSLoading(sbLoading)
  }, [sbLoading, setSLoading])

  // Refresh project on mount
  useEffect(() => {
    if (!projectId) return
    const fetchProject = async () => {
      try {
        const { projectApi } = await import('../api/projectApi')
        const p = await projectApi.get(projectId)
        updateProject(p.id, p)
      } catch { /* ignore */ }
    }
    fetchProject()
  }, [projectId])

  const selectedShot = storyboard?.shots.find((s) => s.id === selectedShotId) ?? null

  const handleReorder = async (orderedIds: string[]) => {
    reorderShots(orderedIds)
    try {
      await storyboardApi.reorderShots({ shotIds: orderedIds })
    } catch {
      // revert on failure: refetch
    }
  }

  const handleShotUpdate = async (shotId: string, updates: Partial<Shot>) => {
    updateShot(shotId, updates)
    try {
      await storyboardApi.updateShot(shotId, updates)
    } catch {
      // silently fail, local state remains updated
    }
  }

  if (sbLoading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '80%' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (sbError) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">加载分镜数据失败</Alert>
      </Box>
    )
  }

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: '280px 1fr 340px',
        gridTemplateRows: '1fr 200px',
        height: 'calc(100vh - 52px)',
        gap: 0,
        overflow: 'hidden',
      }}
    >
      {/* Left: Shot list */}
      <Box
        sx={{
          borderRight: '1px solid',
          borderColor: 'divider',
          overflow: 'auto',
          p: 1.5,
          gridRow: '1 / 3',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* Toolbar */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5, flexShrink: 0 }}>
          <Typography variant="subtitle2" fontWeight={700}>
            分镜列表 ({storyboard?.shots.length || 0})
          </Typography>
          <Stack direction="row">
            <Tooltip title="撤销 (Ctrl+Z)">
              <span>
                <IconButton size="small" onClick={handleUndo} disabled={!canUndo}>
                  <UndoIcon fontSize="small" />
                </IconButton>
              </span>
            </Tooltip>
            <Tooltip title="重做 (Ctrl+Shift+Z)">
              <span>
                <IconButton size="small" onClick={handleRedo} disabled={!canRedo}>
                  <RedoIcon fontSize="small" />
                </IconButton>
              </span>
            </Tooltip>
          </Stack>
        </Box>

        <Box sx={{ flex: 1, overflow: 'auto' }}>
          <ShotList
            shots={storyboard?.shots || []}
            selectedShotId={selectedShotId}
            onSelectShot={setSelectedShot}
            onReorder={handleReorder}
          />
        </Box>
      </Box>

      {/* Center: Preview area */}
      <Box
        sx={{
          overflow: 'auto',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'rgba(0,0,0,0.2)',
        }}
      >
        {selectedShot && selectedShot.keyframeId ? (
          <Box
            sx={{
              width: '100%',
              maxWidth: 720,
              aspectRatio: '16/9',
              borderRadius: 3,
              overflow: 'hidden',
              boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
              border: '1px solid',
              borderColor: 'divider',
            }}
          >
            <img
              src={`/api/v1/assets/keyframes/${selectedShot.keyframeId}/image`}
              alt={`Shot ${selectedShot.order + 1}`}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          </Box>
        ) : (
          <Box sx={{ textAlign: 'center', maxWidth: 400 }}>
            <Typography variant="h6" color="text.disabled" gutterBottom>
              {storyboard?.shots.length ? '选择一个分镜查看预览' : '暂无分镜数据'}
            </Typography>
            <Typography variant="body2" color="text.disabled">
              {!storyboard?.shots.length && '请先在故事输入页导入故事文本进行 AI 解析'}
            </Typography>
          </Box>
        )}

        {/* Dialogue overlay on preview */}
        {selectedShot?.dialogue && (
          <Box
            sx={{
              mt: 2,
              p: 1.5,
              bgcolor: 'rgba(0,0,0,0.7)',
              borderRadius: 2,
              maxWidth: 720,
              width: '100%',
            }}
          >
            <Typography variant="caption" color="text.disabled" display="block" mb={0.25}>
              对白/旁白
            </Typography>
            <Typography variant="body2">{selectedShot.dialogue}</Typography>
          </Box>
        )}
      </Box>

      {/* Right: Shot detail panel */}
      <Box
        sx={{
          borderLeft: '1px solid',
          borderColor: 'divider',
          overflow: 'auto',
          gridRow: '1 / 2',
        }}
      >
        <ShotDetailPanel
          shot={selectedShot}
          characters={characters}
          scenes={scenes}
          onClose={() => setSelectedShot(null)}
          onUpdate={handleShotUpdate}
        />
      </Box>

      {/* Bottom right: Generation panel */}
      <Box
        sx={{
          borderLeft: '1px solid',
          borderTop: '1px solid',
          borderColor: 'divider',
          overflow: 'auto',
          p: 2,
          gridRow: '2 / 3',
          gridColumn: '3 / 4',
        }}
      >
        <GenerationPanel />
      </Box>
    </Box>
  )
}

export default StoryboardEditorPage
