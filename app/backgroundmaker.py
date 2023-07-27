a = "✯✓▰☀♫"
c = 4
b = [[""] * c] * c
for k in range(3):
    for i in b:
        print(i,"|", i,"|", i)
    print(("-"*4*c+' ')*3)
b = ['✓', '▰', '♫', '✯', "☀"]
for l in range(3):
        for i in range(len(b)-1,-1,-1):
            k = b[i:] + b[:i]
            print(k,k,k)
print("-"*128)

for i in range(len(b)):
    k = b[i:] + b[:i]
    for i in k:
        print(i + " "*((len(b)-2)*4), end = "")
    print("\n" *(len(b)-2))