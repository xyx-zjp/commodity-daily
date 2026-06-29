"""长江有色(CCMN)抓取器 - 使用 Playwright 渲染页面"""
import re
from playwright.sync_api import sync_playwright


def fetch_ccmn():
    """抓取 ccmn.cn 1#铜、A00铝、0#锌均价"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            context = browser.new_context(
                viewport={'width': 1280, 'height': 900},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            page.goto('https://www.ccmn.cn/', wait_until='networkidle', timeout=60000)
            page.wait_for_timeout(5000)
            text = page.inner_text('body')
            browser.close()

        results = []

        # 页面格式: 1#铜102480-102520102500+800
        # 规则: 品名 + 低价 + 高价 + 均价 + 涨跌

        patterns = {
            "1#铜": (r"1#铜\s*(\d{5,6})[\-–—](\d{5,6})\s*(\d{5,6})\s*([\+\-]?\d+)", "长江1#铜", "电解铜"),
            "A00铝": (r"A00铝\s*(\d{5,6})[\-–—](\d{5,6})\s*(\d{5,6})\s*([\+\-]?\d+)", "长江A00铝", "电解铝"),
            "0#锌": (r"0#锌\s*(\d{5,6})[\-–—](\d{5,6})\s*(\d{5,6})\s*([\+\-]?\d+)", "长江0#锌", "0#锌"),
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
                if key == "1#铜":
                    print(f"[CCMN] debug text snippet: {text[:500]}")

        return results if results else None

    except Exception as e:
        print(f"[CCMN] Error: {e}")
        import traceback
        traceback.print_exc()
    return None
