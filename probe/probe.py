import urllib.request, urllib.parse, re
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","Accept-Language":"zh-TW,zh;q=0.9"}
q=urllib.parse.quote("PS5 光碟版")
t=urllib.request.urlopen(urllib.request.Request(f"https://tw.buy.yahoo.com/search/product?p={q}",headers=UA),timeout=20).read().decode("utf-8","replace")
i=t.find('"ec_productid"')
j=t.rfind('{',0,i-1500)
print("Y RAW", t[i-2500:i+600].replace("\n"," "))
print("Y keys", sorted(set(re.findall(r'"(ec_[a-z_]+)"',t))))
