import React, { useState } from 'react'
import { Box, Toolbar, AppBar, Typography, IconButton, useTheme } from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import Sidebar from './Sidebar'

const DRAWER_WIDTH = 240

interface AppShellProps {
  children: React.ReactNode
}

const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const theme = useTheme()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden', bgcolor: 'background.default' }}>
      {/* Top AppBar */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          zIndex: theme.zIndex.drawer + 1,
          bgcolor: 'rgba(15,15,26,0.85)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid',
          borderColor: 'divider',
          width: sidebarOpen ? `calc(100% - ${DRAWER_WIDTH}px)` : '100%',
          ml: sidebarOpen ? `${DRAWER_WIDTH}px` : 0,
          transition: theme.transitions.create(['width', 'margin-left'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar variant="dense" sx={{ minHeight: 52 }}>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 800,
              letterSpacing: '-0.03em',
              background: 'linear-gradient(135deg, #a78bfa, #ec4899)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            MuseGen
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 1, mt: 0.2 }}>
            AI 动漫视频生成系统
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Sidebar open={sidebarOpen} drawerWidth={DRAWER_WIDTH} />

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          pt: '52px',
          height: '100vh',
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        {children}
      </Box>
    </Box>
  )
}

export default AppShell
