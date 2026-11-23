import urllib.request, re
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","Accept-Language":"zh-TW,zh;q=0.9"}
t=urllib.request.urlopen(urllib.request.Request("https://www.acergaming.com/products/PS5",headers=UA),timeout=20).read().decode("utf-8","replace")
cards=t.split('<div class="productItem')[1:]
print("AG ncards",len(cards))
for c in cards:
    c=re.sub(r"\s+"," ",c)[:6000]
    name=re.search(r'<h3 class="d-none">([^<]*)</h3>',c)
    if name and ("光碟版主機" in name.group(1) or "金鋼狼" in name.group(1)):
        i=c.find('data-price') if 'data-price' in c else c.find('35860')
        print("AG RAW", name.group(1), "::", re.sub(r'<(svg|path|img)[^>]*>','',c)[-2500:])
