#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import sys
import argparse
import json
import struct

VERSION = "2.1.2"
MEMORY_ALIGN = 4
N_TYPE = 0xcafe1a7e
OWNER = 'FDO'
NOTE_SECTION_NAME = ".note.package"
OUTPUT_LINKER_SCRIPT_NAME = "module_info.ld"

DESCRIPTION = 'Generate package note section'

EPILOG = """
    This tool generates linker script for ELF binaries to stamp
    package/module information into note section. The arguments are in ASCII
    charset as described above.

    Script outputs module_info.ld as linker script and .note.package.bin files
    into the script running directory.

    Once linker script is generated, linker arguments
    "-Wl,-T,module_info.ld" need to be passed to GCC/clang compilers.

    Example:
    Build executable with linker script
    $ gcc -o hello_world hello_world.c -Wl,-T,module_info.ld

    Check if .note.package is part of the ELF file
    $ readelf -n hello_world

    Check payload data in hex and string view
    $ objdump -s hello_world -j .note.package

    -- LINKER SCRIPT AND C CODE MIX METHOD --

    This option generates linker script with minimal information, and
    C code with note section content. This is SELinux compliant.
    This method is default, it doesn't require to set stamp argument.

    $ ./generate-package-note.py --name "pkgname" --type "rpm" \\
        --version "1.2.3.4" --moduleVersion "1.2.3.4-beta" \\
        --os "mariner" --osVersion "1.0" \\
        --maintainer "DEADBEEF-BBC3-4FED-9192-110C11DED04D" \\
        --copyright "Microsoft" \\
        --outdir "/source/pkgname/build/" \\
        --repo "pkgname-git-repo-name" \\
        --hash "527233b5780c25911998c4a1b3d35d38fafa39cd" \\
        --branch "1.0" --stamp "Mix"

    - Generated example C code:

    const unsigned char __attribute__((aligned(4), section(".note.package")))
         __attribute__((used)) module_info_note_package[] = {
            0x04,  0x00,  0x00,  0x00,
            0xac,  0x01,  0x00,  0x00,
            0x7e,  0x1a,  0xfe,  0xca,
            0x46,  0x44,  0x4f,  0x00,
            ....
        };

    - Generated example Linker script:
        SECTIONS
        {
            .note.package : ALIGN(4)
            {
                KEEP (*(.note.package))
            }
        }
        INSERT AFTER .note.gnu.build-id;

    -- LINKER SCRIPT ONLY OPTION --

    Due to limited linker support and SELinux compliancy problem,
    this method will be kept as experimental.

    $ ./generate-package-note.py --name "pkgname" --type "rpm" \\
        --version "1.2.3.4" --moduleVersion "1.2.3.4-beta" \\
        --os "mariner" --osVersion "1.0" \\
        --maintainer "DEADBEEF-BBC3-4FED-9192-110C11DED04D" \\
        --copyright "Microsoft" \\
        --outdir "/source/pkgname/build/" \\
        --repo "pkgname-git-repo-name" \\
        --hash "527233b5780c25911998c4a1b3d35d38fafa39cd" \\
        --branch "1.0" --stamp "LinkerOnly"

        SECTIONS
        {
            .note.package (READONLY) : ALIGN(4)
            {
                BYTE(0x04) BYTE(0x00) BYTE(0x00) BYTE(0x00)
                BYTE(0x04) BYTE(0x01) BYTE(0x00) BYTE(0x00)
                BYTE(0x7e) BYTE(0x1a) BYTE(0xfe) BYTE(0xca)
                BYTE(0x46) BYTE(0x44) BYTE(0x4f) BYTE(0x00)
                .....
                BYTE(0x35) BYTE(0x22) BYTE(0x0a) BYTE(0x7d)

                KEEP (*(.note.package))
            }
        }
        INSERT AFTER .note.gnu.build-id;

    Last but not least, please make sure arguments are quoted.
    """

DO_NOT_EDIT_COMMENT = """
    This file is automatically generated by """ \
    + os.path.basename(sys.argv[0]) + """ tool.
    Do not modify this file, your changes will be lost!
"""
C_MODULE_NAME = 'module_info.c'


class Endian():
    LittleEndian = "<"
    BigEndian = ">"
    map = {
        "LittleEndian": LittleEndian,
        "BigEndian": BigEndian
    }


def align_len(len, align=4):
    return (len + align - 1) & ~(align - 1)


def align_memory(str, align=4):
    len_str = len(str)
    res = str.ljust(align_len(len_str, align), chr(0))
    return res


class ELF_NHdr():
    def __init__(
            self, n_namesz, n_descsz, n_type, endian=Endian.LittleEndian):
        self.note_header = struct.pack(endian + 'III',
                                       n_namesz, n_descsz, n_type)

    def get_header(self):
        return self.note_header


def bin_to_hex(note_bin, prefix, suffix, align):
        note_bin_str = ""
        for i, c in enumerate(note_bin, start=1):
            build_str = prefix + "{:02x}" + suffix
            note_bin_str += build_str.format(c)
            note_bin_str += "\n\t\t" if i % align == 0 else " "
        return note_bin_str


class Note_Section():
    def __init__(
            self, n_type, owner, desc, align=4, endian=Endian.LittleEndian):
        self.align = align
        self.desc = align_memory(desc, align)
        self.owner = align_memory(owner, align)
        self.desc = bytearray(self.desc.encode('ascii'))
        self.owner = bytearray(self.owner.encode('ascii'))
        len_owner = len(self.owner)
        len_desc = len(self.desc)
        self.note_header = ELF_NHdr(len_owner, len_desc, n_type, endian)
        self.note_section = self.note_header.get_header() \
            + struct.pack("{0}s".format(len_owner), self.owner) \
            + struct.pack("{0}s".format(len_desc), self.desc)

    def save(self, file_name):
        with open(file_name, "wb") as f:
            f.write(self.note_section)

    def save_c_code(self, file_name, alignment):
        c_code_text = "const unsigned char __attribute__((aligned("
        c_code_text += str(alignment)
        c_code_text += "), section(\".note.package\")))"
        c_code_text += " __attribute__((used))"
        c_code_text += " module_info_note_package[] = {"
        c_code_text += "\n\t\t"
        c_code_text += bin_to_hex(self.note_section, '0x', ', ', self.align)
        c_code_text += "};\n"

        c_code_encoded = c_code_text.encode('ascii')
        with open(file_name, "wb") as f:
            f.write(c_code_encoded)

    def get(self):
        return self.note_section


class LinkerScript():
    def __init__(
                self, section_name, note_bin='', memory_align=4):

        self.note_bin = note_bin
        self.section_name = section_name
        self.align = memory_align
        self.text = ""
        self.comment = ""
        self.script_text = ""

    def generate(self, readonly_flag=True):
        self.text += "SECTIONS\n{\n"
        self.text += "\t" + self.section_name
        if readonly_flag:
            self.text += " (READONLY)"
        self.text += " : ALIGN({})".format(self.align)
        self.text += "\n\t{\n\t\t"
        self.text += bin_to_hex(self.note_bin, 'BYTE(0x', ')', self.align)
        self.text += "\n\t\tKEEP (*(" + self.section_name + "))\n"
        self.text += "\t}\n"
        self.text += "}\n"
        self.text += "INSERT AFTER .note.gnu.build-id"
        self.text += ";"

    # Prints final linker scipt
    def display(self):
        print('=' * 80)
        print(self.text)
        print('=' * 80)

    def add_comment(self, comment):
        self.comment += "/*\n"
        self.comment += comment
        self.comment += "\n*/\n\n"

    def save(self, file_name):
        with open(file_name, "wb") as f:
            f.write(bytearray(self.comment.encode('ascii')))
            f.write(bytearray(self.text.encode('ascii')))


def generate_cpp_header(module_info, outdir):
    file_name = 'auto_module_info.h'
    if outdir:
        file_name = outdir + 'auto_module_info.h'
    cpp_header_content = """\
#ifndef _AUTO_MODULE_INFO_H_
#define _AUTO_MODULE_INFO_H_

#define MODULE_VERSION      \"{0}\"
#define PACKAGE_VERSION     \"{1}\"
#define PACKAGE_NAME        \"{2}\"
#define TARGET_OS           \"{3}\"
#define TARGET_OS_VERSION   \"{4}\"

#endif //_AUTO_MODULE_INFO_H_"""

    cpp_header_content = cpp_header_content.format(
                                        module_info['moduleVersion'],
                                        module_info['version'],
                                        module_info['name'],
                                        module_info['os'],
                                        module_info['osVersion'])
    with open(file_name, "wb") as f:
        f.write(bytearray(cpp_header_content.encode('ascii')))
    print(cpp_header_content)
    print("Generated {} file...\n".format(file_name))


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(
            "readable_dir:{} does not exist".format(path))


def parse_args():
    parser = argparse.ArgumentParser(
                description=DESCRIPTION,
                epilog=EPILOG,
                formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--name', required=True,
                        help='Package name.\n\n')

    parser.add_argument('--outdir', type=dir_path,
                        help='Folder to write .note.package.bin'
                        ', module_info.ld and header files.'
                        ' Both Windows or Linux paths are supported.\n\n')

    parser.add_argument('--version', required=True,
                        help='Package version.\n\n')

    parser.add_argument('--type',
                        choices=['bb', 'deb', 'rpm', 'agent', 'lib'],
                        help='Package/binary type. e.g. bb for bitbake,'
                        ' deb for debian packages. If a binary is from rpm'
                        ' and, it is an agent, please use \'agent\'.\n\n')

    parser.add_argument('--moduleVersion',
                        help='Module version. Consist of 4 parts version'
                        ' and each field is limited to 0-65535 range.\n\n')

    parser.add_argument('--os',
                        help='OS name. ID from /etc/os-release\n\n')

    parser.add_argument('--osVersion',
                        help='OS version. VERSION from /etc/os-release\n\n')

    parser.add_argument('--maintainer',
                        help='Maintainer information. '
                        'Internal service GUID or Maintainer e-mail.\n\n')

    parser.add_argument('--pkgid', help='package-system dependent identifier, '
                        'e.g. binutils-2.30-21ubuntu~18.04.4.\n\n')

    parser.add_argument('--repo', help='Repository name or address\n\n')
    parser.add_argument('--branch', help='Branch name\n\n')
    parser.add_argument('--copyright', help='Copyright information.\n\n')
    parser.add_argument('--hash', help='Git commit-id or hash.\n\n')
    parser.add_argument('--upstreamVersion', help='Upstream version in case'
                        ' internal and opensource versions don\'t match.\n\n')

    parser.add_argument('--endian', choices=['LittleEndian', 'BigEndian'],
                        default='LittleEndian',
                        help='Specifies if little endian or big endian. '
                        'The default is little-endian.\n'
                        'This is not part of note section payload.\n\n')

    parser.add_argument('--stamp', choices=['LinkerOnly', 'Mix'],
                        default='Mix',
                        help='Specifies note section stamping method. '
                        'The default is Mix, which generates C code and linker'
                        ' script and SELinux compliant. Linker script only '
                        'option may cause `execmem` SELinux issues. '
                        'this option is experimental for now.\n\n')
    try:
        return parser.parse_args()
    except:
        parser.format_usage()
        sys.exit(0)

if __name__ == '__main__':
    print("==== ELF note generator v{} ====".format(VERSION))
    args = parse_args()
    endian = Endian.map[args.endian]
    stamp_method = args.stamp

    delattr(args, 'outdir')
    delattr(args, 'endian')
    delattr(args, 'stamp')

    module_info = {
                    arg: getattr(args, arg) for arg in dir(args)
                    if getattr(args, arg) is not None and arg[0] != '_'
                  }

    desc_json = json.dumps(module_info, indent=1)
    note = Note_Section(N_TYPE, OWNER, desc_json, MEMORY_ALIGN, endian)

    if outdir:
        note.save(outdir + NOTE_SECTION_NAME + ".bin")
    else:
        note.save(NOTE_SECTION_NAME + ".bin")

    generated_files = ''
    if stamp_method == 'LinkerOnly':
        script = LinkerScript(NOTE_SECTION_NAME, note.get())
        script.add_comment(DO_NOT_EDIT_COMMENT)
        script.add_comment("".join(arg + ' ' for arg in sys.argv))
        script.add_comment(desc_json)
        script.generate()
        if outdir:
            script.save(outdir + OUTPUT_LINKER_SCRIPT_NAME)
        else:
            script.save(OUTPUT_LINKER_SCRIPT_NAME)
        generated_files += OUTPUT_LINKER_SCRIPT_NAME
    else:
        script = LinkerScript(NOTE_SECTION_NAME)
        script.add_comment(DO_NOT_EDIT_COMMENT)
        script.add_comment("".join(arg + ' ' for arg in sys.argv))
        script.add_comment(desc_json)
        script.generate(readonly_flag=False)
        if outdir:
            script.save(outdir + OUTPUT_LINKER_SCRIPT_NAME)
            note.save_c_code(outdir + C_MODULE_NAME, MEMORY_ALIGN)
        else:
            script.save(OUTPUT_LINKER_SCRIPT_NAME)
            note.save_c_code(C_MODULE_NAME, MEMORY_ALIGN)
        generated_files += OUTPUT_LINKER_SCRIPT_NAME + ", "
        generated_files += C_MODULE_NAME

    generate_cpp_header(module_info, outdir)
    print('Successfully generated {}'
          ' and {} files...'.format(
              generated_files,
              NOTE_SECTION_NAME))
