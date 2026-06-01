import React from 'react'
import { Box, Step, StepLabel, Stepper, Typography } from '@mui/material'

interface Step {
  label: string
  description?: string
}

interface ProgressStepperProps {
  steps: Step[]
  activeStep: number
  orientation?: 'horizontal' | 'vertical'
}

const ProgressStepper: React.FC<ProgressStepperProps> = ({
  steps,
  activeStep,
  orientation = 'horizontal',
}) => {
  return (
    <Box>
      <Stepper activeStep={activeStep} orientation={orientation} alternativeLabel={orientation === 'horizontal'}>
        {steps.map((step, idx) => (
          <Step key={idx} completed={idx < activeStep}>
            <StepLabel
              optional={
                step.description ? (
                  <Typography variant="caption" color="text.secondary">
                    {step.description}
                  </Typography>
                ) : undefined
              }
            >
              {step.label}
            </StepLabel>
          </Step>
        ))}
      </Stepper>
    </Box>
  )
}

export default ProgressStepper
