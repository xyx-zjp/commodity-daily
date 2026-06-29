"""上海生铁价格抓取器 - feijs.com"""
import re
import requests
from bs4 import BeautifulSoup
from . import HEADERS


def fetch_shengti():
    """抓取上海生铁价格"""
    try:
        # 第1步：抓取列表页获取最新链接
        list_url = 'http://www.feijs.com/news/news_stzq.asp'
        resp = requests.get(list_url, headers=HEADERS, timeout=15)
        resp.encoding = 'gb2312'
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 找到最新的"上海生铁价格"链接
        candidates = []
        for a in soup.find_all('a'):
            text = a.get_text(strip=True)
            if '上海生铁' in text:
                href = a.get('href', '')
                # 支持相对链接和绝对链接
                if href.startswith('http'):
                    full_href = href
                elif href.startswith('news_detail.asp'):
                    full_href = f'http://www.feijs.com/news/{href}'
                else:
                    continue
                # 从文本提取日期，如 "2026年6月29日上海生铁价格"
                m_date = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
                if m_date:
                    date_sort = f'{m_date.group(1)}{int(m_date.group(2)):02d}{int(m_date.group(3)):02d}'
                else:
                    date_sort = '0'
                candidates.append((date_sort, full_href, text))

        if not candidates:
            print('[生铁] 未找到上海生铁价格链接')
            return None

        # 选择日期最新的一条
        candidates.sort(key=lambda x: x[0], reverse=True)
        latest_href = candidates[0][1]
        print(f'[生铁] 最新链接: {latest_href} ({candidates[0][2]})')

        # 第2步：抓取详情页
        resp2 = requests.get(latest_href, headers=HEADERS, timeout=15)
        resp2.encoding = 'gb2312'
        soup2 = BeautifulSoup(resp2.text, 'html.parser')
        text = soup2.get_text()

        # 解析铸造生铁 Z18
        z18_price = None
        m_z18 = re.search(r'铸造生铁.*?Z18.*?(\d{3,5})', text)
        if m_z18:
            z18_price = int(m_z18.group(1))

        # 解析炼钢生铁 L8-10
        l810_price = None
        m_l8 = re.search(r'炼钢[铁]?.*?L8.*?(\d{3,5})', text)
        if m_l8:
            l810_price = int(m_l8.group(1))

        # 解析日期并统一为 YYYY-MM-DD
        date_str = ''
        m_date = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', text)
        if m_date:
            date_str = f'{m_date.group(1)}-{int(m_date.group(2)):02d}-{int(m_date.group(3)):02d}'

        results = []
        if z18_price:
            results.append({
                'name': '铸造生铁Z18',
                'spec': 'Z18',
                'price': z18_price,
                'change': None,
                'date': date_str,
                'source': '废金属资讯网',
                'link': list_url
            })
        if l810_price:
            results.append({
                'name': '炼钢生铁L8-10',
                'spec': 'L8-10',
                'price': l810_price,
                'change': None,
                'date': date_str,
                'source': '废金属资讯网',
                'link': list_url
            })

        return results if results else None

    except Exception as e:
        print(f'[生铁] 抓取失败: {e}')
        import traceback
        traceback.print_exc()
    return None
