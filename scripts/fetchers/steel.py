"""西本钢材指数抓取器 - steelx2.com"""
from . import safe_fetch, parse_price
import re

def fetch_steel_index():
    """抓取西本钢材指数"""
    try:
        soup = safe_fetch('https://www.steelx2.com/indices/65/index.html')
        # 在页面中搜索价格相关信息
        text = soup.get_text()
        
        # 尝试多种模式匹配
        patterns = [
            r'今日指数[：:]\s*(\d+[\d,]*\.?\d*)',
            r'最新价[：:]\s*(\d+[\d,]*\.?\d*)',
            r'当前指数[：:]\s*(\d+[\d,]*\.?\d*)',
            r'钢材指数[^\d]*(\d+[\d,]*\.?\d*)',
        ]
        
        price = None
        for p in patterns:
            m = re.search(p, text)
            if m:
                price = float(m.group(1).replace(',', ''))
                break
        
        # 也尝试从数值中找到合理的价格
        if not price:
            nums = re.findall(r'(\d{4,5}(?:\.\d+)?)', text)
            for n in nums:
                val = float(n)
                if 3000 <= val <= 5000:  # 钢材指数合理范围
                    price = val
                    break
        
        if price:
            return {
                'name': '西本钢材指数',
                'price': price,
                'change': 0,  # metalx2 不直接提供涨跌
                'date': '',  # 从页面解析
                'source': '西本新干线',
                'link': 'https://www.steelx2.com/indices/65/index.html'
            }
    except Exception as e:
        print(f'[steel] 抓取失败: {e}')
    return None
