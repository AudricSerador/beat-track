import time
bruh = []
elapsed = 0
start = time.time()
count = 0
for i in range(10000):
    elapsed = time.time() - start
    print(f"{count}: {elapsed}")
    count += 1
