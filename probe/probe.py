import urllib.request, urllib.parse, re, json
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","Accept-Language":"zh-TW,zh;q=0.9"}
def get(u,h=None):
    r=urllib.request.urlopen(urllib.request.Request(u,headers={**UA,**(h or {})}),timeout=20)
    return r.status, r.read().decode("utf-8","replace")
C="-NeqTSgDQOAYi30lg4a7:inline-live-3"; B="-NeqTStJZDIBQHEMSDI8"
for u in [f"https://inline.app/api/booking-capacitiesV3?companyId={urllib.parse.quote(C)}&branchId={B}",
          f"https://inline.app/api/booking-capacities?companyId={urllib.parse.quote(C)}&branchId={B}"]:
    try:
        s,t=get(u); print("INLINE",s,len(t),u[:60]); 
        try:
            d=json.loads(t); print("INLINE keys", list(d)[:10] if isinstance(d,dict) else type(d))
            for k in ("2026-11-28","2026-12-05"):
                def find(o,path=""):
                    if isinstance(o,dict):
                        for kk,v in o.items():
                            if kk==k: print("INLINE",path+"/"+kk, json.dumps(v,ensure_ascii=False)[:800])
                            else: find(v,path+"/"+kk)
                find(d)
            print("INLINE sample", t[:600])
        except Exception as e: print("INLINE notjson", t[:300])
    except Exception as e: print("INLINE ERR",u[:60],e)
try:
    s,t=get("https://www.feastogether.com.tw/booking/Inparadise"); print("FEAST",s,len(t))
    js=re.findall(r'src="([^"]+\.js)"',t); print("FEAST js",js[:10])
    for j in js[:8]:
        jj=j if j.startswith("http") else "https://www.feastogether.com.tw"+j
        try:
            _,code=get(jj)
            apis=set(re.findall(r'["\'`](https?://[a-zA-Z0-9.-]*feastogether[^"\'`]*|/api/[A-Za-z0-9/_-]+)["\'`]',code))
            if apis: print("FEAST api in",j, sorted(apis)[:60])
        except Exception as e: print("FEAST jsERR",j,e)
except Exception as e: print("FEAST ERR",e)
