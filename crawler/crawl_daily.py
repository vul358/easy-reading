import re
import redis
import requests
from bs4 import BeautifulSoup
import json
from opencc import OpenCC
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from build_index import es


r = redis.Redis(host="localhost", port=6379, decode_responses=True) 
yesterday_tw = (datetime.utcnow() - timedelta(hours=16)).date()
cc = OpenCC("s2twp")


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Accept-Encoding":"gzip, deflate",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT":"1",
    "Connection": "close",
    "Upgrade-Insecure-Requests":"1"
}


class StopCrawling(Exception):
    pass


def get_content(url):
    response = requests.get(url, headers=headers)
    print(f"{response.status_code=}")
    if response.status_code == 503:
        print(response.content)
    return response.content


def crawler_sto(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    try:
        # crawl novel
        list_body = soup.select(".slistbody")
        print(len(list_body))
        for body in list_body:
            # crawl title and author
            sto = "https://www.sto.cx"
            title_author = body.select(".t")[0].text.strip()
            title, author = re.findall(r"《(.*)》作者：([^\(]+)", title_author)[0]
            title_tw = cc.convert(title)
            author_tw = cc.convert(author)
            print(title_tw, author_tw)
            # get content if not empty
            content = body.select(".i a")
            if content:
                intro = content[0].get("onclick")
            # crawl complete outline
                intro_url = re.findall(r"content: "(.*)}", intro)[0].strip(""")
                outline_raw = BeautifulSoup(get_content(sto+intro_url),"lxml").select("body")[0].text.strip()
                h3 = BeautifulSoup(get_content(sto+intro_url),"lxml").find("h3").text.strip()
                outline = outline_raw.strip("立即阅读").strip(h3)
                outline_tw = cc.convert(outline)
                # get tags
                match = re.search(r"內容標籤：(.*)主角：", outline_tw)
                match_2 = re.search(r"內容標簽：(.*)主角：", outline_tw) 
                if match:
                    tags = match.group(1).strip()
                elif match_2:
                    tags = match_2.group(1).strip()
                else:
                    tags = ""
                print(f"有詳細介紹，tags:{tags}")
            else:
                outline = body.select(".i")[0].text.strip()
                outline_tw = cc.convert(outline)
                tags = ""
                print(f"無詳細介紹")
            # crawl year
            year = int(re.findall(r"Time：(\d+)年", body.select(".b")[0].text.split()[0])[0])
            # crawl date
            date_text = body.select(".b")[0].text.split()[0].strip("Time：")
            date = datetime.strptime(date_text, "%Y年%m月%d日").strftime("%Y-%m-%d")
            # crawl category
            category = body.select(".b")[0].text.split()[1].strip("Class：")
            category_tw = cc.convert(category)
            # crawl size
            size = int(body.select(".b")[0].text.split()[2].strip("Size：").strip("k"))
            # crawl url
            url = body.select_one(".t a")["href"]
            novel_url = sto + url
            # crawl comments number
            try:
                novel_id = re.findall(r"book-(\d+)-", novel_url)[0]
            except:
                novel_id = re.findall(r"bid=(\d+)&", novel_url)[0]
            comment_url = "https://www.sto.cx/User/comment.aspx?id="+ novel_id
            comment_text = BeautifulSoup(get_content(comment_url),"lxml").select(".comtLT .fr")[0].text.strip()
            comment_num = int(re.findall(r"共(\d+)條", comment_text)[0].strip())
            print(f"評論數量：{comment_num}")
            body = {
            "title": title_tw,
            "author": author_tw,
            "outline": outline_tw,
            "category": category_tw,
            "tags": tags,
            "year": year,
            "url": novel_url,
            "website": "sto",
            "size": size,
            "comment": comment_num,
            "date": date,
            } 
            novel = title_tw + author_tw 
            print(novel)
            # only insert yesterday's new novels into DB daily
            if r.get(f"{novel}") is None:
                r.set(f"{novel}", f"{url}")
                novel_date = datetime.strptime(date,"%Y-%m-%d").date()
                print(novel_date)
                if novel_date > yesterday_tw:
                    pass
                elif novel_date == yesterday_tw:
                    es.index(index="sto_novels_info", body = body)
                    print(f"{date}-{category}-進入資料庫")
                else:
                    raise StopCrawling
        last_page = soup.select(".paginator a")[-1].attrs.get("disabled")
        if last_page:
            has_next_page = False
        else:
            has_next_page = True
    except Exception as e:
        print(e)
        return None
    else:
        return {"has_next_page": has_next_page}


def get_sto_category(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    try:
        categories_links = soup.select("#showClass a")
        sto = "https://www.sto.cx"
        links = []
        for link in categories_links:
            href = link["href"]  
            url = sto + href
            links.append(url)
        return links
    except Exception as e:
        print(e)


def get_sto_page_url():
    start_page = "https://www.sto.cx/sbn.aspx?c=0"
    links = get_sto_category(get_content(start_page))
    for link in links:
        i = 1
        while True:
            page_url = f"{link}&page={i}"
            result = crawler_sto(get_content(page_url))
            if result and result["has_next_page"]:
                i += 1
            else:
                break


if __name__ == "__main__":
    get_sto_page_url()
    r.flushdb() 
