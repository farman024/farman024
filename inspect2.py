import re
t = open("dark.svg", encoding="utf-8").read()
# top-level structure
groups = re.findall(r'<g class="([^"]+)"', t)
from collections import Counter
print("class counts:", Counter(groups).most_common(15))
# all translate values (sample to see if any target logo clusters)
vals = re.findall(r'type="translate" values="([^"]+)"', t)
print("num translate anims:", len(vals))
# check for other opacity-driven groups (logo layers)
op = re.findall(r'<animate attributeName="opacity" values="([^"]+)" keyTimes="([^"]+)" dur="14.2s"', t)
print("opacity cycles:", Counter(op).most_common(10))
# svg size / viewbox
print("svg head:", t[:300])
