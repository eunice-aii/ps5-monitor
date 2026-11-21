import urllib.request, urllib.parse, re, json
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","Accept-Language":"zh-TW,zh;q=0.9"}
kw="PS5 光碟版"
q=urllib.parse.quote(kw)
urls={
 "momo_www":f"https://www.momoshop.com.tw/search/searchShop.jsp?keyword={q}",
 "momo_m":f"https://m.momoshop.com.tw/search.momo?searchKeyword={q}",
 "yahoo":f"https://tw.buy.yahoo.com/search/product?p={q}",
 "books":f"https://search.books.com.tw/search/query/key/{q}/cat/all",
 "etmall":f"https://www.etmall.com.tw/Search?keyword={q}",
 "tkec":f"https://www.tk3c.com/search.aspx?keyword={q}",
 "shopee":f"https://shopee.tw/api/v4/search/search_items?keyword={q}&limit=20",
 "sony":"https://store.sony.com.tw/product/show/ff8080818a8e1bc8018b0283e5bb0a55",
 "rakuten":f"https://www.rakuten.com.tw/search/{q}/",
}
for k,u in urls.items():
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=20)
        t=r.read().decode("utf-8","replace")
        print(f"=== {k} {r.status} len={len(t)}")
        for m in list(re.finditer(r"PS5[^<>\"]{0,60}光碟[^<>\"]{0,60}",t))[:4]:
            s=m.start(); print("  ..", re.sub(r"\s+"," ",t[s:s+300])[:300])
        for key in ["__NEXT_DATA__","goodsCode","i_code","prdPrice","window.__","application/ld+json","price"]:
            if key in t: print("  has",key, t.count(key))
    except Exception as e:
        print(f"=== {k} ERR {e}")
