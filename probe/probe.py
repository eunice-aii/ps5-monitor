import urllib.request, urllib.parse, re, json
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","Accept-Language":"zh-TW,zh;q=0.9","Accept":"application/json, text/plain, */*"}
def get(u,h=None):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={**UA,**(h or {})}),timeout=20)
        return r.status, r.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
C=urllib.parse.quote("-NeqTSgDQOAYi30lg4a7:inline-live-3"); B="-NeqTStJZDIBQHEMSDI8"
ref={"Referer":f"https://inline.app/booking/-NeqTSgDQOAYi30lg4a7:inline-live-3/{B}","Origin":"https://inline.app"}
s,t=get(f"https://inline.app/api/booking-capacitiesV3?companyId={C}&branchId={B}",ref); print("INLINE",s,t[:400].replace("\n"," "))
s,t=get(f"https://inline.app/booking/-NeqTSgDQOAYi30lg4a7:inline-live-3/{B}"); print("INLINEPAGE",s,len(t),t[:300].replace("\n"," "))
for rid in ("17565","17800"):
    s,t=get(f"https://tw.eztable.com/restaurant/{rid}"); print("EZ",rid,s,len(t))
    for m in set(re.findall(r'https://[a-z0-9.-]*eztable[a-z0-9.-]*/[a-zA-Z0-9/_.-]*(?:api|availab|quota|booking)[a-zA-Z0-9/_.?=&-]*',t)): print("EZ url",m)
