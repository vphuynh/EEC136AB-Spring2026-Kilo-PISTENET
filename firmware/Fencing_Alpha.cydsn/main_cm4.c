#include "project.h"
#include <string.h>
#include <stdio.h>
#include <stdarg.h>

// this firmware was for programming both player devices
// in BLE component on top design, simply change the device name under GAP settings to Fencing_P1 or Fencing_P2

// use P1/P2 player id to program player 1/2 device
// define PLAYER_ID "P1"
#define PLAYER_ID "P1"


// ***************
// *** GLOBALS ***
// ***************


bool ble_connected = 0;
uint32_t hit_counter = 0;

cy_stc_ble_conn_handle_t app_con_handle;

#define WEAPON_UNKNOWN 0
#define WEAPON_EPEE    1
#define WEAPON_FOIL    2
#define WEAPON_SABER   3
uint8_t weapon = WEAPON_SABER;
bool weapon_changed = true;

#define TOUCH_NONE    0
#define TOUCH_INVALID 1
#define TOUCH_VALID   2

const uint8 DEBUG_HEADER[] = {0x0Du, 0x0Au};
const uint8 DEBUG_TAIL[] = {0x00u, 0xFFu, 0xFFu};


// ***************************
// *** DEBUG FUNCTIONALITY ***
// ***************************


int uart_print(const char * fmt, ...) {
    char    buf[256];
    int     len;
    va_list args;

    va_start(args, fmt);
    len = vsnprintf(buf, sizeof(buf), fmt, args);
    va_end(args);

    if (len > 0) {
        UART_PutString(buf);
    }
    return len;
}


int uart_println(const char * fmt, ...) {
    char    buf[256];
    va_list args;

    va_start(args, fmt);
    vsnprintf(buf, sizeof(buf) - 2u, fmt, args);
    va_end(args);

    return uart_print("%s\r\n", buf); // formatted string and \r\n sent atomically
}


// *****************************
// *** SENSING FUNCTIONALITY ***
// *****************************


volatile bool timer_flag = false;

void TimerInterruptHandler() {
    Cy_TCPWM_ClearInterrupt(SampleCounter_HW, SampleCounter_CNT_NUM, CY_TCPWM_INT_ON_TC);
    timer_flag = true;
}


int sense_epee() {
    // ButtonDrive (C) is disconnected
    Cy_GPIO_Clr(ButtonDrive_PORT, ButtonDrive_NUM);
    Cy_GPIO_SetDrivemode(ButtonDrive_PORT, ButtonDrive_NUM, CY_GPIO_DM_HIGHZ);
    // ButtonSense (B) is an input pullup
    Cy_GPIO_Set(ButtonSense_PORT, ButtonSense_NUM); // IMPORTANT!!!
    Cy_GPIO_SetDrivemode(ButtonSense_PORT, ButtonSense_NUM, CY_GPIO_DM_PULLUP);
    
    return Cy_GPIO_Read(ButtonSense_PORT, ButtonSense_NUM) ? TOUCH_NONE : TOUCH_VALID;
}


int sense_foil() {
    while (CapSense_IsBusy()); // wait for result if needed
    CapSense_ProcessAllWidgets(); // process results
    
    // read capacitive sensor
    bool cap = CapSense_IsWidgetActive(CapSense_HITSENSOR_WDGT_ID);
    
    // read button: ButtonDrive goes low, ButtonSense reads with pullup
    // read button with input pullup
    Cy_GPIO_Set(ButtonSense_PORT, ButtonSense_NUM); // IMPORTANT!!!
    Cy_GPIO_SetDrivemode(ButtonSense_PORT, ButtonSense_NUM, CY_GPIO_DM_PULLUP);
    // drive other side of button low
    Cy_GPIO_Clr(ButtonDrive_PORT, ButtonDrive_NUM);
    Cy_GPIO_SetDrivemode(ButtonDrive_PORT, ButtonDrive_NUM, CY_GPIO_DM_STRONG);
    
    CyDelayUs(10); // wait for stability (probably not necessary but you never know)
    bool button = Cy_GPIO_Read(ButtonSense_PORT, ButtonSense_NUM);
    
    // disconnect both sides of button
    Cy_GPIO_SetDrivemode(ButtonDrive_PORT, ButtonDrive_NUM, CY_GPIO_DM_HIGHZ);
    Cy_GPIO_SetDrivemode(ButtonSense_PORT, ButtonSense_NUM, CY_GPIO_DM_HIGHZ);
    
    // wait some time for stuff to stabilize before using capsense again
    CyDelayUs(10);
    CapSense_ScanAllWidgets(); // do next capsense scan
    
    return button ? (cap ? TOUCH_VALID : TOUCH_INVALID) : TOUCH_NONE;
}


int sense_saber() {
    // disconnect both sides of button
    Cy_GPIO_SetDrivemode(ButtonDrive_PORT, ButtonDrive_NUM, CY_GPIO_DM_HIGHZ);
    Cy_GPIO_SetDrivemode(ButtonSense_PORT, ButtonSense_NUM, CY_GPIO_DM_HIGHZ);
    
    while (CapSense_IsBusy()); // wait for result if needed
    CapSense_ProcessAllWidgets(); // process results
    bool cap = CapSense_IsWidgetActive(CapSense_HITSENSOR_WDGT_ID);
    CapSense_ScanAllWidgets(); // do next capsense scan
    
    return cap ? TOUCH_VALID : TOUCH_NONE;
}


// **********************
// *** LED INDICATION ***
// **********************


void indicate_weapon() {
    if (weapon == WEAPON_UNKNOWN) {
        Cy_GPIO_Write(LED_PORT, LED_NUM, 1);
        CyDelay(1000);
        Cy_GPIO_Write(LED_PORT, LED_NUM, 0);
    } else {
        for (int i = 0; i < weapon; i++) {
            Cy_GPIO_Write(LED_PORT, LED_NUM, 1);
            CyDelay(150);
            Cy_GPIO_Write(LED_PORT, LED_NUM, 0);
            CyDelay(150);
        }
    }
}


// *****************
// *** BLE STACK ***
// *****************


bool BLE_SendHitPacket(bool on_target, uint32_t hit_counter) {
    if (!ble_connected /*|| !notificationsReady*/)
        return false;
    
    char data[21];
    snprintf(data, sizeof(data), "%s,hit,%d,%lu", PLAYER_ID, on_target, hit_counter);

    cy_stc_ble_gatts_handle_value_ntf_t notifyPacket;

    notifyPacket.connHandle = app_con_handle;
    notifyPacket.handleValPair.attrHandle = CY_BLE_FENCINGSERVICE_HITPACKET_CHAR_HANDLE;
    notifyPacket.handleValPair.value.val = (uint8_t *)data;
    notifyPacket.handleValPair.value.len = strlen(data);

    bool success = Cy_BLE_GATTS_Notification(&notifyPacket) == CY_BLE_SUCCESS;
    Cy_BLE_ProcessEvents();
    return success;
}


void BLE_HandleWeaponChange(const char *command) {
    uart_print("Got command: '");
    UART_PutString(command);
    uart_println("'");
    if (strcmp(command, "weapon,epee") == 0) {
        weapon = WEAPON_EPEE;
        uart_println("weapon = epee");
    } else if (strcmp(command, "weapon,foil")  == 0) {
        weapon = WEAPON_FOIL;
        uart_println("weapon = foil");
    } else if (strcmp(command, "weapon,saber") == 0) {
        weapon = WEAPON_SABER;
        uart_println("weapon = saber");
    } else {
        weapon = WEAPON_UNKNOWN;
        uart_println("weapon = unknown");
    }
    weapon_changed = true;
}


void BLE_StackEventHandler(uint32 event, void *eventParam) {
    switch(event) {
        case CY_BLE_EVT_STACK_ON:
        case CY_BLE_EVT_GAP_DEVICE_DISCONNECTED:
            ble_connected = false;

            Cy_BLE_GAPP_StartAdvertisement(
                CY_BLE_ADVERTISING_FAST,
                CY_BLE_PERIPHERAL_CONFIGURATION_0_INDEX
            );
            break;

        case CY_BLE_EVT_GATT_CONNECT_IND:
            ble_connected = true;
            app_con_handle = *(cy_stc_ble_conn_handle_t *)eventParam;
            break;
            
        case CY_BLE_EVT_GATTS_WRITE_REQ:
        {
            cy_stc_ble_gatt_write_param_t *req =
                (cy_stc_ble_gatt_write_param_t*)eventParam;

            if (req->handleValPair.attrHandle ==
                    CY_BLE_FENCINGSERVICE_WEAPONCHANGE_CHAR_HANDLE)
            {
                /* Copy to null-terminated buffer */
                char cmd[21] = {0};
                uint16 len = req->handleValPair.value.len;
                if (len > 20) len = 20;
                memcpy(cmd, req->handleValPair.value.val, len);

                /* Send the write response first, then handle command */
                Cy_BLE_GATTS_WriteRsp(req->connHandle);

                BLE_HandleWeaponChange(cmd);   /* your handler — see below */
                return;                        /* skip default WriteRsp */
            }

            /* Check if laptop is toggling the HitPacket CCCD */
            if (req->handleValPair.attrHandle ==
                    CY_BLE_FENCINGSERVICE_HITPACKET_CLIENT_CHARACTERISTIC_CONFIGURATION_DESC_HANDLE)
            {
                Cy_BLE_GATTS_WriteRsp(req->connHandle);
                // TODO enable notifications here
                // CheckCCCD();
                return;
            }

            /* Default response for any other attribute */
            Cy_BLE_GATTS_WriteRsp(req->connHandle);
            break;
        }

        default:
            break;
    }
}


int main2() {
    Cy_SysInt_Init(&SampleCounterInt_cfg, TimerInterruptHandler);
    NVIC_ClearPendingIRQ(SampleCounterInt_cfg.intrSrc); /* Clears the interrupt */
    NVIC_EnableIRQ(SampleCounterInt_cfg.intrSrc); /* Enable the core interrupt */
    __enable_irq();
    
    Cy_TCPWM_Counter_Init(SampleCounter_HW, SampleCounter_CNT_NUM, &SampleCounter_config);
    Cy_TCPWM_Enable_Multiple(SampleCounter_HW, SampleCounter_CNT_MASK); /* Enable the counter instance */
    // Cy_TCPWM_Counter_SetPeriod(SampleCounter_HW, SampleCounter_CNT_NUM, TIMER_PERIOD_MSEC - 1);
    Cy_TCPWM_TriggerReloadOrIndex(SampleCounter_HW, SampleCounter_CNT_MASK); 
    
    UART_Start();
    uart_println("Startup player " PLAYER_ID);
    
    uart_print("init BLE... ");
    Cy_BLE_Start(BLE_StackEventHandler);
    uart_println("done.");

    uart_print("init CapSense... ");
    CapSense_Start();
    CapSense_ScanAllWidgets();
    uart_println("done.");
    
    uart_println("Startup done.");
    
    int touch_state = 0;
    int last_touch_state = 0;
    int run_length = 1;

    for (;;) {
        Cy_BLE_ProcessEvents();
        
        if (weapon_changed) {
            weapon_changed = false;
            last_touch_state = TOUCH_NONE;
            run_length = 1;
            indicate_weapon();
        }
        
        if (timer_flag) {
            timer_flag = false;
            
            if (weapon == WEAPON_EPEE) {
                touch_state = sense_epee();
            } else if (weapon == WEAPON_FOIL) {
                touch_state = sense_foil();
            } else if (weapon == WEAPON_SABER) {
                touch_state = sense_saber();
            }
            
            Cy_GPIO_Write(LED_PORT, LED_NUM, touch_state == TOUCH_VALID);
            
            if (touch_state != TOUCH_NONE && touch_state == last_touch_state) {
                run_length++;
                
                if (
                    (weapon == WEAPON_EPEE  && run_length == 12) // 6 ms (range is 2-10)
                 || (weapon == WEAPON_FOIL  && run_length == 28) // 14 ms (range is 13-15)
                 || (weapon == WEAPON_SABER && run_length == 2 ) // 1 ms (range is 0.1-1)
                ) {
                    if (touch_state == TOUCH_VALID) {
                        BLE_SendHitPacket(1, hit_counter);
                        uart_println("valid hit %ld", hit_counter);
                    } else {
                        Cy_GPIO_Write(LED_PORT, LED_NUM, 1);
                        BLE_SendHitPacket(1, hit_counter);
                        uart_println("off hit %ld", hit_counter);
                        Cy_GPIO_Write(LED_PORT, LED_NUM, 0);
                    }
                    hit_counter++;
                }
            } else {
                run_length = 1;
            }
            
            last_touch_state = touch_state;
        }
    }
}


int main_debug() {
    __enable_irq();    
    UART_Start();
    CapSense_Start();
    CapSense_ScanAllWidgets();
    
    for (;;) {
        if (!CapSense_IsBusy()) {
            CapSense_ProcessAllWidgets();
            
            // Debug with CapSense tuner software - access through TopDesign -> right-click CapSense component
            // Send packet header
            UART_PutArrayBlocking((uint8 *)(&DEBUG_HEADER), sizeof(DEBUG_HEADER));
            // Send packet with capsense data
            UART_PutArrayBlocking((uint8 *)(&CapSense_dsRam), sizeof(CapSense_dsRam));
            // Send packet tail
            UART_PutArrayBlocking((uint8 *)(&DEBUG_TAIL), sizeof(DEBUG_TAIL));
            
            CapSense_ScanAllWidgets();
        }
    }
}


int main() {
    return main2();
    // return main_debug();
}