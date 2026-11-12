# 받아쓰기 숫자 ↔ 자막 한글 읽기 대조용(11/3 팀장 · 11강 p1T resplit_v7.py 에서 옮김)
#  mlx 받아쓰기는 「10에서 15mm」처럼 숫자·단위로 적고 자막(메모)은 「십에서 십오 밀리미터」 → 글자 짝짓기(difflib)가 안 맞아 단어 시각을 못 찾음.
#  kor(w) = 대조할 때만 받아쓰기 쪽을 한자어 읽기로 바꿈(자막 글자는 절대 안 바꿈). 사용: sys.path.insert(0, "<_작업>/오더09_공용"); from num_read import kor
import re
def sino(n):
    D = "영일이삼사오육칠팔구"; n = int(n)
    if n == 0: return "영"
    out = ""
    for v, u in ((1000, "천"), (100, "백"), (10, "십")):
        k = n // v; n %= v
        if k: out += ("" if k == 1 else D[k]) + u
    return out + (D[n] if n else "")
def kor(w):
    w = re.sub(r"(?i)mm", "밀리미터", w); w = re.sub(r"(?i)cm", "센티미터", w)
    return re.sub(r"\d+", lambda m: sino(m.group()), w)
if __name__ == "__main__":
    for t in ["10에서", "15mm", "25", "120cm", "3"]: print(t, "→", kor(t))
