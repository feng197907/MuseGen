import { useCallback, useEffect } from 'react'
import useProjectStore from '../store/projectStore'
import { projectApi } from '../api/projectApi'

/**
 * Hook that binds undo/redo keyboard shortcuts (Ctrl+Z / Ctrl+Shift+Z)
 * and calls API endpoints for persistent undo/redo.
 */
const useUndoRedo = () => {
  const undo = useProjectStore((s) => s.undo)
  const redo = useProjectStore((s) => s.redo)
  const currentProject = useProjectStore((s) => s.currentProject)

  const handleUndo = useCallback(async () => {
    const record = undo()
    if (!record || !currentProject) return

    try {
      await projectApi.undo(currentProject.id)
      // Apply the before state locally (reverse the operation)
      useProjectStore.getState().updateProject(
        currentProject.id,
        record.beforeState,
        false,
      )
    } catch {
      // Revert by pushing record back
      useProjectStore.getState().pushUndo(record)
    }
  }, [undo, currentProject])

  const handleRedo = useCallback(async () => {
    const record = redo()
    if (!record || !currentProject) return

    try {
      await projectApi.redo(currentProject.id)
      useProjectStore.getState().updateProject(
        currentProject.id,
        record.afterState,
        false,
      )
    } catch {
      useProjectStore.getState().pushUndo(record)
    }
  }, [redo, currentProject])

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault()
        handleUndo()
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && e.shiftKey) {
        e.preventDefault()
        handleRedo()
      }
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [handleUndo, handleRedo])

  return { handleUndo, handleRedo, canUndo: useProjectStore((s) => s.undoStack.length > 0), canRedo: useProjectStore((s) => s.redoStack.length > 0) }
}

export default useUndoRedo
