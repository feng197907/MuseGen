import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  Stack,
  Chip,
} from '@mui/material'
import HomeIcon from '@mui/icons-material/Home'
import MovieCreationIcon from '@mui/icons-material/MovieCreation'
import CollectionsIcon from '@mui/icons-material/Collections'
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary'
import useProjectStore from '../../store/projectStore'

interface SidebarProps {
  open: boolean
  drawerWidth: number
}

const NAV_ITEMS = [
  { path: '/', label: '首页', icon: <HomeIcon />, exact: true },
]

const PROJECT_NAV_ITEMS = [
  { suffix: 'input', label: '故事输入', icon: <MovieCreationIcon /> },
  { suffix: 'storyboard', label: '分镜编辑', icon: <CollectionsIcon /> },
  { suffix: 'assets', label: '资产库', icon: <CollectionsIcon /> },
  { suffix: 'export', label: '导出合成', icon: <VideoLibraryIcon /> },
]

const Sidebar: React.FC<SidebarProps> = ({ open, drawerWidth }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const currentProject = useProjectStore((s) => s.currentProject)

  const projectId = currentProject?.id

  const isActive = (path: string, exact = false): boolean => {
    if (exact) return location.pathname === path
    return location.pathname.startsWith(path)
  }

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: open ? drawerWidth : 0,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          bgcolor: 'rgba(20,20,35,0.95)',
          backdropFilter: 'blur(12px)',
          borderRight: '1px solid',
          borderColor: 'divider',
          pt: '56px',
        },
      }}
    >
      <Box sx={{ overflow: 'auto', p: 1 }}>
        {/* Global nav */}
        <List dense>
          {NAV_ITEMS.map((item) => (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                selected={isActive(item.path, item.exact)}
                onClick={() => navigate(item.path)}
                sx={{ borderRadius: 2, mb: 0.5 }}
              >
                <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: 14 }} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        {/* Project nav */}
        {projectId && (
          <>
            <Typography
              variant="caption"
              sx={{
                px: 2,
                pt: 2,
                pb: 0.5,
                display: 'block',
                fontWeight: 600,
                color: 'text.secondary',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontSize: 11,
              }}
            >
              当前项目
            </Typography>
            <Stack direction="row" sx={{ px: 2, pb: 1 }}>
              <Chip
                label={currentProject?.name || '未命名'}
                size="small"
                color="primary"
                variant="outlined"
                sx={{ fontSize: 11, height: 24 }}
              />
              <Chip
                label={currentProject?.status || 'draft'}
                size="small"
                sx={{ fontSize: 11, height: 24, ml: 0.5 }}
              />
            </Stack>
            <List dense>
              {PROJECT_NAV_ITEMS.map((item) => (
                <ListItem key={item.suffix} disablePadding>
                  <ListItemButton
                    selected={isActive(`/project/${projectId}/${item.suffix}`)}
                    onClick={() => navigate(`/project/${projectId}/${item.suffix}`)}
                    sx={{ borderRadius: 2, mb: 0.5 }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
                    <ListItemText
                      primary={item.label}
                      primaryTypographyProps={{ fontSize: 14 }}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </>
        )}

        {/* Empty state */}
        {!projectId && (
          <Box sx={{ px: 2, pt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              选择一个项目开始创作
            </Typography>
          </Box>
        )}
      </Box>
    </Drawer>
  )
}

export default Sidebar
