        /* if (!CapSense_IsBusy()) {
            CapSense_ProcessAllWidgets();
            
//            // Debug with CapSense tuner software - access through TopDesign -> right-click CapSense component
//            // Send packet header
//            UART_PutArrayBlocking((uint8 *)(&DEBUG_HEADER), sizeof(DEBUG_HEADER));
//            // Send packet with capsense data
//            UART_PutArrayBlocking((uint8 *)(&CapSense_dsRam), sizeof(CapSense_dsRam));
//            // Send packet tail
//            UART_PutArrayBlocking((uint8 *)(&DEBUG_TAIL), sizeof(DEBUG_TAIL));
            
            read_sensors(&cap_state, &button_state);
            
            CapSense_ScanAllWidgets();
        }
        
        bool hit_active = cap_state && button_state;
        // Cy_GPIO_Write(LED_PORT, LED_NUM, hit_active);

        if(hit_active && hit_already_counted == 0) {
            Cy_GPIO_Write(LED_PORT, LED_NUM, 1);
            CyDelay(100);
            Cy_GPIO_Write(LED_PORT, LED_NUM, 0);
            hit_already_counted = 1;
            uart_println("cap hit %lu", hit_counter);
            BLE_SendHitPacket(1, hit_counter);
            hit_counter++;
        }

        if(!hit_active) {
            hit_already_counted = 0;
        }*/