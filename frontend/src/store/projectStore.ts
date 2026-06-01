import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import type { Project } from '../types/project'

interface OperationRecord {
  action: string
  beforeState: Partial<Project>
  afterState: Partial<Project>
  timestamp: number
}

interface ProjectState {
  projects: Project[]
  currentProject: Project | null
  undoStack: OperationRecord[]
  redoStack: OperationRecord[]
  isLoading: boolean
  error: string | null
}

interface ProjectActions {
  setProjects: (projects: Project[]) => void
  setCurrentProject: (project: Project | null) => void
  addProject: (project: Project) => void
  updateProject: (id: string, updates: Partial<Project>, recordUndo?: boolean) => void
  removeProject: (id: string) => void
  pushUndo: (record: OperationRecord) => void
  undo: () => OperationRecord | null
  redo: () => OperationRecord | null
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearUndoRedo: () => void
}

const MAX_STACK = 20

const useProjectStore = create<ProjectState & ProjectActions>()(
  immer((set, get) => ({
    projects: [],
    currentProject: null,
    undoStack: [],
    redoStack: [],
    isLoading: false,
    error: null,

    setProjects: (projects) => {
      set((state) => {
        state.projects = projects
      })
    },

    setCurrentProject: (project) => {
      set((state) => {
        state.currentProject = project
      })
    },

    addProject: (project) => {
      set((state) => {
        state.projects.unshift(project)
      })
    },

    updateProject: (id, updates, recordUndo = false) => {
      set((state) => {
        const idx = state.projects.findIndex((p) => p.id === id)
        if (idx !== -1) {
          if (recordUndo) {
            const before = { ...state.projects[idx] }
            state.undoStack.push({
              action: 'updateProject',
              beforeState: before,
              afterState: { ...before, ...updates },
              timestamp: Date.now(),
            })
            if (state.undoStack.length > MAX_STACK) {
              state.undoStack.shift()
            }
            state.redoStack = []
          }
          Object.assign(state.projects[idx], updates)
        }
        if (state.currentProject?.id === id) {
          Object.assign(state.currentProject!, updates)
        }
      })
    },

    removeProject: (id) => {
      set((state) => {
        state.projects = state.projects.filter((p) => p.id !== id)
        if (state.currentProject?.id === id) {
          state.currentProject = null
        }
      })
    },

    pushUndo: (record) => {
      set((state) => {
        state.undoStack.push(record)
        if (state.undoStack.length > MAX_STACK) {
          state.undoStack.shift()
        }
        state.redoStack = []
      })
    },

    undo: () => {
      const { undoStack } = get()
      if (undoStack.length === 0) return null
      const record = undoStack[undoStack.length - 1]
      set((state) => {
        state.undoStack.pop()
        state.redoStack.push(record)
        if (state.redoStack.length > MAX_STACK) {
          state.redoStack.shift()
        }
      })
      return record
    },

    redo: () => {
      const { redoStack } = get()
      if (redoStack.length === 0) return null
      const record = redoStack[redoStack.length - 1]
      set((state) => {
        state.redoStack.pop()
        state.undoStack.push(record)
        if (state.undoStack.length > MAX_STACK) {
          state.undoStack.shift()
        }
      })
      return record
    },

    setLoading: (loading) => {
      set((state) => {
        state.isLoading = loading
      })
    },

    setError: (error) => {
      set((state) => {
        state.error = error
      })
    },

    clearUndoRedo: () => {
      set((state) => {
        state.undoStack = []
        state.redoStack = []
      })
    },
  })),
)

export default useProjectStore
