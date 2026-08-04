import re
t = open("dark.svg", encoding="utf-8").read()
m = re.search(r'<g class="band">.*?<animate attributeName="opacity" values="([^"]+)" keyTimes="([^"]+)"', t, re.S)
print("opacity values:", m.group(1))
print("keyTimes:", m.group(2))
m2 = re.search(r'<animateTransform attributeName="transform" type="translate" values="([^"]+)" keyTimes="([^"]+)"', t, re.S)
print("translate values:", m2.group(1)[:220])
print("tr keyTimes:", m2.group(2))
# find all distinct logo-ish translate targets near frame box
f = re.findall(r'type="translate" values="([^"]+)"', t)
print("total translate anims:", len(f))
from collections import Counter
print("distinct:", Counter(f).most_common(8))
i = t.find('<g class="band"')
j = t.find('</g>', i)
print(t[i:i+1500])
