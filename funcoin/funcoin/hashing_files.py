from hashlib import sha256

file = open("my_image_1.png", "rb")
hash = sha256(file.read()).hexdigest()
file.close()

print(f"The hash of my file is: {hash}")