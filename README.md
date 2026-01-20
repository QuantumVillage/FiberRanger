```
__/\\\\\\\\\\\\\\\________/\\\_______________________________________________                     
 _\/\\\///////////________\/\\\_______________________________________________                    
  _\/\\\______________/\\\_\/\\\_______________________________________________                   
   _\/\\\\\\\\\\\_____\///__\/\\\____________/\\\\\\\\___/\\/\\\\\\\____________                  
    _\/\\\///////_______/\\\_\/\\\\\\\\\____/\\\/////\\\_\/\\\/////\\\___________                 
     _\/\\\_____________\/\\\_\/\\\////\\\__/\\\\\\\\\\\__\/\\\___\///____________                
      _\/\\\_____________\/\\\_\/\\\__\/\\\_\//\\///////___\/\\\___________________               
       _\/\\\_____________\/\\\_\/\\\\\\\\\___\//\\\\\\\\\\_\/\\\___________________              
        _\///______________\///__\/////////_____\//////////__\///____________________             
____/\\\\\\\\\____________________________________________________________________________        
 __/\\\///////\\\__________________________________________________________________________       
  _\/\\\_____\/\\\__________________________________/\\\\\\\\_______________________________      
   _\/\\\\\\\\\\\/_____/\\\\\\\\\_____/\\/\\\\\\____/\\\////\\\_____/\\\\\\\\___/\\/\\\\\\\__     
    _\/\\\//////\\\____\////////\\\___\/\\\////\\\__\//\\\\\\\\\___/\\\/////\\\_\/\\\/////\\\_    
     _\/\\\____\//\\\_____/\\\\\\\\\\__\/\\\__\//\\\__\///////\\\__/\\\\\\\\\\\__\/\\\___\///__   
      _\/\\\_____\//\\\___/\\\/////\\\__\/\\\___\/\\\__/\\_____\\\_\//\\///////___\/\\\_________  
       _\/\\\______\//\\\_\//\\\\\\\\/\\_\/\\\___\/\\\_\//\\\\\\\\___\//\\\\\\\\\\_\/\\\_________ 
        _\///________\///___\////////\//__\///____\///___\////////_____\//////////__\///__________
```

**An open source Phase-Diffusion Quantum Random Number Generator**

## Overview

Here's an overview of what's going on here:

```mermaid
---
title: PD-QRNG Process Flow
---

flowchart TD
    subgraph Fiber Optics
    L[Laser Diode]
    D[Detector]
    end
    subgraph R[<div style="width:30em; height:8em; display:flex; justify-content: flex-start;">Raspberry Pi Pico</div>]
        I[Pi Pico Init]
        subgraph PIO [<div style="width:10em; height:8em; display:flex; justify-content: flex-start;">PIO</div>]
        A[Narrow Pulse Wave]
        end
        subgraph Core 1
        G[Gather Entropy]
        end
        subgraph Core 2
        M[Calculate Min-Entropy]
        S[Generate SHA512 Hashes]
        U[Send Data over UART]
        end
    end
    B[USB Bridge]
    I -->|Initializes Cores| G[Gather Entropy]
    I -->|Loads PIO Program| A
    D -->|ADC read| G
    G -->|Process Data| M
    G -->|Load Raw Samples| S
    S --> U
    M --> U
    U -->|Go Back for More| G
    A  -->|Drives| L
    L e1@==>|pulses sent through fiber network| D
    e1@{ animate: true }
    U ==>|Serial Connection| B
```

## Hardware

### Optical Assembly

![](images/PD-QRNG.drawio.svg)

This is what the system looks like in hardware:

![PD-QRNG-v1](images/pd-qrng-v1.jpg)

### Circuit Details

`GPIO0` and `ADC0` are used on the RPi Pico. Here are more details:

* The `3V3` and `GND` pins (3rd and 5th on RHS) are used to power the two fiber modules.
* Both an A and a B module are used - one transmits at 1310 and recieves at 1510, the other at 1510 and recieves at 1310.
* Pin 8 on the A module (`TX` positive pin) is used to drive the laser.
* Pin 2 on the B module (`RX` positive pin) is used to recieve.
* Between this `RX` pin and the `ADC0` pin, there is a small circuit that normalizes the voltage from being centered around 0V to being centered around 1.65V. This circuit is comprised of:
    * 2x 10k Ohm resistors are used. On is connected to `3V3` and the other to `GND` they form a voltage divider the middle of which is tied to `ADC0`.
    * 1x 10nF ceramic capacitor is used - this goes from `RX` to `ADC0` that has the voltage lift from the divider. 

The circuit looks like this: 

![Circuit Diag](images/circuit.svg)
