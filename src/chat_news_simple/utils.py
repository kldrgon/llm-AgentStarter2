import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Optional, Tuple

# 设置请求会话和重试机制
def create_session() -> requests.Session:
    session = requests.Session()

    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


# 解析相对时间为绝对时间
def parse_relative_time(relative_time: str) -> datetime:
    now = datetime.now()
    if "分钟前" in relative_time:
        minutes = int(relative_time.replace("分钟前", "").strip())
        return now - timedelta(minutes=minutes)
    elif "小时前" in relative_time:
        hours = int(relative_time.replace("小时前", "").strip())
        return now - timedelta(hours=hours)
    else:
        return now


# 解析详细页的时间
def parse_time_from_detailed_page(session: requests.Session, link: str) -> Optional[datetime]:
    response = session.get(link)
    response.encoding = 'utf-8'

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        date_span = soup.find('span', class_='date')
        if date_span:
            date_str = date_span.text.strip()
            try:
                return datetime.strptime(date_str, '%Y年%m月%d日 %H:%M')
            except ValueError:
                return None
    return None


# 获取新闻列表

def get_news_list(session: requests.Session, keyword: str, time_range: str, page: int,  max_news: int = 20) -> List[List[str]]:
    """
    time_range        时间范围：h-一个小时内；d-一天内；w-一周内；m-一个月内；年份数字(如2023、2024)-表示限定指定的年份内
    """
    news_list = []
    page_number = page

    while True:
        url = f'https://search.sina.com.cn/news?c=news&adv=1&q={keyword}&time={time_range}&size=20&page={page_number}'
        print(f"正在从{url}获取新闻")
        response = session.get(url)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            result_blocks = soup.find_all('div', class_='box-result clearfix')

            if not result_blocks:
                break

            for block in result_blocks:
                title_tag = block.find('a')
                title = title_tag.text.strip()
                link = title_tag['href']

                # 跳过视频链接
                if 'video.sina.com.cn' in link:
                    continue

                infos = block.find('div', class_='r-info')
                source_time = infos.find('span').text.strip()
                st_list = source_time.split()
                source = st_list[0]

                time_str = ' '.join(st_list[1:3]) if len(st_list) > 2 else st_list[1]
                if "分钟前" in time_str or "小时前" in time_str:
                    news_time = parse_relative_time(time_str)
                else:
                    news_time = datetime.now()

                summary = infos.find('p', class_='content').text.strip()

                news_list.append([title, link, source, news_time, summary])

                if max_news != -1 and len(news_list) >= max_news:
                    return news_list

            page_number += 1
        else:
            break

    return news_list


# 提取新闻详细内容并优先获取详细页时间
def extract_news_details(session: requests.Session, news: List[str]) -> Optional[Tuple[str, str, str, datetime, str, str]]:
    title, link, source, list_time, summary = news
    detailed_time = parse_time_from_detailed_page(session, link)
    final_time = detailed_time if detailed_time else list_time
    print(f"正在从{link}获取详情")
    response = session.get(link)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('div', class_='article')
        if content is None:
            content = soup.find('section', class_='art_pic_card art_content')
        content_text = content.text.strip() if content else '正文内容未找到'
    else:
        content_text = '正文内容获取失败'

    return title, link, source, final_time, summary, content_text
