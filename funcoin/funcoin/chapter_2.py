import hashlib

# Hash functions expect bytes as input: the encode() method turns strings to bytes
input_bytes = b"dan"

output = hashlib.sha256(input_bytes)

#We used hexdigest() to convert bytes to hex because it's easier to read
print(output.hexdigest())

#-try nackit, token, noborders, nolines, nolimit, nonaira
name = ""

print(name[::-1])