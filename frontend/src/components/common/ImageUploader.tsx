import React, { useRef, useState } from 'react'
import { Box, Typography, Button, CircularProgress, Alert } from '@mui/material'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import ImageIcon from '@mui/icons-material/Image'
import client from '../../api/client'

interface ImageUploaderProps {
  /** Uploaded image URL callback */
  onUpload: (url: string) => void
  /** Upload endpoint path (relative to API base) */
  uploadPath: string
  label?: string
  previewUrl?: string | null
  accept?: string
}

const ImageUploader: React.FC<ImageUploaderProps> = ({
  onUpload,
  uploadPath,
  label = '上传图片',
  previewUrl,
  accept = 'image/png,image/jpeg,image/webp',
}) => {
  const inputRef = useRef<HTMLInputElement>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [preview, setPreview] = useState<string | null>(previewUrl || null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Local preview
    const objectUrl = URL.createObjectURL(file)
    setPreview(objectUrl)

    setLoading(true)
    setError(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await client.post(uploadPath, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      onUpload((res.data as any).url)
    } catch (err: any) {
      setError(err.message || '上传失败')
      setPreview(previewUrl || null)
    } finally {
      setLoading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  return (
    <Box>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      <Box
        sx={{
          border: '2px dashed',
          borderColor: 'divider',
          borderRadius: 2,
          p: 2,
          textAlign: 'center',
          bgcolor: 'rgba(255,255,255,0.02)',
          cursor: 'pointer',
          '&:hover': { borderColor: 'primary.main' },
          transition: 'border-color 0.15s',
        }}
        onClick={() => !loading && inputRef.current?.click()}
      >
        {preview ? (
          <img
            src={preview}
            alt="preview"
            style={{
              maxWidth: '100%',
              maxHeight: 160,
              objectFit: 'cover',
              borderRadius: 8,
              display: 'block',
              margin: '0 auto 8px',
            }}
          />
        ) : (
          <ImageIcon sx={{ fontSize: 40, color: 'text.disabled', mb: 1 }} />
        )}

        {loading ? (
          <CircularProgress size={20} />
        ) : (
          <Button size="small" startIcon={<UploadFileIcon />} disabled={loading}>
            {label}
          </Button>
        )}

        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
          支持 PNG / JPEG / WebP
        </Typography>
      </Box>
      {error && (
        <Alert severity="error" sx={{ mt: 1 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
    </Box>
  )
}

export default ImageUploader
