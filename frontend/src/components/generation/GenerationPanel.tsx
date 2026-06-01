import React, { useState } from 'react'
import {
  Paper,
  Typography,
  Button,
  Stack,
  LinearProgress,
  Chip,
  Box,
  Divider,
  Alert,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import StopIcon from '@mui/icons-material/Stop'
import type { AsyncTask } from '../../types/task'
import { TASK_PHASES } from '../../utils/constants'
import { generateApi } from '../../api/generateApi'
import useSSE from '../../hooks/useSSE'
import useProjectStore from '../../store/projectStore'

const GenerationPanel: React.FC = () => {
  const currentProject = useProjectStore((s) => s.currentProject)
  const [activeTask, setActiveTask] = useState<AsyncTask | null>(null)
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('')
  const [phaseIdx, setPhaseIdx] = useState(-1)
  const [error, setError] = useState<string | null>(null)
  const [isLaunching, setIsLaunching] = useState(false)

  const isRunning = activeTask?.status === 'queued' || activeTask?.status === 'running'

  useSSE({
    taskId: activeTask?.id ?? null,
    enabled: isRunning,
    onMessage: (evt) => {
      setProgress(evt.progress)
      setCurrentStep(evt.message || evt.currentStep)
      // Map task type to phase index
      const idx = TASK_PHASES.findIndex((p) => p.key === evt.taskType)
      if (idx !== -1) setPhaseIdx(idx)

      if (evt.status === 'done') {
        setActiveTask((prev) => prev ? { ...prev, status: 'done' } : prev)
      }
      if (evt.status === 'failed') {
        setActiveTask((prev) => prev ? { ...prev, status: 'failed' } : prev)
        setError('生成过程中出现错误，请重试')
      }
    },
  })

  const handleStart = async () => {
    if (!currentProject) return
    setError(null)
    setIsLaunching(true)
    try {
      const task = await generateApi.fullPipeline({
        projectId: currentProject.id,
        storyText: currentProject.storyText,
      })
      setActiveTask(task)
      setProgress(0)
      setPhaseIdx(0)
    } catch (e: any) {
      setError(e.message || '启动失败，请检查配置')
    } finally {
      setIsLaunching(false)
    }
  }

  return (
    <Paper
      sx={{
        p: 3,
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Typography variant="h6" fontWeight={700} mb={2}>
        生成控制台
      </Typography>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Phase stepper */}
      <Stepper activeStep={phaseIdx} alternativeLabel sx={{ mb: 3 }}>
        {TASK_PHASES.map((phase) => (
          <Step key={phase.key}>
            <StepLabel
              sx={{
                '& .MuiStepLabel-label': { fontSize: 11 },
              }}
            >
              {phase.label}
            </StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Progress */}
      {isRunning && (
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              {currentStep || '处理中...'}
            </Typography>
            <Typography variant="caption" fontWeight={600}>
              {Math.round(progress)}%
            </Typography>
          </Box>
          <LinearProgress variant="determinate" value={progress} sx={{ borderRadius: 2, height: 6 }} />
        </Box>
      )}

      {/* Status chip */}
      {activeTask && !isRunning && (
        <Box sx={{ mb: 2 }}>
          <Chip
            label={
              activeTask.status === 'done'
                ? '✓ 生成完成'
                : activeTask.status === 'failed'
                ? '✗ 生成失败'
                : activeTask.status
            }
            color={activeTask.status === 'done' ? 'success' : activeTask.status === 'failed' ? 'error' : 'default'}
          />
        </Box>
      )}

      <Divider sx={{ my: 2 }} />

      <Stack direction="row" spacing={2}>
        <Button
          variant="contained"
          startIcon={<PlayArrowIcon />}
          onClick={handleStart}
          disabled={isRunning || isLaunching || !currentProject}
          sx={{ minWidth: 140 }}
        >
          {isLaunching ? '启动中...' : isRunning ? '生成中...' : '一键全流程生成'}
        </Button>
        {isRunning && (
          <Button variant="outlined" color="error" startIcon={<StopIcon />} disabled>
            停止
          </Button>
        )}
      </Stack>

      {!currentProject && (
        <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mt: 1 }}>
          请先选择一个项目
        </Typography>
      )}
    </Paper>
  )
}

export default GenerationPanel
