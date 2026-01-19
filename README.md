# Fiber Ranger

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
        A[Offset Square Wave Pulse]
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

## Optical Assembly

![](images/PD-QRNG.drawio.svg)