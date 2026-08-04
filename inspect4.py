import re
t = open("dark.svg", encoding="utf-8").read()
i = t.find('<g class="trav"')
j = t.find('</g>', i)
print("TRAV GROUP:", t[i:i+1200])
print()
# also band transform targets distribution - how far do they go
vals = re.findall(r'type="translate" values="0 0;([^;]+);0 0"', t)
import numpy as np
xs = [float(v.split()[0]) for v in vals]
ys = [float(v.split()[1]) for v in vals]
print("band translate dx: min", min(xs), "max", max(xs), "mean", np.mean(xs))
print("band translate dy: min", min(ys), "max", max(ys), "mean", np.mean(ys))
