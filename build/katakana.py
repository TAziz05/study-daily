"""Katakana practice questions: single kana, dakuten, combinations, loanwords and spelling."""
import random

BASIC = """ア a|イ i|ウ u|エ e|オ o|カ ka|キ ki|ク ku|ケ ke|コ ko|サ sa|シ shi|ス su|セ se|ソ so|タ ta|チ chi|ツ tsu|テ te|ト to|
ナ na|ニ ni|ヌ nu|ネ ne|ノ no|ハ ha|ヒ hi|フ fu|ヘ he|ホ ho|マ ma|ミ mi|ム mu|メ me|モ mo|ヤ ya|ユ yu|ヨ yo|
ラ ra|リ ri|ル ru|レ re|ロ ro|ワ wa|ヲ o (wo)|ン n"""
DAKU = """ガ ga|ギ gi|グ gu|ゲ ge|ゴ go|ザ za|ジ ji|ズ zu|ゼ ze|ゾ zo|ダ da|デ de|ド do|
バ ba|ビ bi|ブ bu|ベ be|ボ bo|パ pa|ピ pi|プ pu|ペ pe|ポ po"""
COMBO = """キャ kya|キュ kyu|キョ kyo|シャ sha|シュ shu|ショ sho|チャ cha|チュ chu|チョ cho|ニャ nya|ニュ nyu|ニョ nyo|
ヒャ hya|ヒュ hyu|ヒョ hyo|ミャ mya|ミュ myu|ミョ myo|リャ rya|リュ ryu|リョ ryo|ギャ gya|ギュ gyu|ギョ gyo|
ジャ ja|ジュ ju|ジョ jo|ビャ bya|ビュ byu|ビョ byo|ピャ pya|ピュ pyu|ピョ pyo|
ファ fa|フィ fi|フェ fe|フォ fo|ティ ti|ディ di|トゥ tu|ドゥ du|ウィ wi|ウェ we|ウォ wo|シェ she|ジェ je|チェ che|ヴァ va"""

def parse(s):
    return [tuple(x.strip().split(" ", 1)) for x in s.replace("\n", "").split("|") if x.strip()]

# characters people commonly mix up
LOOK = [set("シツ"), set("ソン"), set("ソリ"), set("ンシ"), set("クケタ"), set("スヌ"), set("ウワフ"),
        set("チテ"), set("コユロ"), set("マア"), set("ルレ"), set("ナメ"), set("セサ"), set("ヲラ"),
        set("ノメ"), set("ハル"), set("エニ"), set("トナ"), set("ヤセ"), set("ホオ")]

def lookalikes(ch):
    out = []
    for g in LOOK:
        if ch in g:
            out += [c for c in g if c != ch and c not in out]
    return out

LOANWORDS = """テレビ|television
コーヒー|coffee
パン|bread
カメラ|camera
ホテル|hotel
レストラン|restaurant
コンピューター|computer
アイスクリーム|ice cream
ハンバーガー|hamburger
スーパー|supermarket
コンビニ|convenience store
アルバイト|part-time job
パーティー|party
シャツ|shirt
セーター|sweater
ネクタイ|necktie
スマホ|smartphone
ノート|notebook
ペン|pen
ジュース|juice
ビール|beer
ケーキ|cake
チーズ|cheese
バター|butter
サラダ|salad
スープ|soup
ピザ|pizza
チョコレート|chocolate
タクシー|taxi
バス|bus
トイレ|toilet
シャワー|shower
ベッド|bed
ソファ|sofa
テーブル|table
ドア|door
エレベーター|elevator
エアコン|air conditioner
カレンダー|calendar
ニュース|news
メール|email
インターネット|internet
ゲーム|game
スポーツ|sports
サッカー|soccer
テニス|tennis
ギター|guitar
ピアノ|piano
コンサート|concert
チケット|ticket
デパート|department store
アパート|apartment
マンション|condominium
ポスト|mailbox
ガソリン|gasoline
ハンカチ|handkerchief
スプーン|spoon
フォーク|fork
ナイフ|knife
コップ|cup; glass
ティッシュ|tissue
ソーセージ|sausage
ステーキ|steak
クラス|class
テスト|test
レポート|report; paper
キャンパス|campus
アメリカ|America
フランス|France
ドイツ|Germany
イタリア|Italy
カナダ|Canada
メキシコ|Mexico
オーストラリア|Australia
ロンドン|London
ニューヨーク|New York
クリスマス|Christmas
プレゼント|present; gift
ボールペン|ballpoint pen
ファッション|fashion
ウィンドウ|window (computer)
ディズニー|Disney
チェック|check
シェフ|chef
ジェットコースター|roller coaster
キャンプ|camping
ジョギング|jogging
ミュージック|music
ショッピング|shopping
ヴァイオリン|violin
"""

def variants(word, rng):
    """Plausible misspellings of a katakana word."""
    out = set()
    chars = list(word)
    for i, c in enumerate(chars):
        for alt in lookalikes(c):
            out.add("".join(chars[:i] + [alt] + chars[i + 1:]))
    if "ー" in word:
        out.add(word.replace("ー", "", 1))
    else:
        for i, c in enumerate(chars[:-1]):
            if c not in "ッャュョァィゥェォー":
                out.add("".join(chars[:i + 1] + ["ー"] + chars[i + 1:]))
                break
    if "ッ" in word:
        out.add(word.replace("ッ", "", 1))
        out.add(word.replace("ッ", "ツ", 1))
    for small, big in zip("ャュョァィェォ", "ヤユヨアイエオ"):
        if small in word:
            out.add(word.replace(small, big, 1))
    out.discard(word)
    out = sorted(out)
    rng.shuffle(out)
    return out


def questions():
    rng = random.Random(7)
    out = []
    G = dict(k="kana", g="Kana", L="Katakana")

    def kana_set(rows, topic, label):
        roms = [r for _, r in rows]
        for kana, rom in rows:
            look = [k for k in lookalikes(kana) if k in dict(rows)] if len(kana) == 1 else []
            # reading
            pool = [dict(rows)[k] for k in look] + [r for r in roms if r != rom and r not in [dict(rows)[k] for k in look]]
            near = pool[:len(look)] + sorted(pool[len(look):], key=lambda r: (r[0] != rom[0] and r[-1] != rom[-1], rng.random()))
            w = []
            for r in near:
                if r != rom and r not in w:
                    w.append(r)
            out.append(dict(G, T=topic, t="Katakana – " + topic, s="Katakana chart" + label,
                            q=f"How do you read 「{kana}」?", a=rom, w=w[:3],
                            e=f"{kana} is read “{rom}”." + (f" Don't mix it up with {'、'.join(look)}." if look else "")))
            # writing
            others = [k for k, _ in rows if k != kana]
            cands = look + sorted([k for k in others if k not in look], key=lambda k: (dict(rows)[k][-1] != rom[-1], rng.random()))
            out.append(dict(G, T=topic, t="Katakana – " + topic, s="Katakana chart" + label,
                            q=f"Which katakana is “{rom}”?", a=kana, w=cands[:3],
                            e=f"“{rom}” is written {kana}." + (f" Look-alikes: {'、'.join(look)}." if look else "")))

    kana_set(parse(BASIC), "Basic katakana", "")
    kana_set(parse(DAKU), "Dakuten ゛ and handakuten ゜", " (゛゜)")
    kana_set(parse(COMBO), "Combinations (ャュョ, ファ, ティ…)", " (combinations)")

    words = [tuple(l.split("|")) for l in LOANWORDS.strip().splitlines()]
    meanings = [m for _, m in words]
    for i, (kw, m) in enumerate(words):
        w = [x for x in rng.sample(meanings, 8) if x != m][:3]
        out.append(dict(G, T="Loanwords", t="Katakana – Loanwords", s="Katakana loanwords",
                        q=f"What does the katakana word 「{kw}」 mean?", a=m, w=w,
                        e=f"{kw} = {m}."))
        v = variants(kw, rng)
        if len(v) >= 3:
            out.append(dict(G, T="Spot the right spelling", t="Katakana – Spelling", s="Katakana loanwords",
                            q=f"Which is the correct katakana for “{m}”?", a=kw, w=v[:3],
                            e=f"“{m}” is {kw}. Watch for look-alike characters, long vowels (ー) and small ッ/ャ/ュ/ョ."))
    return out
