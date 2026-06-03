import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  CardContent,
  CardMedia,
  CardActionArea,
  CardActions,
  Typography,
  Chip,
  Box,
  IconButton,
  Tooltip,
} from '@mui/material'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import type { Project } from '../../types/project'
import { formatRelative } from '../../utils/formatTime'
import useProjectStore from '../../store/projectStore'

interface ProjectCardProps {
  project: Project
  onDelete: (id: string) => void
}

const STATUS_COLOR: Record<string, 'default' | 'warning' | 'success'> = {
  draft: 'default',
  in_progress: 'warning',
  completed: 'success',
}

const STATUS_LABEL: Record<string, string> = {
  draft: '草稿',
  in_progress: '进行中',
  completed: '已完成',
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project, onDelete }) => {
  const navigate = useNavigate()
  const setCurrentProject = useProjectStore((s) => s.setCurrentProject)

  const handleOpen = () => {
    setCurrentProject(project)
    navigate(`/project/${project.id}/storyboard`)
  }

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.15s, box-shadow 0.15s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 12px 32px rgba(139,92,246,0.2)',
        },
      }}
    >
      <CardActionArea onClick={handleOpen} sx={{ flexGrow: 1 }}>
        {project.cover_image ? (
          <CardMedia
            component="img"
            height={140}
            image={project.cover_image}
            alt={project.name}
            sx={{ objectFit: 'cover' }}
          />
        ) : (
          <Box
            sx={{
              height: 140,
              background: 'linear-gradient(135deg, rgba(139,92,246,0.3), rgba(236,72,153,0.3))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography
              sx={{
                fontSize: 40,
                fontWeight: 800,
                background: 'linear-gradient(135deg, #a78bfa, #ec4899)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              {project.name.charAt(0).toUpperCase()}
            </Typography>
          </Box>
        )}
        <CardContent>
          <Typography variant="h6" gutterBottom noWrap>
            {project.name}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1, minHeight: 40 }} noWrap>
            {project.description || '暂无描述'}
          </Typography>
          <Chip
            label={STATUS_LABEL[project.status] || project.status}
            color={STATUS_COLOR[project.status] || 'default'}
            size="small"
          />
        </CardContent>
      </CardActionArea>
      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 1 }}>
        <Typography variant="caption" color="text.secondary">
          {formatRelative(project.updated_at)}
        </Typography>
        <Tooltip title="删除项目">
          <IconButton
            size="small"
            color="error"
            onClick={(e) => {
              e.stopPropagation()
              onDelete(project.id)
            }}
          >
            <DeleteOutlineIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </CardActions>
    </Card>
  )
}

export default ProjectCard
