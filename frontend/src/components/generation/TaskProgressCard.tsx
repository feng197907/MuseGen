import React from 'react'
import {
  Paper,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Stack,
  Tooltip,
} from '@mui/material'
import type { AsyncTask } from '../../types/task'
import { formatRelative } from '../../utils/formatTime'

interface TaskProgressCardProps {
  task: AsyncTask
}

const STATUS_COLOR: Record<string, 'default' | 'warning' | 'success' | 'error'> = {
  queued: 'default',
  running: 'warning',
  done: 'success',
  failed: 'error',
}

const TASK_TYPE_LABEL: Record<string, string> = {
  parse_story: '故事解析',
  generate_assets: '资产生成',
  generate_keyframes: '关键帧生成',
  generate_animation: '动画生成',
  generate_audio: '配音生成',
  compose_video: '视频合成',
  full_pipeline: '全流程',
}

const TaskProgressCard: React.FC<TaskProgressCardProps> = ({ task }) => {
  return (
    <Paper
      sx={{
        p: 2,
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 2,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" fontWeight={600}>
          {TASK_TYPE_LABEL[task.taskType] || task.taskType}
        </Typography>
        <Stack direction="row" spacing={0.5} alignItems="center">
          <Chip
            label={task.status}
            color={STATUS_COLOR[task.status] || 'default'}
            size="small"
            sx={{ height: 20, fontSize: 11 }}
          />
          <Typography variant="caption" color="text.secondary">
            {formatRelative(task.createdAt)}
          </Typography>
        </Stack>
      </Box>

      {/* Progress */}
      {(task.status === 'running' || task.status === 'queued') && (
        <Box sx={{ mb: 1 }}>
          <LinearProgress
            variant={task.status === 'queued' ? 'indeterminate' : 'determinate'}
            value={task.progress}
            sx={{ borderRadius: 2, height: 5 }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.25, display: 'block' }}>
            {task.currentStep || (task.status === 'queued' ? '等待执行...' : '处理中...')}
          </Typography>
        </Box>
      )}

      {/* Error */}
      {task.status === 'failed' && task.errorMessage && (
        <Tooltip title={task.errorMessage}>
          <Typography
            variant="caption"
            color="error"
            noWrap
            sx={{ display: 'block', mt: 0.5, cursor: 'help' }}
          >
            错误: {task.errorMessage}
          </Typography>
        </Tooltip>
      )}

      {/* Success summary */}
      {task.status === 'done' && (
        <Typography variant="caption" color="success.main" sx={{ display: 'block', mt: 0.5 }}>
          ✓ 完成 — {task.currentStep || '任务成功'}
        </Typography>
      )}

      {/* Task ID */}
      <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mt: 0.5 }}>
        ID: {task.id.slice(0, 8)}...
      </Typography>
    </Paper>
  )
}

export default TaskProgressCard
