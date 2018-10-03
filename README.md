# paytonImageEditor
Cisco SPA232D firmware editor

## GPL
[SPA112_SPA122_SPA232D_gpl_pkg-4.zip](https://netix.dl.sourceforge.net/project/cisco-gpl/Unified%20Communications/Communications%20Gateways/Cisco%20Small%20Business%20Voice%20Gateways%20and%20ATAs/SPA112_SPA122_SPA232D_gpl_pkg-4.zip)

## Build custom firmware
```bash
$ cd CustomFW
$ sudo tar xf squashfs-root.tar.xz
$ ./build.sh
``` 
You can find a pre-built custom firmware with only telnet enabled [here](https://github.com/BigNerd95/paytonImageEditor/blob/master/CustomFW/CustomFW.bin?raw=true)

## Flash CustomFW
Flash the custom firmware like an official update through the web interface

## Telnet
You can now connect to telnet:
```bash
$ telnet 192.168.15.1 23000
```
(No login)

You must connect via LAN port.
