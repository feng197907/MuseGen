import React from 'react'
import { Box, Typography } from '@mui/material'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import ShotCard from './ShotCard'
import type { Shot } from '../../types/project'

interface ShotListProps {
  shots: Shot[]
  selectedShotId: string | null
  onSelectShot: (id: string) => void
  onReorder: (orderedIds: string[]) => void
}

const ShotList: React.FC<ShotListProps> = ({ shots, selectedShotId, onSelectShot, onReorder }) => {
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id) return

    const oldIndex = shots.findIndex((s) => s.id === active.id)
    const newIndex = shots.findIndex((s) => s.id === over.id)
    if (oldIndex === -1 || newIndex === -1) return

    const reordered = [...shots]
    const [moved] = reordered.splice(oldIndex, 1)
    reordered.splice(newIndex, 0, moved)

    onReorder(reordered.map((s) => s.id))
  }

  if (shots.length === 0) {
    return (
      <Box sx={{ py: 6, textAlign: 'center' }}>
        <Typography color="text.secondary" variant="body2">
          暂无分镜数据
        </Typography>
        <Typography color="text.disabled" variant="caption">
          请先导入故事文本进行解析
        </Typography>
      </Box>
    )
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={shots.map((s) => s.id)} strategy={verticalListSortingStrategy}>
        <Box sx={{ py: 1 }}>
          {shots.map((shot) => (
            <ShotCard
              key={shot.id}
              shot={shot}
              selected={shot.id === selectedShotId}
              onSelect={() => onSelectShot(shot.id)}
            />
          ))}
        </Box>
      </SortableContext>
    </DndContext>
  )
}

export default ShotList
