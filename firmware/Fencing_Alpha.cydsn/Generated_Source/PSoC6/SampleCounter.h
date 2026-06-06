/*******************************************************************************
* File Name: SampleCounter.h
* Version 1.0
*
* Description:
*  This file provides constants and parameter values for the SampleCounter
*  component.
*
********************************************************************************
* Copyright 2016-2017, Cypress Semiconductor Corporation.  All rights reserved.
* You may use this file only in accordance with the license, terms, conditions,
* disclaimers, and limitations in the end user license agreement accompanying
* the software package with which this file was provided.
*******************************************************************************/

#if !defined(SampleCounter_CY_TCPWM_COUNTER_PDL_H)
#define SampleCounter_CY_TCPWM_COUNTER_PDL_H

#include "cyfitter.h"
#include "tcpwm/cy_tcpwm_counter.h"

   
/*******************************************************************************
* Variables
*******************************************************************************/
/**
* \addtogroup group_globals
* @{
*/
extern uint8_t  SampleCounter_initVar;
extern cy_stc_tcpwm_counter_config_t const SampleCounter_config;
/** @} group_globals */


/***************************************
*  Conditional Compilation Parameters
***************************************/

#define SampleCounter_INIT_COMPARE_OR_CAPTURE    (2UL)


/***************************************
*        Function Prototypes
****************************************/
/**
* \addtogroup group_general
* @{
*/
void SampleCounter_Start(void);
__STATIC_INLINE cy_en_tcpwm_status_t SampleCounter_Init(cy_stc_tcpwm_counter_config_t const *config);
__STATIC_INLINE void SampleCounter_DeInit(void);
__STATIC_INLINE void SampleCounter_Enable(void);
__STATIC_INLINE void SampleCounter_Disable(void);
__STATIC_INLINE uint32_t SampleCounter_GetStatus(void);

#if(CY_TCPWM_COUNTER_MODE_CAPTURE == SampleCounter_INIT_COMPARE_OR_CAPTURE)
    __STATIC_INLINE uint32_t SampleCounter_GetCapture(void);
    __STATIC_INLINE uint32_t SampleCounter_GetCaptureBuf(void);
#else
    __STATIC_INLINE void SampleCounter_SetCompare0(uint32_t compare0);
    __STATIC_INLINE uint32_t SampleCounter_GetCompare0(void);
    __STATIC_INLINE void SampleCounter_SetCompare1(uint32_t compare1);
    __STATIC_INLINE uint32_t SampleCounter_GetCompare1(void);
    __STATIC_INLINE void SampleCounter_EnableCompareSwap(bool enable);
#endif /* (CY_TCPWM_COUNTER_MODE_CAPTURE == SampleCounter_INIT_COMPARE_OR_CAPTURE) */

__STATIC_INLINE void SampleCounter_SetCounter(uint32_t count);
__STATIC_INLINE uint32_t SampleCounter_GetCounter(void);
__STATIC_INLINE void SampleCounter_SetPeriod(uint32_t period);
__STATIC_INLINE uint32_t SampleCounter_GetPeriod(void);
__STATIC_INLINE void SampleCounter_TriggerStart(void);
__STATIC_INLINE void SampleCounter_TriggerReload(void);
__STATIC_INLINE void SampleCounter_TriggerStop(void);
__STATIC_INLINE void SampleCounter_TriggerCapture(void);
__STATIC_INLINE uint32_t SampleCounter_GetInterruptStatus(void);
__STATIC_INLINE void SampleCounter_ClearInterrupt(uint32_t source);
__STATIC_INLINE void SampleCounter_SetInterrupt(uint32_t source);
__STATIC_INLINE void SampleCounter_SetInterruptMask(uint32_t mask);
__STATIC_INLINE uint32_t SampleCounter_GetInterruptMask(void);
__STATIC_INLINE uint32_t SampleCounter_GetInterruptStatusMasked(void);
/** @} general */


/***************************************
*           API Constants
***************************************/

/**
* \addtogroup group_macros
* @{
*/
/** This is a ptr to the base address of the TCPWM instance */
#define SampleCounter_HW                 (SampleCounter_TCPWM__HW)

/** This is a ptr to the base address of the TCPWM CNT instance */
#define SampleCounter_CNT_HW             (SampleCounter_TCPWM__CNT_HW)

/** This is the counter instance number in the selected TCPWM */
#define SampleCounter_CNT_NUM            (SampleCounter_TCPWM__CNT_IDX)

/** This is the bit field representing the counter instance in the selected TCPWM */
#define SampleCounter_CNT_MASK           (1UL << SampleCounter_CNT_NUM)
/** @} group_macros */

#define SampleCounter_INPUT_MODE_MASK    (0x3U)
#define SampleCounter_INPUT_DISABLED     (7U)


/*******************************************************************************
* Function Name: SampleCounter_Init
****************************************************************************//**
*
* Invokes the Cy_TCPWM_Counter_Init() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE cy_en_tcpwm_status_t SampleCounter_Init(cy_stc_tcpwm_counter_config_t const *config)
{
    return(Cy_TCPWM_Counter_Init(SampleCounter_HW, SampleCounter_CNT_NUM, config));
}


/*******************************************************************************
* Function Name: SampleCounter_DeInit
****************************************************************************//**
*
* Invokes the Cy_TCPWM_Counter_DeInit() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_DeInit(void)                   
{
    Cy_TCPWM_Counter_DeInit(SampleCounter_HW, SampleCounter_CNT_NUM, &SampleCounter_config);
}

/*******************************************************************************
* Function Name: SampleCounter_Enable
****************************************************************************//**
*
* Invokes the Cy_TCPWM_Enable_Multiple() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_Enable(void)                   
{
    Cy_TCPWM_Enable_Multiple(SampleCounter_HW, SampleCounter_CNT_MASK);
}


/*******************************************************************************
* Function Name: SampleCounter_Disable
****************************************************************************//**
*
* Invokes the Cy_TCPWM_Disable_Multiple() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_Disable(void)                  
{
    Cy_TCPWM_Disable_Multiple(SampleCounter_HW, SampleCounter_CNT_MASK);
}


/*******************************************************************************
* Function Name: SampleCounter_GetStatus
****************************************************************************//**
*
* Invokes the Cy_TCPWM_Counter_GetStatus() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE uint32_t SampleCounter_GetStatus(void)                
{
    return(Cy_TCPWM_Counter_GetStatus(SampleCounter_HW, SampleCounter_CNT_NUM));
}


#if(CY_TCPWM_COUNTER_MODE_CAPTURE == SampleCounter_INIT_COMPARE_OR_CAPTURE)
    /*******************************************************************************
    * Function Name: SampleCounter_GetCapture
    ****************************************************************************//**
    *
    * Invokes the Cy_TCPWM_Counter_GetCapture() PDL driver function.
    *
    *******************************************************************************/
    __STATIC_INLINE uint32_t SampleCounter_GetCapture(void)               
    {
        return(Cy_TCPWM_Counter_GetCapture(SampleCounter_HW, SampleCounter_CNT_NUM));
    }


    /*******************************************************************************
    * Function Name: SampleCounter_GetCaptureBuf
    ****************************************************************************//**
    *
    * Invokes the Cy_TCPWM_Counter_GetCaptureBuf() PDL driver function.
    *
    *******************************************************************************/
    __STATIC_INLINE uint32_t SampleCounter_GetCaptureBuf(void)            
    {
        return(Cy_TCPWM_Counter_GetCaptureBuf(SampleCounter_HW, SampleCounter_CNT_NUM));
    }
#else
    /*******************************************************************************
    * Function Name: SampleCounter_SetCompare0
    ****************************************************************************//**
    *
    * Invokes the Cy_TCPWM_Counter_SetCompare0() PDL driver function.
    *
    *******************************************************************************/
    __STATIC_INLINE void SampleCounter_SetCompare0(uint32_t compare0)      
    {
        Cy_TCPWM_Counter_SetCompare0(SampleCounter_HW, SampleCounter_CNT_NUM, compare0);
    }


    /*******************************************************************************
    * Function Name: SampleCounter_GetCompare0
    ****************************************************************************//**
    *
    * Invokes the Cy_TCPWM_Counter_GetCompare0() PDL driver function.
    *
    *******************************************************************************/
    __STATIC_INLINE uint32_t SampleCounter_GetCompare0(void)              
    {
        return(Cy_TCPWM_Counter_GetCompare0(SampleCounter_HW, SampleCounter_CNT_NUM));
    }


    /*******************************************************************************
    * Function Name: SampleCounter_SetCompare1
    ****************************************************************************//**
    *
    * Invokes the Cy_TCPWM_Counter_SetCompare1() PDL driver function.
    *
    *******************************************************************************/
    __STATIC_INLINE void SampleCounter_SetCompare1(uint32_t compare1)      
    {
        Cy_TCPWM_Counter_SetCompare1(SampleCounter_HW, SampleCounter_CNT_NUM, compare1);
    }


    /*******************************************************************************
    * Function Name: SampleCounter_GetCompare1
    ****************************************************************************//**
    *
    * Invokes the Cy_TCPWM_Counter_GetCompare1() PDL driver function.
    *
    *******************************************************************************/
    __STATIC_INLINE uint32_t SampleCounter_GetCompare1(void)              
    {
        return(Cy_TCPWM_Counter_GetCompare1(SampleCounter_HW, SampleCounter_CNT_NUM));
    }


    /*******************************************************************************
    * Function Name: SampleCounter_EnableCompareSwap
    ****************************************************************************//**
    *
    * Invokes the Cy_TCPWM_Counter_EnableCompareSwap() PDL driver function.
    *
    *******************************************************************************/
    __STATIC_INLINE void SampleCounter_EnableCompareSwap(bool enable)  
    {
        Cy_TCPWM_Counter_EnableCompareSwap(SampleCounter_HW, SampleCounter_CNT_NUM, enable);
    }
#endif /* (CY_TCPWM_COUNTER_MODE_CAPTURE == SampleCounter_INIT_COMPARE_OR_CAPTURE) */


/*******************************************************************************
* Function Name: SampleCounter_SetCounter
****************************************************************************//**
*
* Invokes the Cy_TCPWM_Counter_SetCounter() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_SetCounter(uint32_t count)          
{
    Cy_TCPWM_Counter_SetCounter(SampleCounter_HW, SampleCounter_CNT_NUM, count);
}


/*******************************************************************************
* Function Name: SampleCounter_GetCounter
****************************************************************************//**
*
* Invokes the Cy_TCPWM_Counter_GetCounter() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE uint32_t SampleCounter_GetCounter(void)               
{
    return(Cy_TCPWM_Counter_GetCounter(SampleCounter_HW, SampleCounter_CNT_NUM));
}


/*******************************************************************************
* Function Name: SampleCounter_SetPeriod
****************************************************************************//**
*
* Invokes the Cy_TCPWM_Counter_SetPeriod() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_SetPeriod(uint32_t period)          
{
    Cy_TCPWM_Counter_SetPeriod(SampleCounter_HW, SampleCounter_CNT_NUM, period);
}


/*******************************************************************************
* Function Name: SampleCounter_GetPeriod
****************************************************************************//**
*
* Invokes the Cy_TCPWM_Counter_GetPeriod() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE uint32_t SampleCounter_GetPeriod(void)                
{
    return(Cy_TCPWM_Counter_GetPeriod(SampleCounter_HW, SampleCounter_CNT_NUM));
}


/*******************************************************************************
* Function Name: SampleCounter_TriggerStart
****************************************************************************//**
*
* Invokes the Cy_TCPWM_TriggerStart() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_TriggerStart(void)             
{
    Cy_TCPWM_TriggerStart(SampleCounter_HW, SampleCounter_CNT_MASK);
}


/*******************************************************************************
* Function Name: SampleCounter_TriggerReload
****************************************************************************//**
*
* Invokes the Cy_TCPWM_TriggerReloadOrIndex() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_TriggerReload(void)     
{
    Cy_TCPWM_TriggerReloadOrIndex(SampleCounter_HW, SampleCounter_CNT_MASK);
}


/*******************************************************************************
* Function Name: SampleCounter_TriggerStop
****************************************************************************//**
*
* Invokes the Cy_TCPWM_TriggerStopOrKill() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_TriggerStop(void)
{
    Cy_TCPWM_TriggerStopOrKill(SampleCounter_HW, SampleCounter_CNT_MASK);
}


/*******************************************************************************
* Function Name: SampleCounter_TriggerCapture
****************************************************************************//**
*
* Invokes the Cy_TCPWM_TriggerCaptureOrSwap() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_TriggerCapture(void)     
{
    Cy_TCPWM_TriggerCaptureOrSwap(SampleCounter_HW, SampleCounter_CNT_MASK);
}


/*******************************************************************************
* Function Name: SampleCounter_GetInterruptStatus
****************************************************************************//**
*
* Invokes the Cy_TCPWM_GetInterruptStatus() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE uint32_t SampleCounter_GetInterruptStatus(void)       
{
    return(Cy_TCPWM_GetInterruptStatus(SampleCounter_HW, SampleCounter_CNT_NUM));
}


/*******************************************************************************
* Function Name: SampleCounter_ClearInterrupt
****************************************************************************//**
*
* Invokes the Cy_TCPWM_ClearInterrupt() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_ClearInterrupt(uint32_t source)     
{
    Cy_TCPWM_ClearInterrupt(SampleCounter_HW, SampleCounter_CNT_NUM, source);
}


/*******************************************************************************
* Function Name: SampleCounter_SetInterrupt
****************************************************************************//**
*
* Invokes the Cy_TCPWM_SetInterrupt() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_SetInterrupt(uint32_t source)
{
    Cy_TCPWM_SetInterrupt(SampleCounter_HW, SampleCounter_CNT_NUM, source);
}


/*******************************************************************************
* Function Name: SampleCounter_SetInterruptMask
****************************************************************************//**
*
* Invokes the Cy_TCPWM_SetInterruptMask() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE void SampleCounter_SetInterruptMask(uint32_t mask)     
{
    Cy_TCPWM_SetInterruptMask(SampleCounter_HW, SampleCounter_CNT_NUM, mask);
}


/*******************************************************************************
* Function Name: SampleCounter_GetInterruptMask
****************************************************************************//**
*
* Invokes the Cy_TCPWM_GetInterruptMask() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE uint32_t SampleCounter_GetInterruptMask(void)         
{
    return(Cy_TCPWM_GetInterruptMask(SampleCounter_HW, SampleCounter_CNT_NUM));
}


/*******************************************************************************
* Function Name: SampleCounter_GetInterruptStatusMasked
****************************************************************************//**
*
* Invokes the Cy_TCPWM_GetInterruptStatusMasked() PDL driver function.
*
*******************************************************************************/
__STATIC_INLINE uint32_t SampleCounter_GetInterruptStatusMasked(void)
{
    return(Cy_TCPWM_GetInterruptStatusMasked(SampleCounter_HW, SampleCounter_CNT_NUM));
}

#endif /* SampleCounter_CY_TCPWM_COUNTER_PDL_H */


/* [] END OF FILE */
