import re
t = open("dark.svg", encoding="utf-8").read()
# each traveler: cx values at keyTimes 0.000;0.180;0.260;0.420;0.500;0.660;0.740
# structure: photo,photo,logo1,logo1,logo2,logo2,photo  (0.26-0.42 logo1, 0.50-0.66 logo2)
cxs = re.findall(r'<animate attributeName="cx" values="([^"]+)"', t)
print("num cx anims:", len(cxs))
# collect logo1 targets (index 2) and logo2 targets (index 4)
l1x, l1y, l2x, l2y = [], [], [], []
cys = re.findall(r'<animate attributeName="cy" values="([^"]+)"', t)
for cx, cy in zip(cxs, cys):
    a = cx.split(";"); b = cy.split(";")
    l1x.append(float(a[2])); l1y.append(float(b[2]))
    l2x.append(float(a[4])); l2y.append(float(b[4]))
print("logo1 targets x range:", min(l1x), max(l1x), "y:", min(l1y), max(l1y))
print("logo2 targets x range:", min(l2x), max(l2x), "y:", min(l2y), max(l2y))
# count distinct clusters: quantize
import numpy as np
print("logo1 mean pos:", np.mean(l1x), np.mean(l1y))
print("logo2 mean pos:", np.mean(l2x), np.mean(l2y))
# same for all? check std
print("logo1 x std:", np.std(l1x), "y std:", np.std(l1y))
print("logo2 x std:", np.std(l2x), "y std:", np.std(l2y))
