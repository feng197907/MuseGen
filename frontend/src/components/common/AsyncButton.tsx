import React from 'react'
import { Button, CircularProgress, type ButtonProps } from '@mui/material'

interface AsyncButtonProps extends Omit<ButtonProps, 'onClick'> {
  loading?: boolean
  onClick?: () => void | Promise<void>
}

const AsyncButton: React.FC<AsyncButtonProps> = ({
  loading = false,
  disabled,
  children,
  startIcon,
  onClick,
  ...rest
}) => {
  const handleClick = async () => {
    if (loading || disabled) return
    await onClick?.()
  }

  return (
    <Button
      {...rest}
      disabled={disabled || loading}
      startIcon={loading ? <CircularProgress size={16} color="inherit" /> : startIcon}
      onClick={handleClick}
    >
      {children}
    </Button>
  )
}

export default AsyncButton
