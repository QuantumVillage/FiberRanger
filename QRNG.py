import machine
import rp2
import _thread
import math
import time
import ubinascii
import uhashlib

# ----------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------
TARGET_FREQ = 250_000_000  # 250 MHz System Clock
BATCH_SIZE = 1024          # Samples per batch
LAG_DEPTH = 12             # Compare current sample vs 12 samples ago

# ----------------------------------------------------------------------------
# PIO PROGRAM
# ----------------------------------------------------------------------------
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def square_wave():
    # The main loop:
    # 1. Set pin high (1 cycle)
    # 2. Set pin low  (1 cycle) + 4 cycles delay
    wrap_target()
    set(pins, 1)
    set(pins, 0) [4] 
    wrap()

# ----------------------------------------------------------------------------
# GLOBALS (Inter-core communication)
# ----------------------------------------------------------------------------
sample_queue = []
queue_lock = _thread.allocate_lock()

# ----------------------------------------------------------------------------
# CORE 1: Processing & Output
# ----------------------------------------------------------------------------
def core1_entry():
    # Ring buffer history
    history = [0] * LAG_DEPTH
    hist_head = 0
    
    print("Core 1: Processing Entropy & Hashing.")
    
    while True:
        batch = None
        with queue_lock:
            if sample_queue:
                batch = sample_queue.pop(0)
        
        if batch is None:
            # No data yet, yield slightly
            time.sleep_ms(1)
            continue
            
        # --- Processing ---
        # Histogram for Min-Entropy (0-4095 for 12-bit delta)
        # Using a list as a sparse array/histogram
        counts = [0] * 4096 
        max_count = 0
        
        min_val = 4096
        max_val = 0
        
        # Prepare bytes for hashing (1024 samples * 2 bytes = 2048 bytes)
        batch_bytes = bytearray(BATCH_SIZE * 2)
        
        for i in range(BATCH_SIZE):
            val = batch[i] & 0xFFF
            
            # Update Min/Max
            if val < min_val: min_val = val
            if val > max_val: max_val = val
            
            # Lagged Derivative Calculation
            old_val = history[hist_head]
            history[hist_head] = val
            hist_head = (hist_head + 1) % LAG_DEPTH
            
            delta = (val - old_val + 2048) & 0xFFF
            
            counts[delta] += 1
            if counts[delta] > max_count:
                max_count = counts[delta]
            
            # Store raw sample in bytearray (Little Endian)
            batch_bytes[2*i] = val & 0xFF
            batch_bytes[2*i+1] = (val >> 8) & 0xFF

        # Calculate Min-Entropy
        min_entropy = 10.0 - math.log2(max_count) if max_count > 0 else 0.0
        
        # Calculate Range
        dynamic_range = max_val - min_val
        
        # Squelch Safety Check
        if dynamic_range < 200:
            min_entropy = 0.0
            
        # Hashing (Using SHA256 as SHA512 is often not available in standard MicroPython)
        h1_ctx = uhashlib.sha256()
        h1_ctx.update(batch_bytes)
        hash_out_1 = h1_ctx.digest()
        
        h2_ctx = uhashlib.sha256()
        h2_ctx.update(hash_out_1)
        hash_out_2 = h2_ctx.digest()
        
        # Output
        print(f"H_min: {min_entropy:.4f} | R: {dynamic_range:4d} | Data: ")
        print(ubinascii.hexlify(hash_out_1).decode())
        print(ubinascii.hexlify(hash_out_2).decode())

# ----------------------------------------------------------------------------
# CORE 0: Hardware Setup & Acquisition
# ----------------------------------------------------------------------------
def main():
    # 1. Overclock to 250 MHz
    machine.freq(TARGET_FREQ)
    
    # 2. Launch Core 1
    _thread.start_new_thread(core1_entry, ())
    
    # 3. Setup PIO Square Wave on Pin 0
    # Note: Pin 0 is set to high drive strength/slew via direct register write if needed, 
    # but standard PIO init is usually sufficient for basic operation.
    # To match C "MAXIMIZE DRIVER PERFORMANCE": PADS_BANK0_GPIO0 (0x4001c004) = 0x31 (Fast Slew, 12mA)
    machine.mem32[0x4001c004] = 0x31 
    
    sm = rp2.StateMachine(0, square_wave, freq=TARGET_FREQ, set_base=machine.Pin(0))
    sm.active(1)
    
    # 4. Setup ADC on Pin 26 (ADC 0)
    adc = machine.ADC(0)
    
    print(f"Core 0: Generating {machine.freq()/1000000} MHz Wave & Sampling ADC.")
    
    # 5. Main Loop
    while True:
        current_batch = []
        for _ in range(BATCH_SIZE):
            # Read ADC (MicroPython returns 16-bit 0-65535)
            val = adc.read_u16()
            current_batch.append(val)
            
            # Jitter: busy_wait_us_32(1 + (adc_read() & 0x03))
            jitter_read = adc.read_u16()
            time.sleep_us(1 + (jitter_read & 0x03))
            
        with queue_lock:
            # Simple flow control to prevent OOM if Core 1 is slow
            if len(sample_queue) < 4:
                sample_queue.append(current_batch)

if __name__ == "__main__":
    main()