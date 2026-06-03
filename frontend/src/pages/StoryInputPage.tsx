import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  Divider,
  CircularProgress,
  Chip,
  Stack,
  LinearProgress,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import { useMutation } from '@tanstack/react-query'
import { generateApi } from '../api/generateApi'
import { projectApi } from '../api/projectApi'
import useProjectStore from '../store/projectStore'
import useSSE from '../hooks/useSSE'
import type { AsyncTask } from '../types/task'
import TaskProgressCard from '../components/generation/TaskProgressCard'

const StoryInputPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const currentProject = useProjectStore((s) => s.currentProject)
  const updateProject = useProjectStore((s) => s.updateProject)

  const [storyText, setStoryText] = useState(currentProject?.story_text || '')
  const [activeTask, setActiveTask] = useState<AsyncTask | null>(null)
  const [sseProgress, setSseProgress] = useState(0)
  const [sseStep, setSseStep] = useState('')
  const [parseError, setParseError] = useState<string | null>(null)

  const isRunning = activeTask?.status === 'queued' || activeTask?.status === 'running'

  useSSE({
    taskId: activeTask?.id ?? null,
    enabled: isRunning,
    onMessage: (evt) => {
      setSseProgress(evt.progress)
      setSseStep(evt.message || evt.current_step)
      if (evt.status === 'done') {
        setActiveTask((prev) => prev ? { ...prev, status: 'done' } : prev)
        // Refresh project info
        if (projectId) {
          projectApi.get(projectId).then((p) => updateProject(p.id, p)).catch(() => {})
        }
      }
      if (evt.status === 'failed') {
        setActiveTask((prev) => prev ? { ...prev, status: 'failed' } : prev)
        setParseError('故事解析失败，请重试')
      }
    },
  })

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!projectId) throw new Error('No project ID')
      await projectApi.update(projectId, { story_text: storyText })
      updateProject(projectId, { story_text: storyText })
    },
  })

  const parseMutation = useMutation({
    mutationFn: async () => {
      if (!projectId) throw new Error('No project ID')
      // Save first
      await projectApi.update(projectId, { story_text: storyText })
      updateProject(projectId, { story_text: storyText })
      // Then trigger parse
      return generateApi.parseStory({ project_id: projectId, story_text: storyText })
    },
    onSuccess: (task) => {
      setActiveTask(task)
      setParseError(null)
      setSseProgress(0)
    },
    onError: (e: any) => {
      const msg = e?.response?.data?.detail
        ? (Array.isArray(e.response.data.detail)
            ? e.response.data.detail.map((d: any) => d.msg || JSON.stringify(d)).join('; ')
            : e.response.data.detail)
        : (e?.message || '启动解析失败')
      setParseError(msg)
    },
  })

  return (
    <Box sx={{ p: 4, maxWidth: 960, mx: 'auto' }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          故事输入
        </Typography>
        <Typography color="text.secondary">
          输入您的故事文本，AI 将自动解析角色、场景和分镜结构
        </Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="subtitle1" fontWeight={600} mb={1.5}>
          故事文本
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={14}
          placeholder="在此输入故事文本...&#10;&#10;例如：&#10;故事发生在一个奇幻的魔法学校...&#10;主角小明是一个充满好奇心的少年..."
          value={storyText}
          onChange={(e) => setStoryText(e.target.value)}
          sx={{ mb: 2 }}
          disabled={isRunning}
        />
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Chip
            label={`${storyText.length} 字符`}
            size="small"
            color={storyText.length > 100 ? 'primary' : 'default'}
          />
          <Stack direction="row" spacing={1.5}>
            <Button
              variant="outlined"
              onClick={() => saveMutation.mutate()}
              disabled={isRunning || saveMutation.isPending}
            >
              保存
            </Button>
            <Button
              variant="contained"
              startIcon={
                parseMutation.isPending || isRunning ? (
                  <CircularProgress size={16} color="inherit" />
                ) : (
                  <AutoAwesomeIcon />
                )
              }
              onClick={() => parseMutation.mutate()}
              disabled={!storyText.trim() || isRunning || parseMutation.isPending}
            >
              AI 解析故事
            </Button>
          </Stack>
        </Box>
      </Paper>

      {/* Error */}
      {parseError && (
        <Alert severity="error" onClose={() => setParseError(null)} sx={{ mb: 2 }}>
          {parseError}
        </Alert>
      )}

      {/* Task progress */}
      {activeTask && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="subtitle1" fontWeight={600} mb={2}>
            解析进度
          </Typography>
          {isRunning && (
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">{sseStep || '分析故事结构...'}</Typography>
                <Typography variant="caption" fontWeight={600}>{Math.round(sseProgress)}%</Typography>
              </Box>
              <LinearProgress variant="determinate" value={sseProgress} sx={{ borderRadius: 2, height: 6 }} />
            </Box>
          )}
          <TaskProgressCard task={activeTask} />
        </Paper>
      )}

      {/* Navigation tips */}
      <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="body2" color="text.secondary">
          解析完成后，您可以在分镜编辑器中查看和调整结果
        </Typography>
        <Button
          variant="outlined"
          endIcon={<ArrowForwardIcon />}
          onClick={() => navigate(`/project/${projectId}/storyboard`)}
        >
          前往分镜编辑器
        </Button>
      </Paper>

      <Divider sx={{ my: 3 }} />

      {/* Tips */}
      <Box>
        <Typography variant="subtitle2" fontWeight={600} mb={1} color="text.secondary">
          故事写作建议
        </Typography>
        {[
          '描述角色的外貌特征（如：黑色长发、蓝色眼睛的少年）',
          '说明场景的时间、地点和氛围（如：夜晚的魔法森林）',
          '包含人物的对话和动作（如：小明说"我不相信"，转身离去）',
          '文字建议在 200-3000 字之间以获得最佳分镜效果',
        ].map((tip, i) => (
          <Typography key={i} variant="body2" color="text.secondary" sx={{ mb: 0.5, pl: 1 }}>
            · {tip}
          </Typography>
        ))}
      </Box>
    </Box>
  )
}

export default StoryInputPage
