import sys, struct, binascii, os
from Crypto.Hash import MD5

class PaytonModule():
    def __init__(self, header, body):
        self.__fromBin__(header, body)

    def __fromBin__(self, header, fw_body):

        (self.always_zeros, 
        self.mdul_magic, 
        self.mdul_type, 
        self.mdul_instance, 
        self.reserved_1, 
        self.hdr_len, 
        self.mdul_digest, 
        self.mdul_len, 
        self.mdul_chksum, 
        self.mdul_version, 
        self.reserved_2,
        self.hdr_chksum) = struct.unpack(">4s4sBB2sI16sII32s52sI", header)

        self.header = header
        self.module_data = fw_body[self.hdr_len : self.hdr_len + self.mdul_len]

    def check_digest(self, mdul_digest):
        digest = MD5.new(self.module_data).digest()
        return digest == mdul_digest

    def check_checksum(self, hdr_chksum):
        checksum = sum(self.header[:-4])
        return checksum == hdr_chksum
        
    def __str__(self):
        return  "Always zeros:    " + str(self.always_zeros.hex()) + "\n" \
                "Module Magic:    " + str(self.mdul_magic)         + "\n" \
                "Module Type:     " + str(self.mdul_type)          + "\n" \
                "Module Instance: " + str(self.mdul_instance)      + "\n" \
                "Reserved 1:      " + str(self.reserved_1)         + "\n" \
                "Header size:     " + str(self.hdr_len)            + " bytes\n" \
                "Module digest:   " + str(self.mdul_digest.hex())   + "     Correct: " + str(self.check_digest(self.mdul_digest)) + "\n" \
                "Module size:     " + str(self.mdul_len)           + " bytes\n" \
                "Module checksum: " + str(hex(self.mdul_chksum))   + "\n" \
                "Module version:  " + str(self.mdul_version.decode("ascii")) + "\n" \
                "Reserved 2:      " + str(len(self.reserved_2))    + " bytes\n" \
                "Header checksum: " + str(hex(self.hdr_chksum))    + "     Correct: " + str(self.check_checksum(self.hdr_chksum)) + "\n\n"

    def build(self):

        self.mdul_digest = MD5.new(self.module_data).digest()
        self.mdul_len = len(self.module_data)

        header = struct.pack(">4s4sBB2sI16sII32s52s", #"I"
                                self.always_zeros, 
                                self.mdul_magic, 
                                self.mdul_type, 
                                self.mdul_instance, 
                                self.reserved_1, 
                                self.hdr_len, 
                                self.mdul_digest,       # modified
                                self.mdul_len,          # modified
                                self.mdul_chksum, 
                                self.mdul_version, 
                                self.reserved_2#,
                                #self.hdr_chksum        # modified
                            )

        self.hdr_chksum = sum(header)
        header += struct.pack(">I", self.hdr_chksum)
        self.header = header
        
        return self.header, self.module_data

class PaytonFirmware():
    def __init__(self, data):
        self.firmware = data
        self.__fromBin__(self.firmware)
        self.__extractModules__(self.firmware)

    def __fromBin__(self, firmware):
        (self.fm_magic, 
        self.fm_signature, 
        self.fm_digest, 
        self.fm_randseq, 
        self.hdr_len, 
        self.mdul_hdr_len, 
        self.fm_len, 
        self.fm_version, 
        self.num_mduls, 
        self.flash_type, 
        self.slic_type) = struct.unpack(">16s32s16s16sIII32sIII", firmware[0:0x88])

    def __extractModules__(self, firmware):
        
        self.modules = []
        firmware_body = firmware[self.hdr_len + self.mdul_hdr_len * self.num_mduls : ]

        for i in range(0, self.num_mduls):
            module_header = firmware[self.hdr_len + self.mdul_hdr_len * i : self.hdr_len + self.mdul_hdr_len * i + self.mdul_hdr_len]
            
            module = PaytonModule(module_header, firmware_body)
            self.modules.append(module)

            firmware_body = firmware_body[self.mdul_hdr_len + module.mdul_len : ]        

    def check_digest(self, fm_digest):
        headers = bytearray(self.firmware[ : self.hdr_len + self.mdul_hdr_len * self.num_mduls])
        headers[16:64] = bytearray(48) # delete signature and digest
        digest = MD5.new(headers).digest()
        return digest == fm_digest

    def check_randseq(self, fm_randseq):
        headers = bytearray(self.firmware[ : self.hdr_len + self.mdul_hdr_len * self.num_mduls])
        headers[16:80] = bytearray(64) # delete signature, digest and randseq
        randseq = self.calc_randseq(headers)
        return randseq == fm_randseq

    def calc_randseq(self, headers):
        headers=bytearray(headers) # local copy to avoid smashing passed headers
        c = 0
        for i in range(0, len(headers)):
            headers[i] = (headers[i] + c) & 0xFF
            c += 19
        return MD5.new(headers).digest()
        
    def __str__(self):
        res =   "Magic:               " + str(self.fm_magic.decode("ascii")) + "\n" \
                "Signature:           " + str(self.fm_signature.hex())            + "\n" \
                "Digest:              " + str(self.fm_digest.hex())  + "   Correct: " + str(self.check_digest(self.fm_digest)) + "\n" \
                "Randseq:             " + str(self.fm_randseq.hex()) + "   Correct: " + str(self.check_randseq(self.fm_randseq)) + "\n" \
                "Header size:         " + str(self.hdr_len)                 + " bytes\n" \
                "Modules header size: " + str(self.mdul_hdr_len)            + " bytes\n" \
                "Firmware length:     " + str(self.fm_len)                  + " bytes\n" \
                "Version:             " + str(self.fm_version.decode("ascii"))    + "\n" \
                "Modules number:      " + str(self.num_mduls)                     + "\n" \
                "Flash type:          " + str(hex(self.flash_type))               + "\n" \
                "Slic type:           " + str(hex(self.slic_type))                + "\n\n" 

        for m in self.modules:
            res += str(m)

        return res

    def build(self):
        self.num_mduls = len(self.modules)
        headers = b""
        body = b""
        headers_len = self.hdr_len + self.mdul_hdr_len * self.num_mduls

        for m in self.modules:
            mdul_hdr, mdul_data = m.build()
            headers += mdul_hdr
            body += mdul_hdr + mdul_data

        self.fm_len = headers_len + len(body)

        self.fm_signature = bytes(32)
        self.fm_digest = bytes(16)
        self.fm_randseq = bytes(16)

        fw_head = struct.pack(">16s32s16s16sIII32sIII", 
                                self.fm_magic, 
                                self.fm_signature, 
                                self.fm_digest, 
                                self.fm_randseq, 
                                self.hdr_len, 
                                self.mdul_hdr_len, 
                                self.fm_len, 
                                self.fm_version, 
                                self.num_mduls, 
                                self.flash_type, 
                                self.slic_type
                            )
        
        headers = bytearray(fw_head + headers)
        
        self.fm_randseq = self.calc_randseq(headers)
        headers[64:64+16] = struct.pack(">16s", self.fm_randseq)

        self.fm_digest = MD5.new(headers).digest()
        headers[48:48+16] = struct.pack(">16s", self.fm_digest)

        self.firmware = headers + body

        return self.firmware


def create_write_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)

if __name__ == "__main__":
    if sys.argv[1]  == "info":
        with open(sys.argv[2], "rb") as f:
            p = PaytonFirmware(f.read())
        print(p)

    elif sys.argv[1] == "split":
        with open(sys.argv[2], "rb") as f:
            p = PaytonFirmware(f.read())
        print(p)
        for i, m in enumerate(p.modules):
            print("Extracting module", i)
            create_write_file("extract/" + str(i) + "_type" + str(m.mdul_type) + ".module", m.module_data)

    elif sys.argv[1] == "create_fs_update":
        with open(sys.argv[2], "rb") as f:
            p = PaytonFirmware(f.read())
        print(p)
        p.modules.remove(p.modules[1]) # remove second module
        with open(sys.argv[3], "rb") as f:
            p.modules[0].module_data = f.read() # replace first module (type 9) with passed kernel+fs image (module type 9 contains kernel + rootfs)
        cfw = p.build()
        print("\n\nNEW firmware:\n")
        print(p)

        with open(sys.argv[4], "wb") as f: # write new firmware
            f.write(cfw) 

        
