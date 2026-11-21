import urllib.request, urllib.parse, re, json
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","Accept-Language":"zh-TW,zh;q=0.9"}
q=urllib.parse.quote("PS5 光碟版")
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=20).read().decode("utf-8","replace")
t=get(f"https://tw.buy.yahoo.com/search/product?p={q}")
m=re.search(r'<script type="application/ld\+json"[^>]*>(.*?)</script>',t,re.S)
print("YAHOO LD:", m.group(1)[:1500] if m else None)
m=re.search(r'window\.(__\w+)\s*=',t); print("YAHOO var", m.group(1) if m else None, t[m.start():m.start()+200] if m else "")
for kw in ['"isSoldOut"','soldOut','"price"','"ec_productid"','"productId"','"title"']:
    i=t.find(kw); print("Y",kw,t.count(kw), t[max(0,i-200):i+250].replace("\n"," ") if i>=0 else "")
e=get(f"https://www.etmall.com.tw/Search?keyword={q}")
for kw in ['FinalPrice','"Title"','"GoodId"','Goods','SoldOut','IsSoldOut','api/','ajax','/Search/']:
    i=e.find(kw); print("E",kw,e.count(kw), e[max(0,i-150):i+250].replace("\n"," ") if i>=0 else "")
