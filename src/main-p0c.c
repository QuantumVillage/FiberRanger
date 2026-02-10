#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "hardware/vreg.h"

// Include the header generated from our .pio file
#include "squarewave.pio.h"

#define TARGET_FREQ_KHZ 250000 // 250 MHz System Clock
#define OUTPUT_PIN 0           // We will output on GP0

int main() {
    // ----------------------------------------------------
    // 1. OVERCLOCKING SETUP
    // ----------------------------------------------------
    
    // Increase voltage to stabilize high frequency (1.25V or 1.30V)
    vreg_set_voltage(VREG_VOLTAGE_1_25);
    sleep_ms(10);

    // Set system clock to 250MHz
    bool overclock_success = set_sys_clock_khz(TARGET_FREQ_KHZ, true);

    // Re-init stdio so USB/UART works at the new speed
    stdio_init_all();

    if (overclock_success) {
        printf("System Clock set to: %d Hz\n", clock_get_hz(clk_sys));
    } else {
        printf("Overclock failed! Running at default speed.\n");
    }

    // ----------------------------------------------------
    // 2. PIO SETUP
    // ----------------------------------------------------

    // Choose PIO instance (PIO0 or PIO1)
    PIO pio = pio0;
    
    // Find a free state machine
    uint sm = pio_claim_unused_sm(pio, true);
    
    // Load the program into PIO memory
    uint offset = pio_add_program(pio, &square_wave_program);

    // Start the square wave
    // Frequency will be System_Clock / 2 = 125 MHz
    square_wave_program_init(pio, sm, offset, OUTPUT_PIN);

    printf("Square wave generating on Pin %d at approx %d MHz\n", 
           OUTPUT_PIN, clock_get_hz(clk_sys) / 2 / 1000000);

    // Loop forever
    while (true) {
        tight_loop_contents();
    }
}