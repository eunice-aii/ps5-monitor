import urllib.request, re
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","Accept-Language":"zh-TW,zh;q=0.9"}
d=urllib.request.urlopen(urllib.request.Request("https://www.acergaming.com/product/detail/ZL.A00TZ.1PO?category=PS5",headers=UA),timeout=20).read().decode("utf-8","replace")
d1=re.sub(r"\s+"," ",d)
for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>',d1): print("AG LD", m.group(1)[:1500])
for kw in ["availability","InStock","OutOfStock","stock","Stock","庫存","售完","完售","已售","缺貨","暫無","補貨","購物車","cart","Cart","buyButton","btn-buy","disabled","url:","ajax","fetch("]:
    idx=[m.start() for m in re.finditer(re.escape(kw),d1)][:3]
    for i in idx: print("AG",kw,"::",d1[max(0,i-200):i+250])
