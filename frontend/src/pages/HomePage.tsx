import React, { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  CircularProgress,
  Alert,
  InputAdornment,
  TextField,
  Stack,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import SearchIcon from '@mui/icons-material/Search'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import ProjectCard from '../components/project/ProjectCard'
import NewProjectDialog from '../components/project/NewProjectDialog'
import { projectApi } from '../api/projectApi'
import type { ProjectCreateRequest } from '../types/project'
import useProjectStore from '../store/projectStore'

const HomePage: React.FC = () => {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const queryClient = useQueryClient()
  const setProjects = useProjectStore((s) => s.setProjects)

  const { data: projects = [], isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const list = await projectApi.list()
      setProjects(list)
      return list
    },
  })

  const createMutation = useMutation({
    mutationFn: (body: ProjectCreateRequest) => projectApi.create(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setDialogOpen(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => projectApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects'] }),
  })

  const filtered = projects.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description?.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  return (
    <Box sx={{ p: 4, maxWidth: 1400, mx: 'auto' }}>
      {/* Hero header */}
      <Box sx={{ mb: 5, textAlign: 'center' }}>
        <Typography
          variant="h3"
          fontWeight={800}
          gutterBottom
          sx={{
            background: 'linear-gradient(135deg, #a78bfa, #ec4899)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          MuseGen
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 520, mx: 'auto' }}>
          将故事文本转化为精美的动漫视频 — 由 AI 驱动的全流程创作平台
        </Typography>
      </Box>

      {/* Toolbar */}
      <Stack direction="row" spacing={2} alignItems="center" mb={3}>
        <TextField
          size="small"
          placeholder="搜索项目..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 220 }}
        />
        <Box sx={{ flex: 1 }} />
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>
          新建项目
        </Button>
      </Stack>

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          加载项目列表失败
        </Alert>
      )}

      {/* Loading */}
      {isLoading && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Project grid */}
      {!isLoading && (
        <>
          {filtered.length === 0 ? (
            <Box
              sx={{
                py: 10,
                textAlign: 'center',
                border: '2px dashed',
                borderColor: 'divider',
                borderRadius: 4,
              }}
            >
              <Typography variant="h6" color="text.secondary" gutterBottom>
                {searchQuery ? '没有匹配的项目' : '还没有项目'}
              </Typography>
              {!searchQuery && (
                <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)} sx={{ mt: 1 }}>
                  创建第一个项目
                </Button>
              )}
            </Box>
          ) : (
            <Grid container spacing={2.5}>
              {filtered.map((project) => (
                <Grid item key={project.id} xs={12} sm={6} md={4} lg={3}>
                  <ProjectCard
                    project={project}
                    onDelete={(id) => deleteMutation.mutate(id)}
                  />
                </Grid>
              ))}
            </Grid>
          )}

          <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mt: 3 }}>
            共 {projects.length} 个项目
          </Typography>
        </>
      )}

      {/* New project dialog */}
      <NewProjectDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onSubmit={(data) => createMutation.mutate(data)}
      />
    </Box>
  )
}

export default HomePage
