import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { ThemeProvider, CssBaseline } from '@mui/material'
import theme from './theme'
import AppShell from './components/layout/AppShell'
import HomePage from './pages/HomePage'
import StoryInputPage from './pages/StoryInputPage'
import StoryboardEditorPage from './pages/StoryboardEditorPage'
import AssetLibraryPage from './pages/AssetLibraryPage'
import ExportPage from './pages/ExportPage'

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppShell>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/project/:id/input" element={<StoryInputPage />} />
          <Route path="/project/:id/storyboard" element={<StoryboardEditorPage />} />
          <Route path="/project/:id/assets" element={<AssetLibraryPage />} />
          <Route path="/project/:id/export" element={<ExportPage />} />
        </Routes>
      </AppShell>
    </ThemeProvider>
  )
}

export default App
