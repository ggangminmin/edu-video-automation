import sys; sys.path.insert(0, "v3"); from voice import *
for arg in sys.argv[1:]:
    a, b = map(float, arg.split(":"))
    print(arg, " ".join(f"{j/FR:.3f}:{db[j]:.0f}" for j in range(int(a*FR), int(b*FR))))
    print(" pauses", pauses(a, b), "\n")
