from hashlib import sha256

x = 5
y = 0 # We don't know what y shold be yet...

while sha256(f'{x*y}'.encode()).hexdigest()[-1] != "b":
    y+=1
    
print(f'The solution is y = {y}')