import urllib.request, urllib.parse, re
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","Accept-Language":"zh-TW,zh;q=0.9","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
q=urllib.parse.quote("PS5 光碟版")
for u in [f"https://www.tw.coupang.com/search?q={q}", f"https://www.tw.coupang.com/np/search?q={q}", "https://www.tw.coupang.com/"]:
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=20); t=r.read().decode("utf-8","replace")
        print("CP",r.status,len(t),u)
        for m in list(re.finditer(r"PS5[^<>\"]{0,80}",t))[:6]: print("CP ..",re.sub(r"\s+"," ",t[m.start():m.start()+250]))
        for kw in ["__NEXT_DATA__","productId","salePrice","soldOut","outOfStock","captcha","Access Denied"]: print("CP has",kw,t.count(kw))
    except urllib.error.HTTPError as e: print("CP ERR",e.code,u,e.read()[:200])
    except Exception as e: print("CP ERR",u,e)
