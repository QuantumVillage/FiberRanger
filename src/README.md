# How to Build

Download the pi pico SDK: https://github.com/raspberrypi/pico-sdk

Set `export PICO_SDK_PATH=/path/to/pico-sdk/`

Then from the this `src` directory:

```bash
mkdir build
cd build
cmake ..
make
```

This will create a file `entropy_gen.uf2`. 

Plug in a raspberry pi pico into your USB port whilst holding down the `BOOTSEL` button. This will load a filesystem, to which you copy the `entropy_gen.uf2` file. 

Your pi pico is now programmed! 
