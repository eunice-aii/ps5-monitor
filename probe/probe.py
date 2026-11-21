import urllib.request, urllib.parse, re, json, html
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","Accept-Language":"zh-TW,zh;q=0.9"}
q=urllib.parse.quote("PS5 光碟版")
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=20).read().decode("utf-8","replace")
t=get(f"https://tw.buy.yahoo.com/search/product?p={q}")
m=re.search(r'id="gqlstate-data"[^>]*>(.*?)</script>',t,re.S)
print("Y gql found", bool(m))
if m:
    raw=m.group(1)
    try: d=json.loads(raw)
    except Exception: d=json.loads(html.unescape(raw))
    found=[]
    def walk(o):
        if isinstance(o,dict):
            if "ec_productid" in o: found.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o,list):
            for v in o: walk(v)
    walk(d)
    print("Y items",len(found))
    if found:
        print("Y keys", sorted(found[0].keys()))
        for f in found[:15]:
            print("Y", {k:f.get(k) for k in f if k in("ec_productid","ec_title","ec_name","ec_price","ec_final_price","ec_has_stock","ec_saleprice","ec_item_url")})
e=get(f"https://www.etmall.com.tw/Search?keyword={q}")
srcs=re.findall(r'src="(/Resource/Bundle/Search[^"]+)"',e)
print("E srcs",srcs)
for s in srcs:
    js=get("https://www.etmall.com.tw"+s)
    for mm in set(re.findall(r'["\'](/[A-Za-z]+/[A-Za-z/]*(?:Search|Goods|Product)[A-Za-z/]*)["\']',js)): print("E url",mm)
i=e.find('"Title"'); print("E title ctx", e[max(0,i-400):i+600].replace("\n"," "))
