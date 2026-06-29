# 数据抓取器基类和工具
import requests
import re
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

def load_history():
    """加载历史数据"""
    path = os.path.join(DATA_DIR, 'history.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'products': {}}

def save_history(data):
    """保存历史数据"""
    path = os.path.join(DATA_DIR, 'history.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_product_history(name, price, change, date_str):
    """更新单个产品的历史记录"""
    data = load_history()
    if name not in data['products']:
        data['products'][name] = {'history': []}
    
    hist = data['products'][name]['history']
    # 去重：同一天的数据覆盖
    hist = [h for h in hist if h.get('date') != date_str]
    hist.append({'date': date_str, 'price': price, 'change': change})
    # 只保留最近60条
    hist = hist[-60:]
    data['products'][name]['history'] = hist
    data['last_updated'] = date_str
    save_history(data)
    return hist

def safe_fetch(url, encoding=None):
    """安全请求，返回 soup"""
    resp = requests.get(url, headers=HEADERS, timeout=20)
    if encoding:
        resp.encoding = encoding
    elif resp.apparent_encoding:
        resp.encoding = resp.apparent_encoding
    return BeautifulSoup(resp.text, 'html.parser')

def parse_price(text):
    """从文本中提取价格数字"""
    nums = re.findall(r'[\d,]+\.?\d*', str(text).replace(',', ''))
    if nums:
        return float(nums[0])
    return None
