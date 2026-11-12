# 공통: 지금 폴더(NN강/work)에서 강 번호 N
import os, re, unicodedata as u
N = int(re.search(r"(\d+)강", u.normalize("NFC", os.getcwd().split("/")[-2])).group(1))
