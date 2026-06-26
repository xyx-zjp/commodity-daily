"""长江有色(CCMN)抓取器"""
import re
from . import safe_fetch

def fetch_ccmn():
    """抓取 ccmn.cn 1#铜、A00铝、0#锌均价"""
    try:
        soup = safe_fetch('https://www.ccmn.cn/')
        text = soup.get_text()
        
        results = []
        
        # 1#铜
        for pattern in [r'1#铜[^\d]*?(\d{4,6})[^\d]*?(\d{4,6})', r'电解铜[^\d]*?(\d{4,6})[^\d]*?(\d{4,6})']:
            m = re.search(pattern, text)
            if m:
                low, high = int(m.group(1)), int(m.group(2))
                avg = (low + high) / 2
                results.append({
                    'name': '长江1#铜',
                    'spec': '电解铜',
                    'price': avg,
                    'change': None,
                    'date': '',
                    'source': '长江有色(CCMN)',
                    'link': 'https://www.ccmn.cn/',
                    'range': f'{low}~{high}'
                })
                break
        
        # A00铝
        for pattern in [r'A00铝[^\d]*?(\d{4,6})[^\d]*?(\d{4,6})', r'电解铝[^\d]*?A00[^\d]*?(\d{4,6})[^\d]*?(\d{4,6})']:
            m = re.search(pattern, text)
            if m:
                low, high = int(m.group(1)), int(m.group(2))
                avg = (low + high) / 2
                results.append({
                    'name': '长江A00铝',
                    'spec': '电解铝',
                    'price': avg,
                    'change': None,
                    'date': '',
                    'source': '长江有色(CCMN)',
                    'link': 'https://www.ccmn.cn/',
                    'range': f'{low}~{high}'
                })
                break
        
        # 0#锌
        for pattern in [r'0#锌[^\d]*?(\d{4,6})[^\d]*?(\d{4,6})', r'锌锭[^\d]*?0#[^\d]*?(\d{4,6})[^\d]*?(\d{4,6})']:
            m = re.search(pattern, text)
            if m:
                low, high = int(m.group(1)), int(m.group(2))
                avg = (low + high) / 2
                results.append({
                    'name': '长江0#锌',
                    'spec': '0#锌',
                    'price': avg,
                    'change': None,
                    'date': '',
                    'source': '长江有色(CCMN)',
                    'link': 'https://www.ccmn.cn/',
                    'range': f'{low}~{high}'
                })
                break
        
        for r in results:
            print(f'[CCMN] {r["name"]}: 均价={r["price"]}')
        
        return results if results else None
        
    except Exception as e:
        print(f'[CCMN] 抓取失败: {e}')
    return None
