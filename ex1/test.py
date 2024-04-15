import hashlib

groupid = b"hhhhhh"

with open("ergebnispins.txt", "r") as file:
    pins = file.read().strip()


data = groupid + pins.encode('utf-8')

hashed = hashlib.sha224(data).hexdigest()

print(hashed)
