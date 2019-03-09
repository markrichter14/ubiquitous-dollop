fn = 'misc/show_list.txt'

max_len = -float('inf')
with open(fn, 'r') as f:
    r = f.readlines()

for l in r:
    n = l.strip()
    print(n, len(n), max_len)
    if len(n) > max_len:
        max_len = len(n)

print(max_len)



