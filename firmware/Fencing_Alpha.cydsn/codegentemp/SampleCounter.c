/*******************************************************************************
* File Name: SampleCounter.c
* Version 1.0
*
* Description:
*  This file provides the source code to the API for the SampleCounter
*  component
*
********************************************************************************
* Copyright 2016-2017, Cypress Semiconductor Corporation.  All rights reserved.
* You may use this file only in accordance with the license, terms, conditions,
* disclaimers, and limitations in the end user license agreement accompanying
* the software package with which this file was provided.
*******************************************************************************/

#include "SampleCounter.h"

/** Indicates whether or not the SampleCounter has been initialized. 
*  The variable is initialized to 0 and set to 1 the first time 
*  SampleCounter_Start() is called. This allows the Component to 
*  restart without reinitialization after the first call to 
*  the SampleCounter_Start() routine.
*/
uint8_t SampleCounter_initVar = 0U;

/** The instance-specific configuration structure. This should be used in the 
*  associated SampleCounter_Init() function.
*/ 
cy_stc_tcpwm_counter_config_t const SampleCounter_config =
{
        .period = 24999UL,
        .clockPrescaler = 0UL,
        .runMode = 0UL,
        .countDirection = 0UL,
        .compareOrCapture = 2UL,
        .compare0 = 16384UL,
        .compare1 = 16384UL,
        .enableCompareSwap = false,
        .interruptSources = 1UL,
        .captureInputMode = 3UL,
        .captureInput = CY_TCPWM_INPUT_CREATOR,
        .reloadInputMode = 3UL,
        .reloadInput = CY_TCPWM_INPUT_CREATOR,
        .startInputMode = 3UL,
        .startInput = CY_TCPWM_INPUT_CREATOR,
        .stopInputMode = 3UL,
        .stopInput = CY_TCPWM_INPUT_CREATOR,
        .countInputMode = 3UL,
        .countInput = CY_TCPWM_INPUT_CREATOR,
};


/*******************************************************************************
* Function Name: SampleCounter_Start
****************************************************************************//**
*
*  Calls the SampleCounter_Init() when called the first time and enables 
*  the SampleCounter. For subsequent calls the configuration is left 
*  unchanged and the component is just enabled.
*
* \globalvars
*  \ref SampleCounter_initVar
*
*******************************************************************************/
void SampleCounter_Start(void)
{
    if (0U == SampleCounter_initVar)
    {
        (void)Cy_TCPWM_Counter_Init(SampleCounter_HW, SampleCounter_CNT_NUM, &SampleCounter_config); 

        SampleCounter_initVar = 1U;
    }

    Cy_TCPWM_Enable_Multiple(SampleCounter_HW, SampleCounter_CNT_MASK);
    
    #if (SampleCounter_INPUT_DISABLED == 7UL)
        Cy_TCPWM_TriggerStart(SampleCounter_HW, SampleCounter_CNT_MASK);
    #endif /* (SampleCounter_INPUT_DISABLED == 7UL) */    
}


/* [] END OF FILE */
