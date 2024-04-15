import hashlib

groupid = b"12349876"

print(hashlib.sha224(groupid).hexdigest())
