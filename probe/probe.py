import urllib.request, re, json
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","Accept-Language":"zh-TW,zh;q=0.9"}
def get(u):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=20); return r.status,r.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e: return e.code,e.read().decode("utf-8","replace")
s,t=get("https://www.acergaming.com/products/PlayStation5"); print("AG",s,len(t))
for kw in ["shopline","SHOPLINE","app.value","__NEXT_DATA__","productList","products_json","window.mainConfig","sold_out","quantity","unlimited_quantity","api/","光碟"]:
    i=t.find(kw); print("AG",kw,t.count(kw), t[max(0,i-150):i+300].replace("\n"," ") if i>=0 else "")
for m in sorted(set(re.findall(r'href="(/products/[^"#?]+)"',t)))[:60]: print("AG link",m)
