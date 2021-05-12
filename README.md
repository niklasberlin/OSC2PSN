# OSC2PSN
small script to convert Open Sound Control (OSC) into PosiStageNet (PSN) Data


## requirements

you need the python wrapper for the PSN implementation by vyv (https://github.com/vyv/psn-py), go to the libs folder, download the precompiled Version of the python wrapper for your python Version and OS (tested with Windows 10 64Bit and Python 3.9). place the psn.pyd file in the same folder as my script

you need to install python-osc (https://github.com/attwad/python-osc)

## configure

in the top part of my script is a config area, there you can configure the input and output IPs and Ports, as well as the number of trackers with their corresponding OSC address
