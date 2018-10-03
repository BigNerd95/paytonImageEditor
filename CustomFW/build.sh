#!/bin/bash

sudo FW_TOOLS/mksquashfs squashfs-root fs.sqfs -noappend -le -noI
sudo FW_TOOLS/mkimage -A arm -O linux -C none -T filesystem -n "cybertan_rom_bin" -c "SP2X" -d fs.sqfs -s fs.img
cat FW_TOOLS/kernel.img fs.img > kernel_fs.img
python3 ../PaytonEditor.py create_fs_update ../Firmware/Payton_232D_1.4.1_002_282_102615_1043_pfmwr_hsfw.bin kernel_fs.img CustomFW.bin
sudo rm fs.sqfs fs.img kernel_fs.img
