"""西本钢材指数抓取器 - steelx2.com"""
from . import safe_fetch
import re

def fetch_steel_index():
    """抓取西本钢材指数"""
    try:
        soup = safe_fetch("https://www.steelx2.com/indices/65/index.html")
        text = soup.get_text()

        # 页面数据格式: 2026-06-263440.00-10.00-0.29%
        # 最新数据在最前面，找第一个日期+价格的模式
        m = re.search(r"(\d{4}-\d{2}-\d{2})(\d{4,5}\.\d{2})(-?\d+\.?\d*)", text)
        if m:
            date_str = m.group(1)
            price = float(m.group(2))
            change = float(m.group(3))
            print(f"[steel] {date_str}: {price} (change: {change})")
            return {
                "name": "西本钢材指数",
                "spec": "钢材指数",
                "price": price,
                "change": int(change),
                "date": date_str,
                "source": "西本新干线",
                "link": "https://www.steelx2.com/indices/65/index.html",
            }

        # Fallback: 查找4-5位数字（3000-5000范围）
        nums = re.findall(r"(\d{4,5}(?:\.\d+)?)", text)
        for n in nums:
            val = float(n)
            if 3000 <= val <= 5000:
                print(f"[steel] Fallback: {val}")
                return {
                    "name": "西本钢材指数",
                    "spec": "钢材指数",
                    "price": val,
                    "change": 0,
                    "date": "",
                    "source": "西本新干线",
                    "link": "https://www.steelx2.com/indices/65/index.html",
                }

        print("[steel] No matching price found")
    except Exception as e:
        print(f"[steel] Error: {e}")
    return None
