import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Button,
  Chip,
  Stack,
  Alert,
  LinearProgress,
  Divider,
  CircularProgress,
} from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline'
import { useMutation } from '@tanstack/react-query'
import { useQuery } from '@tanstack/react-query'
import { exportApi } from '../api/exportApi'
import { storyboardApi } from '../api/storyboardApi'
import useStoryboardStore from '../store/storyboardStore'
import useAssetStore from '../store/assetStore'
import useSSE from '../hooks/useSSE'
import Timeline from '../components/timeline/Timeline'
import VideoTrack from '../components/timeline/VideoTrack'
import AudioMixerPanel from '../components/audio/AudioMixerPanel'
import type { AsyncTask } from '../types/task'

const ExportPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>()
  const [exportTask, setExportTask] = useState<AsyncTask | null>(null)
  const [progress, setProgress] = useState(0)
  const [progressStep, setProgressStep] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null)
  const [audioTracks, setAudioTracks] = useState<any[]>([])

  const { storyboard, setStoryboard, selectedShotId, setSelectedShot } = useStoryboardStore()

  // Fetch storyboard
  const { isLoading } = useQuery({
    queryKey: ['storyboard', projectId],
    queryFn: async () => {
      if (!projectId) return null
      const sb = await storyboardApi.getByProject(projectId)
      setStoryboard(sb)
      return sb
    },
    enabled: !!projectId,
  })

  const shots = storyboard?.shots || []
  const totalDuration = shots.reduce((sum, s) => sum + s.duration, 0)

  const isRunning = exportTask?.status === 'queued' || exportTask?.status === 'running'

  useSSE({
    taskId: exportTask?.id ?? null,
    enabled: isRunning,
    onMessage: (evt) => {
      setProgress(evt.progress)
      setProgressStep(evt.message || evt.currentStep)
      if (evt.status === 'done') {
        setExportTask((prev) => prev ? { ...prev, status: 'done' } : prev)
        setDownloadUrl(exportApi.getDownloadUrl(exportTask!.id))
      }
      if (evt.status === 'failed') {
        setExportTask((prev) => prev ? { ...prev, status: 'failed' } : prev)
        setError('视频合成失败')
      }
    },
  })

  const composeMutation = useMutation({
    mutationFn: async () => {
      if (!projectId) throw new Error('No project ID')
      return exportApi.compose(projectId)
    },
    onSuccess: (task) => {
      setExportTask(task)
      setProgress(0)
      setError(null)
      setDownloadUrl(null)
    },
    onError: (e: any) => {
      setError(e.message || '启动导出失败')
    },
  })

  const handleVolumeChange = (trackId: string, volume: number) => {
    setAudioTracks((prev) =>
      prev.map((t) => (t.id === trackId ? { ...t, volume } : t)),
    )
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '80%' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" fontWeight={700} mb={1}>
        导出 & 合成
      </Typography>
      <Typography color="text.secondary" mb={3}>
        预览时间线并导出最终视频
      </Typography>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Timeline section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="subtitle1" fontWeight={600} mb={2}>
          视频时间线
        </Typography>
        <Box sx={{ overflowX: 'auto' }}>
          <Box sx={{ minWidth: 600 }}>
            <VideoTrack
              shots={shots}
              totalDuration={totalDuration}
              onSelectShot={setSelectedShot}
              selectedShotId={selectedShotId}
            />
            <Timeline
              shots={shots}
              totalDuration={totalDuration}
              onSelectShot={setSelectedShot}
              selectedShotId={selectedShotId}
            />
          </Box>
        </Box>
      </Paper>

      {/* Audio mixer */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="subtitle1" fontWeight={600} mb={2}>
          音频混音
        </Typography>
        <AudioMixerPanel tracks={audioTracks} onVolumeChange={handleVolumeChange} />
      </Paper>

      <Divider sx={{ my: 3 }} />

      {/* Export control */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="subtitle1" fontWeight={600} mb={2}>
          导出设置
        </Typography>

        <Stack direction="row" spacing={2} flexWrap="wrap" mb={3}>
          {[
            { label: '分辨率', value: '1920×1080 (1080p)' },
            { label: '帧率', value: '24 fps' },
            { label: '格式', value: 'MP4 (H.264)' },
            { label: '镜头数', value: `${shots.length}` },
            { label: '总时长', value: `${totalDuration.toFixed(1)}s` },
          ].map((item) => (
            <Box key={item.label}>
              <Typography variant="caption" color="text.secondary" display="block">
                {item.label}
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {item.value}
              </Typography>
            </Box>
          ))}
        </Stack>

        {/* Progress */}
        {isRunning && (
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                {progressStep || 'FFmpeg 合成处理中...'}
              </Typography>
              <Typography variant="caption" fontWeight={600}>
                {Math.round(progress)}%
              </Typography>
            </Box>
            <LinearProgress variant="determinate" value={progress} sx={{ borderRadius: 2, height: 6 }} />
          </Box>
        )}

        {/* Action row */}
        <Stack direction="row" spacing={2} alignItems="center">
          <Button
            variant="contained"
            size="large"
            startIcon={
              composeMutation.isPending || isRunning ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <PlayCircleOutlineIcon />
              )
            }
            onClick={() => composeMutation.mutate()}
            disabled={shots.length === 0 || isRunning || composeMutation.isPending}
          >
            {isRunning ? '合成中...' : '开始合成视频'}
          </Button>

          {downloadUrl && (
            <Button
              variant="outlined"
              color="success"
              size="large"
              startIcon={<DownloadIcon />}
              href={downloadUrl}
              download="musegen_output.mp4"
              component="a"
            >
              下载视频
            </Button>
          )}

          {exportTask?.status === 'done' && (
            <Chip label="✓ 合成完成" color="success" />
          )}
        </Stack>

        {shots.length === 0 && (
          <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mt: 1 }}>
            请先在分镜编辑器中生成镜头内容
          </Typography>
        )}
      </Paper>
    </Box>
  )
}

export default ExportPage
