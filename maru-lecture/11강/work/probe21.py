import json, numpy as np, subprocess, re, mlx_whisper
exec(open("lead_probe.py").read().split("ns = ")[0].replace("import json, sys,", "import json, sys,"))
for c in np.arange(75.70, 76.40, 0.04):
    print(round(c, 2), tr(c, c + 1.2)[:8], "| 앞:", tr(c - 0.8, c)[-6:], flush=True)
