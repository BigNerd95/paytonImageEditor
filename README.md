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

## Firmware structure  
Header modules are present twice.  

| Size (byte)  | Type | Name | Description |
| :----------: | ---- | ---- | ------- |
| 136 | Firmware Header | Firmware Header | Header of the entire firmware image |
| 128 | Module Header | Module 1 header | Copy of Module 1 header |
| 128 | Module Header | Module 2 header | Copy of Module 2 header |
| 128 | Module Header | Module N header | Copy of Module N header |
| 128 | Module Header | Module 1 header |  |
| Module 1 size | Module Data | Module 1 data |  |
| 128 | Module Header | Module 2 header |  |
| Module 2 size | Module Data | Module 2 data |  |
| 128 | Module Header | Module N header |  |
| Module N size | Module Data | Module N data |  |

### Firmware Header  
| Size (byte)  | Type | Name | Description |
| :----------: | ---- | ---- | ------- |
| 16 | Byte array | Magic | Eg: PAYTOND FiRmWaRe |
| 32 | Byte array | Signature | Not used |  
| 16 | Byte array | Digest | MD5 of Firmware Header + Modules Headers |  
| 16 | Byte array | Randseq | Not so random |  
| 4 | Unsigned BE Int | Firmware Heder Size | Eg: 136 |
| 4 | Unsigned BE Int | Module Header Size | Eg: 128 |
| 4 | Unsigned BE Int | Firmware size | Entire firmware image size |
| 32 | Byte array | Version | Eg: 1.4.1 |
| 4 | Unsigned BE Int | Modules number | Number of modules present in this firmware image |
| 4 | Unsigned BE Int | Flash type | Eg: 0x137a80 |
| 4 | Unsigned BE Int | Slic type | Eg: 0x1eaea3a |

#### Randseq
1) Zero out Signature, Digest and Randseq in Firmware Header  
2) Concat Firmware Header and all Modules Headers    
3) Initialize a counter to 19
4) For each bytes 
    - sum the counter to the byte  
    - keep only first 8 bits 
    - increment counter by 19  
5) MD5 of the resulting bytes
Digest is computed on 

#### Digest
1) Write Randseq in Firmware Header  
2) MD5 Digest of Firmware Header + Modules Headers  

### Module Header
| Size (byte)  | Type | Name | Description |
| :----------: | ---- | ---- | ------- |
| 4 | Unsigned BE Int | Always zero | Eg: 0x00000000 |
| 4 | Byte array | Module Magic | Eg: RSFw |  
| 1 | Unsigned Int | Module type | Used to identify bootloader, filesystem, etc. |  
| 1 | Unsigned Int | Module instance |  |  
| 2 | Byte array | Reserved |  |
| 4 | Unsigned BE Int | Module Header Size | Eg: 128 |
| 16 | Byte array | Module Digest | MD5 of module data |
| 4 | Unsigned BE Int | Module size | Entire firmware image size |
| 4 | Unsigned BE Int | Module Checksum | Not used |
| 32 | Byte array | Module version | Eg: 1.0 |
| 52 | Byte array | Reserved | |
| 4 | Unsigned BE Int | Module Header Checksum | Sum of all bytes of this header (without this filed) |
