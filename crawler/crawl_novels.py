import re
import redis
import requests
from bs4 import BeautifulSoup
import json
from opencc import OpenCC
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from build_index import es

r = redis.Redis(host='localhost', port=6379, decode_responses=True) 
# r.flushdb() 


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Accept-Encoding":"gzip, deflate",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT":"1",
    "Connection": "close",
    "Upgrade-Insecure-Requests":"1"
}


def get_content(url):
    response = requests.get(url, headers=headers)
    print(f'{response.status_code=}')
    if response.status_code == 503:
        print(response.content)
    return response.content


def get_jjwxc_novels(category_url):
    html_content = get_content(category_url)
    soup = BeautifulSoup(html_content, 'lxml')
    try:
        novel_links = soup.select('a[href*="onebook.php?novelid="]')
        print(len(novel_links))
        jjwxc = "https://www.jjwxc.net/"
        for link in novel_links:
            href = link['href']  # 提取href属性
            url = jjwxc + href
            body = crawler_jjwxc(url)
            es.index(index='novels_info', body = body)
        #print(links[0])
        return "Done"
    except Exception as e:
        print(e)


def get_jjwxc_categories(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    try:
        categories_links = soup.select('#navbar a')
        jjwxc = "https://www.jjwxc.net/"
        links = []
        for link in categories_links:
            href = link['href']  # 提取href属性
            url = jjwxc + href
            links.append(url)
        print(links)
        return links
    except Exception as e:
        print(e)


cc = OpenCC('s2twp')


def crawler_jjwxc(url):
    soup = BeautifulSoup(get_content(url), 'lxml')
    try:
        # 標題 
        title = soup.select('h1')[0].text.strip()
        title_tw = cc.convert(title)
        # print(title_tw)
        # 作者
        author = soup.select('h2 span')[0].text.strip('作者：')
        author_tw = cc.convert(author)
        # print(author_tw)
        # 字數
        wordCount = int(soup.find('span', itemprop='wordCount').text.strip('字'))
        # print(wordCount)
        # 文案
        novelintro = soup.select_one('#novelintro').text
        novelintro_tw = cc.convert(novelintro)
        # print(novelintro_tw)
        # 標籤
        tags = soup.select('.smallreadbody a[href*="bookbase.php?bq="]')
        tags_tw = ','.join([cc.convert(tag.text) for tag in tags])
        # print([cc.convert(tag.text) for tag in tags])
        # print(tags_tw)
        # 收藏數
        collected = int(soup.find('span',  itemprop="collectedCount").text)
        # print(collected)
        # category
        category = soup.find('span', itemprop="genre").text.strip()
        category_tw = cc.convert(category)
        # print(category_tw)
    except Exception as e:
        print(e)
        return None
    else:
        body = {
            'title': title_tw,
            'author': author_tw,
            'outline': novelintro_tw,
            'category': category_tw,
            'tags': tags_tw,
            'words': wordCount,
            'collectedCount': collected,
            'url': url,
            'website': 'jjwxc',
        }        
        return body


def crawler_sto(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    try:
        # 小說
        list_body = soup.select('.slistbody')
        print(len(list_body))
        # one = list_body[0].text.strip()
        # print(one)
        for body in list_body:
            # 標題 作者
            sto = "https://www.sto.cx"
            title_author = body.select('.t')[0].text.strip()
            title, author = re.findall(r'《(.*)》作者：(.*)\(', title_author)[0]
            title_tw = cc.convert(title)
            author_tw = cc.convert(author)
            print(title_tw, author_tw)
             # 如果有詳細介紹：
            content = body.select('.i a')
            if content:
                intro = content[0].get('onclick')
                # 完整大綱
                intro_url = re.findall(r"content: '(.*)}", intro)[0].strip("'")
                intro_body = BeautifulSoup(get_content(sto+intro_url),'lxml')
                outline_raw = intro_body.select('body')[0].text.strip()
                h3 = intro_body.find('h3')
                h3 = h3.text.strip() if h3 else ''
                outline = outline_raw.strip('立即阅读').strip(h3)
                outline_tw = cc.convert(outline)
                # print(outline_tw)
                # 內容標籤
                match = re.search(r'內容標籤：(.*)主角：', outline_tw)
                match_2 = re.search(r'內容標簽：(.*)主角：', outline_tw) 
                if match:
                    tags = match.group(1).strip()
                elif match_2:
                    tags = match_2.group(1).strip()
                else:
                    tags = ""
                print(f'有詳細介紹，tags:{tags}')
            else:
                outline = body.select('.i')[0].text.strip()
                outline_tw = cc.convert(outline)
                tags = ""
                print(f'無詳細介紹')
            # 年份
            year = int(re.findall(r'Time：(\d+)年', body.select('.b')[0].text.split()[0])[0])
            # 日期
            date_text = body.select('.b')[0].text.split()[0].strip('Time：')
            date = datetime.strptime(date_text, "%Y年%m月%d日").strftime("%Y-%m-%d")
            # 類別
            category = body.select('.b')[0].text.split()[1].strip("Class：")
            category_tw = cc.convert(category)
            # 文檔大小
            size = int(body.select('.b')[0].text.split()[2].strip("Size：").strip('k'))
            # print(size)
            # url
            url = body.select_one('.t a')['href']
            novel_url = sto + url
            # print(novel_url)
            # 評論數量
            try:
                novel_id = re.findall(r'book-(\d+)-', novel_url)[0]
            except:
                novel_id = re.findall(r'bid=(\d+)', novel_url)[0]
            comment_url = "https://www.sto.cx/User/comment.aspx?id="+ novel_id
            comment_text = BeautifulSoup(get_content(comment_url),'lxml').select('.comtLT .fr')[0].text.strip()
            comment_num = int(re.findall(r'共(\d+)條', comment_text)[0].strip())
            print(f'評論數量：{comment_num}')
            # break
            body = {
                'title': title_tw,
                'author': author_tw,
                'outline': outline_tw,
                'category': category_tw,
                'tags': tags,
                'year': year,
                'url': novel_url,
                'website': 'sto',
                'size': size,
                'comment': comment_num,
                'date': date,
            } 
            novel = title_tw + author_tw 
            if r.get(f'{novel}') is None:
                r.set(f'{novel}', f'{url}')
                es.index(index='sto_novels_info', body = body)
        last_page = soup.select('.paginator a')[-1].attrs.get('disabled')
        if last_page:
            has_next_page = False
        else:
            has_next_page = True
    except Exception as e:
        print(e)
        return None
    else:
        return {'has_next_page': has_next_page}


def get_sto_category(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    try:
        categories_links = soup.select('#showClass a')
        sto = "https://www.sto.cx"
        links = []
        for link in categories_links:
            href = link['href']  # 提取href属性
            url = sto + href
            links.append(url)
        # print(links)
        return links
    except Exception as e:
        print(e)


def get_sto_page_url():
    links = get_sto_category(get_content("https://www.sto.cx/sbn.aspx?c=0"))
    for link in links[-1:]:
        i = 1
        while True:
            page_url = f'{link}&page={i}'
            result = crawler_sto(get_content(page_url))
            if result and result['has_next_page']:
                i += 1
            else:
                break
    

#crawler(get_jjwxc_page("https://www.jjwxc.net/onebook.php?novelid=3546151"))


def jjwxc():
    category_links = get_jjwxc_categories(get_content("https://www.jjwxc.net/channeltoplist.php?channelid=17&str=124"))
    for category_link in category_links:
        get_jjwxc_novels(category_link)    


if __name__ == '__main__':
    get_sto_page_url()
