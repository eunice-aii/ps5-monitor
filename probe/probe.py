import urllib.request, re
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","Accept-Language":"zh-TW,zh;q=0.9"}
def get(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=20); return r.read().decode("utf-8","replace")
t=get("https://www.acergaming.com/products/PS5")
print("AG len",len(t))
for m in list(re.finditer(r'<h3 class="d-none">([^<]*)</h3>',t))[:40]:
    blk=re.sub(r"\s+"," ",t[m.start():m.start()+3500])
    blk=re.sub(r'<(svg|path)[^>]*>','',blk)
    txt=re.sub(r"<[^>]+>"," | ",blk); txt=re.sub(r"(\s*\|\s*)+"," | ",txt)
    print("AG CARD", m.group(1), "::", txt[:500])
d=get("https://www.acergaming.com/product/detail/ZL.A00TZ.1PO?category=PlayStation5")
for kw in ["售完","缺貨","補貨","加入購物車","立即購買","到貨通知","price","NT$","$"]:
    i=d.find(kw); print("AG D",kw,d.count(kw), re.sub(r"\s+"," ",d[max(0,i-200):i+200]) if i>=0 else "")
