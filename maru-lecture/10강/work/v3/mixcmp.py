import sys, numpy as np, subprocess as sp
r = lambda f: np.frombuffer(sp.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 's16le', '-'], capture_output=True).stdout, np.int16).astype(int)
a, b = r(sys.argv[1]), r(sys.argv[2]); print('mix 길이', len(a), len(b), '최대차', abs(a - b).max() if len(a) == len(b) else '길이다름')
