# paytonImageEditor
Cisco SPA232D firmware editor

## GPL
[SPA112_SPA122_SPA232D_gpl_pkg-4.zip](https://netix.dl.sourceforge.net/project/cisco-gpl/Unified%20Communications/Communications%20Gateways/Cisco%20Small%20Business%20Voice%20Gateways%20and%20ATAs/SPA112_SPA122_SPA232D_gpl_pkg-4.zip)

## Build custom firmware
```bash
$ cd CustomFW
$ tar xf squashfs-root.tar.xz
$ ./build.sh
``` 

You can edit `CustomFW/squash-root/etc/my.sh` to run commands at boot.  
You can get info loading `http://192.168.15.1/my.asp`  
(I was not able to connect to telnet server)
