import re, collections
t = open("../efec3e8_dark.svg", "rb").read().decode("utf-16")
print(len(t.encode()) // 1024, "KB")
print(collections.Counter(re.findall(r'class="(\w+)"', t)).most_common(10))
v = re.findall(r'type="translate" values="([^"]+)"', t)
print("translate anims:", len(v))
print("distinct:", len(set(v)))
