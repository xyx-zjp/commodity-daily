"""长江有色(CCMN)抓取器"""
import re
from . import safe_fetch

def fetch_ccmn():
    """抓取 ccmn.cn 1#铜、A00铝、0#锌均价"""
    try:
        soup = safe_fetch("https://www.ccmn.cn/")
        text = soup.get_text()

        results = []

        # 页面格式: 1#铜101680-101720101700+520
        # 规则: 品名 + 低价 + 高价 + 均价 + 涨跌
        
        patterns = {
            "1#铜": (r"1#铜(\d{5,6})\-(\d{5,6})(\d{5,6})([\+\-]?\d+)", "长江1#铜", "电解铜"),
            "A00铝": (r"A00铝(\d{5,6})\-(\d{5,6})(\d{5,6})([\+\-]?\d+)", "长江A00铝", "电解铝"),
            "0#锌": (r"0#锌(\d{5,6})\-(\d{5,6})(\d{5,6})([\+\-]?\d+)", "长江0#锌", "0#锌"),
        }

        for key, (pattern, name, spec) in patterns.items():
            m = re.search(pattern, text)
            if m:
                low = int(m.group(1))
                high = int(m.group(2))
                avg = int(m.group(3))  # 直接使用页面提供的均价
                change_str = m.group(4)
                change = int(change_str) if change_str and change_str != "0" else 0
                print(f"[CCMN] {name}: 均价={avg} ({low}~{high}), 涨跌={change:+d}")
                results.append({
                    "name": name,
                    "spec": spec,
                    "price": avg,
                    "change": change,
                    "date": "",
                    "source": "长江有色(CCMN)",
                    "link": "https://www.ccmn.cn/",
                    "range": f"{low:,}~{high:,}",
                })
            else:
                print(f"[CCMN] {key} not found in page")

        return results if results else None

    except Exception as e:
        print(f"[CCMN] Error: {e}")
    return None
