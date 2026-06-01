import React, { useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import {
  Box,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import useAssetStore from '../store/assetStore'
import { assetApi } from '../api/assetApi'
import CharacterGrid from '../components/asset/CharacterGrid'
import SceneGrid from '../components/asset/SceneGrid'
import AssetDetailModal from '../components/asset/AssetDetailModal'
import type { Character, Scene } from '../types/asset'

type AssetTab = 'characters' | 'scenes'

const AssetLibraryPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>()
  const [tab, setTab] = useState<AssetTab>('characters')
  const [selectedChar, setSelectedChar] = useState<Character | null>(null)
  const [selectedScene, setSelectedScene] = useState<Scene | null>(null)
  const { characters, scenes, setCharacters, setScenes, isLoading } = useAssetStore()

  const { isLoading: isFetching, error } = useQuery({
    queryKey: ['assets', projectId],
    queryFn: async () => {
      if (!projectId) return null
      const [chars, scns] = await Promise.all([
        assetApi.listCharacters(projectId),
        assetApi.listScenes(projectId),
      ])
      setCharacters(chars)
      setScenes(scns)
      return { chars, scns }
    },
    enabled: !!projectId,
  })

  const handleRegenerateChar = useCallback(async (id: string) => {
    try {
      const updated = await assetApi.regenerateCharacter(id)
      useAssetStore.getState().updateCharacter(id, updated)
    } catch {
      // ignore
    }
  }, [])

  if (isFetching || isLoading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '80%' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">加载资产数据失败</Alert>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 4, maxWidth: 1400, mx: 'auto' }}>
      <Typography variant="h4" fontWeight={700} mb={3}>
        资产库
      </Typography>

      <Tabs
        value={tab}
        onChange={(_, v) => setTab(v)}
        sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab
          label={`角色 (${characters.length})`}
          value="characters"
        />
        <Tab
          label={`场景 (${scenes.length})`}
          value="scenes"
        />
      </Tabs>

      {tab === 'characters' && (
        <CharacterGrid
          characters={characters}
          onSelect={setSelectedChar}
        />
      )}

      {tab === 'scenes' && (
        <SceneGrid
          scenes={scenes}
          onSelect={setSelectedScene}
        />
      )}

      {/* Character detail modal */}
      <AssetDetailModal
        asset={selectedChar}
        type="character"
        open={!!selectedChar}
        onClose={() => setSelectedChar(null)}
        onRegenerate={handleRegenerateChar}
      />

      {/* Scene detail modal */}
      <AssetDetailModal
        asset={selectedScene}
        type="scene"
        open={!!selectedScene}
        onClose={() => setSelectedScene(null)}
      />
    </Box>
  )
}

export default AssetLibraryPage
