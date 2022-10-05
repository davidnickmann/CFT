from pwn import *

host = 'chal.imaginaryctf.org'
port = 42050

io = remote(host, port)

for i in range(200):
    io.recvuntil(b'Your lucky number is: ')
    key = int(p.recvuntil(b'\n'))
    key = key + 10000000000
    key = int(key) ^ 1337
    key = list(str(key))
    chars = ''
    for x in range(0, len(key), 2):
        chars += chr(int(''.join(key[x:x + 2])))
    info((chars))
    io.sendlineafter(b'? ', chars.encode())
io.interactive()
