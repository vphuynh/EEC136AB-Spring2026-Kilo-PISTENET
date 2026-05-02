#include "project.h"
#include <string.h>
#include <stdio.h>
#include <stdarg.h>

const uint8 DEBUG_HEADER[] = {0x0Du, 0x0Au};
const uint8 DEBUG_TAIL[] = {0x00u, 0xFFu, 0xFFu};

// this firmware was for programming both player devices
// in BLE component on top design, simply change the device name under GAP settings to Fencing_P1 or Fencing _P2

// use P1/P2 player id to program player 1/2 device
// define PLAYER_ID "P1"
#define PLAYER_ID "P2"

uint8_t ble_connected = 0;
uint32_t hit_counter = 0;

cy_stc_ble_conn_handle_t appConnHandle;

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

void read_sensors(bool* cap, bool* button) {
    // read capacitive sensor
    *cap = CapSense_IsWidgetActive(CapSense_HITSENSOR_WDGT_ID);
    
    // read button: ButtonDrive goes low, ButtonSense reads with pullup
    // read button with input pullup
    Cy_GPIO_Set(ButtonSense_PORT, ButtonSense_NUM); // important!!!
    Cy_GPIO_SetDrivemode(ButtonSense_PORT, ButtonSense_NUM, CY_GPIO_DM_PULLUP);
    // drive other side of button low
    Cy_GPIO_Clr(ButtonDrive_PORT, ButtonDrive_NUM);
    Cy_GPIO_SetDrivemode(ButtonDrive_PORT, ButtonDrive_NUM, CY_GPIO_DM_STRONG);
    
    CyDelayUs(10); // wait for stability (probably not necessary but you never know)
    *button = Cy_GPIO_Read(ButtonSense_PORT, ButtonSense_NUM);
    
    // disconnect both sides of button
    Cy_GPIO_SetDrivemode(ButtonDrive_PORT, ButtonDrive_NUM, CY_GPIO_DM_HIGHZ);
    Cy_GPIO_SetDrivemode(ButtonSense_PORT, ButtonSense_NUM, CY_GPIO_DM_HIGHZ);
    
    // wait some time for stuff to stabilize before using capsense again
    CyDelayUs(10);
}

void StackEventHandler(uint32 event, void *eventParam)
{
    switch(event)
    {
        case CY_BLE_EVT_STACK_ON:
        case CY_BLE_EVT_GAP_DEVICE_DISCONNECTED:
            ble_connected = 0;

            Cy_BLE_GAPP_StartAdvertisement(
                CY_BLE_ADVERTISING_FAST,
                CY_BLE_PERIPHERAL_CONFIGURATION_0_INDEX
            );
            break;

        case CY_BLE_EVT_GATT_CONNECT_IND:
            ble_connected = 1;
            appConnHandle = *(cy_stc_ble_conn_handle_t *)eventParam;
            break;

        default:
            break;
    }
}

int main(void)
{
    __enable_irq();

    uint8_t hit_already_counted = 0;
    uint8_t hit_active = 0;
    char data[20];
    bool cap_state, button_state;
    
    UART_Start();
    uart_println("Startup player " PLAYER_ID);
    
    uart_print("init BLE... ");
    Cy_BLE_Start(StackEventHandler);
    uart_println("done.");

    uart_print("init CapSense... ");
    CapSense_Start();
    CapSense_ScanAllWidgets();
    uart_println("done.");
    
    uart_println("Startup done.");

    for(;;)
    {
        Cy_BLE_ProcessEvents();

        if(!CapSense_IsBusy())
        {
            CapSense_ProcessAllWidgets();
            
//            /* Debug with CapSense tuner software - access through TopDesign -> right-click CapSense component */
//            // Send packet header
//            UART_PutArrayBlocking((uint8 *)(&DEBUG_HEADER), sizeof(DEBUG_HEADER));
//            // Send packet with capsense data
//            UART_PutArrayBlocking((uint8 *)(&CapSense_dsRam), sizeof(CapSense_dsRam));
//            // Send packet tail
//            UART_PutArrayBlocking((uint8 *)(&DEBUG_TAIL), sizeof(DEBUG_TAIL));
            
            read_sensors(&cap_state, &button_state);
            Cy_GPIO_Write(LEDCapSense_PORT, LEDCapSense_NUM, !cap_state);
            Cy_GPIO_Write(LEDButton_PORT, LEDButton_NUM, !button_state);
            
            CapSense_ScanAllWidgets();
        }
        
        bool hit_active = cap_state && button_state;

        if(hit_active && hit_already_counted == 0)
        {
            hit_already_counted = 1;
            
            uart_println("cap hit %lu", hit_counter);

            // make each packet unique so Python does not ignore it as duplicate
            sprintf(data, "%s,hit,%lu", PLAYER_ID, (unsigned long)hit_counter);

            if(ble_connected)
            {
                cy_stc_ble_gatts_handle_value_ntf_t notifyPacket;

                notifyPacket.connHandle = appConnHandle;
                notifyPacket.handleValPair.attrHandle = CY_BLE_FENCINGSERVICE_HITPACKET_CHAR_HANDLE;
                notifyPacket.handleValPair.value.val = (uint8_t *)data;
                notifyPacket.handleValPair.value.len = strlen(data);

                Cy_BLE_GATTS_Notification(&notifyPacket);
                Cy_BLE_ProcessEvents();
            }
            
            hit_counter++;
        }

        if(!hit_active)
        {
            hit_already_counted = 0;
        }
    }
}