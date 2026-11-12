# 타임라인_초안.json → 타임라인_v1.json (11강 render_v3 형식: anchors · audio src/gain · 마지막 장 3.5초 유지)
import json
FPS = 30000 / 1001
def fr(t): return round(round(t * FPS) / FPS, 4)
t = json.load(open("../타임라인_초안.json"))
G = 10 ** ((-16.1 + 17.0) / 20); B = 10 ** ((-16.1 + 20.0) / 20)      # 클립 소리를 본문(−16.1 LUFS)에 맞춤 (ebur128 실측: 인삿말 −17.0 · 끝인사 −20.0)
gr = next(a for a in t["anchor"] if a["part"] == "인삿말"); by = next(a for a in t["anchor"] if a["part"].startswith("클로징"))
s25 = t["slides"][-1]
clip_t0 = round(by["out"] - by["clip_from"], 4)
bye_out = fr(clip_t0 + 21.021)                         # 클립 끝(손 모은 자세)
voice_end = round(clip_t0 + 19.642, 3)
end25 = fr(voice_end + 3.5)                            # 00강: 마지막 말 끝 → 엔딩 전환 3.5초 (11강 v3 와 같음)
t["anchors"] = [{"name": "인삿말", "in": 0.0, "clip": "../아나운서/14_인삿말_090.mp4", "clip_t0": 0.0},
                {"name": "끝인사", "in": s25["start"], "clip": "../아나운서/14_끝인사_090.mp4", "clip_t0": clip_t0, "out": bye_out}]
del t["anchor"]
t["audio"] = [{"slide": 1, "out": 0.0, "src_from": 0.0, "src_to": 18.323, "src": "아나운서/14_인삿말_090.wav", "gain": round(G, 3)}] + t["audio"] + \
             [{"slide": 25, "out": clip_t0, "src_from": 0.0, "src_to": 20.975, "src": "아나운서/14_끝인사_090.wav", "gain": round(B, 3)}]
s25.update(end=end25, voice_end=voice_end, gap_after_voice=round(end25 - voice_end, 3), src_offset=clip_t0); s25.pop("end_with_bye", None)
t["subs"][-1]["end"] = end25
T = end25
t["ending"] = {"zoom_blur": [T, round(T + 0.67, 4)], "card": [round(T + 0.67, 4), round(T + 8.80, 4)],
               "black": [round(T + 8.80, 4), round(T + 9.70, 4)], "logo_off": round(T + 1.17, 4)}
t["total"] = round(T + 9.70, 4)
t["params"]["v1"] = "끝인사 클립=25번 클로징(타입캐스트 클로징 안 씀) · 2번 아나운서 없음 · 클립 소리 게인 본문 LUFS 맞춤"
json.dump(t, open("../타임라인_v1.json", "w"), ensure_ascii=False, indent=1)
print("total", t["total"], "끝인사", t["anchors"][1], "gain", round(G, 3), round(B, 3))
