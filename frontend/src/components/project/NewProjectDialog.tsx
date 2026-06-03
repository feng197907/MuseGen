import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
} from '@mui/material'
import { useForm, Controller } from 'react-hook-form'
import type { ProjectCreateRequest } from '../../types/project'

interface NewProjectDialogProps {
  open: boolean
  onClose: () => void
  onSubmit: (data: ProjectCreateRequest) => void
}

const NewProjectDialog: React.FC<NewProjectDialogProps> = ({ open, onClose, onSubmit }) => {
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProjectCreateRequest>({
    defaultValues: { name: '', description: '', story_text: '' },
  })

  const handleFormSubmit = (data: ProjectCreateRequest) => {
    onSubmit(data)
    reset()
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <DialogTitle sx={{ fontWeight: 700 }}>新建项目</DialogTitle>
        <DialogContent>
          <Controller
            name="name"
            control={control}
            rules={{ required: '项目名称为必填' }}
            render={({ field }) => (
              <TextField
                {...field}
                label="项目名称"
                fullWidth
                margin="normal"
                error={!!errors.name}
                helperText={errors.name?.message}
                autoFocus
              />
            )}
          />
          <Controller
            name="description"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="项目简介"
                fullWidth
                multiline
                rows={2}
                margin="normal"
              />
            )}
          />
          <Controller
            name="story_text"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="故事文本（可选，可后续输入）"
                fullWidth
                multiline
                rows={4}
                margin="normal"
                placeholder="在此输入您的故事文本...&#10;AI 将自动解析角色、场景和分镜。"
              />
            )}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={onClose} color="inherit">
            取消
          </Button>
          <Button type="submit" variant="contained" disabled={isSubmitting}>
            创建项目
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}

export default NewProjectDialog
