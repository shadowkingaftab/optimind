import { create } from 'zustand'

interface UploadState {
  files: File[]
  uploads: Array<{
    id: string
    file: File
    preview: string
    status: 'pending' | 'uploading' | 'processing' | 'complete' | 'error'
    progress: number
  }>
  addFiles: (files: File[]) => void
  removeFile: (id: string) => void
  updateUploadStatus: (id: string, status: string, progress?: number) => void
  clearUploads: () => void
}

export const useUploadStore = create<UploadState>((set) => ({
  files: [],
  uploads: [],

  addFiles: (files) => set((state) => ({
    files: [...state.files, ...files],
    uploads: [
      ...state.uploads,
      ...files.map((file) => ({
        id: Math.random().toString(36).slice(2),
        file,
        preview: '',
        status: 'pending' as const,
        progress: 0
      }))
    ]
  })),

  removeFile: (id) => set((state) => ({
    files: state.files.filter((_, i) => i !== parseInt(id)),
    uploads: state.uploads.filter((u) => u.id !== id)
  })),

  updateUploadStatus: (id, status, progress) => set((state) => ({
    uploads: state.uploads.map((u) =>
      u.id === id ? { ...u, status: status as UploadState['uploads'][0]['status'], progress: progress ?? u.progress } : u
    )
  })),

  clearUploads: () => set({ files: [], uploads: [] })
}))
