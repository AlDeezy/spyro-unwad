#
# Usage:
#   $ python unwad.py "path/to/WAD.WAD"
#

#
# Currently only works with Spyro 1998's NTSC release
#

import hashlib
import os
import sys
from typing import List
import wads

## prep ##

READ_SIZE = 4
OUTPUT_DIR = "out"

NTSC_U_MD5 = '8094f8a9851c5c7a9a306c565750335f'


def extract(file, out_dir, prefix='', name='output', max_files=0x100):
    if not os.path.exists(file):
        print("ERROR: File does not exist.")
        return
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    ref = 0
    fin = open(file, "rb")
    for i in range(max_files):
        o = int.from_bytes(bytearray(fin.read(READ_SIZE)), 'little')
        s = int.from_bytes(bytearray(fin.read(READ_SIZE)), 'little')
        if s == 0:
            # print("file #%i is of size 0. Skipping." % (i+1))
            fin.seek((i + 1) * 2 * READ_SIZE)
            continue

        # print("seeking to", hex(o))
        fin.seek(o)
        if out_dir == OUTPUT_DIR:
            fout = open("%s/%s" % (out_dir, wads.filenames[ref]), "wb")
            ref += 1
        else:
            fout = open("%s/%s%s%i.dat" %
                        (out_dir, prefix, name, (i+1)), "wb")
        # print(format("writing %s bytes" % hex(s)))
        fout.write(fin.read(s))
        fin.seek((i + 1) * 2 * READ_SIZE)
        fout.close()
    fin.close()


def get_archives(filepath) -> List[str]:
    num = 0
    infiles = os.listdir(filepath)
    infiles = [f for f in infiles if os.path.isfile(filepath+'/'+f)]
    infiles.sort()
    outfiles = []
    for file in infiles:
        fin = open(f'{filepath}/{file}', "rb")
        w = fin.read(4)
        if w == b'\x00\x08\x00\x00':
            outfiles.append(file)
            tf = os.path.splitext(file)[0]
        fin.close()
    return outfiles


## fun stuff ##

if not (len(sys.argv) > 1):
    print("ERROR: no arguments supplied.")
    exit()
if not (os.path.exists(sys.argv[1])):
    print("ERROR: file %s does not exist." % sys.argv[1])
    exit()
md5 = hashlib.md5()
with open(sys.argv[1], "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
        md5.update(chunk)
md5.hexdigest()
if not md5.hexdigest() == NTSC_U_MD5:
    print("ERROR: non-supported WAD.WAD file specified.")
    exit()

# Extract base WADs
extract(sys.argv[1], OUTPUT_DIR, name='file')

# Extract sub WADs
for file in get_archives(OUTPUT_DIR):
    fn = os.path.splitext(file)[0]
    f = f"{OUTPUT_DIR}/{file}"
    d = f"{OUTPUT_DIR}/{fn}/"
    extract(f, d, prefix=f"{fn}_", name='sub', max_files=0xa)
