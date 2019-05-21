# Home-Automation-Security #

Contains home security/automation modules for motion detection and temperature alert (used Raspberry Pi Zero). Output trigger and module's setting could be configured from a computer software. Raspberry Pi Zero communicates through the TCP connection. 
The package keeps the log of motion detection and the temperature. It also has SMS alert features.
This repository contains the scripts for the server side only (Raspberry Pi). The client need to connect the specified port through TCP to communicate, receive data  and command the raspberrry.
