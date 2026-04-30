#include "project.h"
#include <string.h>
#include <stdio.h>

// this firmware was for programming both player devices
//in BLE component on top design, simply change the device name under GAP settings to Fencing_P1 or Fencing _P2

//use P1/P2 player id to program player 1/2 device
//define PLAYER_ID "P1"
#define PLAYER_ID "P2"

uint8_t ble_connected = 0;
uint32_t hit_counter = 0;

cy_stc_ble_conn_handle_t appConnHandle;

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

    Cy_BLE_Start(StackEventHandler);

    CapSense_1_Start();
    CapSense_1_ScanAllWidgets();

    for(;;)
    {
        Cy_BLE_ProcessEvents();

        if(!CapSense_1_IsBusy())
        {
            CapSense_1_ProcessAllWidgets();

            hit_active = CapSense_1_IsWidgetActive(CapSense_1_HITSENSOR_WDGT_ID);

            CapSense_1_ScanAllWidgets();
        }

        if(hit_active && hit_already_counted == 0)
        {
            // LED toggle means hit was detected
            Cy_GPIO_Inv(GPIO_PRT7, 1);

            hit_counter++;

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

            hit_already_counted = 1;
        }

        if(!hit_active)
        {
            hit_already_counted = 0;
        }

        CyDelay(20);
    }
}