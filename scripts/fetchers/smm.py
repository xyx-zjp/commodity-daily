"""SMM 有色金属抓取器 - 需要 Playwright 自动登录"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

SMM_USERNAME = os.environ.get('SMM_USERNAME', '15267450959')
SMM_PASSWORD = os.environ.get('SMM_PASSWORD', 'Tc123456')

SMM_PAGES = {
    '411#硅(昆明)': {
        'url': 'https://hq.smm.cn/silicon',
        'keyword': '411#',
        'spec': '工业硅',
        'link': 'https://hq.smm.cn/silicon'
    },
    'SMM A00铝': {
        'url': 'https://hq.smm.cn/aluminum',
        'keyword': 'A00铝',
        'spec': '电解铝',
        'link': 'https://hq.smm.cn/aluminum'
    },
    'SMM 0#锌锭': {
        'url': 'https://hq.smm.cn/zinc',
        'keyword': '0#锌锭',
        'spec': '0#锌',
        'link': 'https://hq.smm.cn/zinc'
    },
    '304/2B卷-毛边(无锡)': {
        'url': 'https://hq.smm.cn/stainless-steel',
        'keyword': '304',
        'spec': '不锈钢',
        'link': 'https://hq.smm.cn/stainless-steel'
    }
}

async def fetch_smm():
    """用 Playwright 登录 SMM 并抓取所有品类的价格"""
    try:
        from playwright.async_api import async_playwright
        
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 900},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # 登录 SMM
            print('[SMM] 开始登录...')
            await page.goto('https://hq.smm.cn/silicon', wait_until='networkidle', timeout=30000)
            
            # 点击登录按钮
            login_btn = await page.query_selector('text=登录')
            if not login_btn:
                login_btn = await page.query_selector('a:has-text("登录")')
            if login_btn:
                await login_btn.click()
                await page.wait_for_timeout(2000)
            
            # 填写登录表单
            username_input = await page.query_selector('input[placeholder*="手机"], input[type="tel"], input[name="phone"], input[name="username"]')
            if not username_input:
                username_input = await page.query_selector('input')
            
            inputs = await page.query_selector_all('input')
            if len(inputs) >= 2:
                await inputs[0].fill(SMM_USERNAME)
                await inputs[1].fill(SMM_PASSWORD)
                print(f'[SMM] 填入账号: {SMM_USERNAME}')
                
                # 查找登录按钮
                submit_btn = await page.query_selector('button:has-text("登"), button:has-text("确"), button[type="submit"]')
                if not submit_btn:
                    submit_btn = await page.query_selector('button')
                if submit_btn:
                    await submit_btn.click()
                    await page.wait_for_timeout(5000)
                    print('[SMM] 登录成功')
            
            # 依次抓取各品类
            for name, cfg in SMM_PAGES.items():
                try:
                    print(f'[SMM] 抓取 {name}...')
                    await page.goto(cfg['url'], wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(2000)
                    
                    content = await page.content()
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    text = soup.get_text()
                    
                    # 提取价格数据
                    price = None
                    change = None
                    price_range = ''
                    
                    # 找表格中的价格
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    for i, line in enumerate(lines):
                        if cfg['keyword'] in line:
                            # 向后搜索价格数据
                            for j in range(i, min(i + 15, len(lines))):
                                import re
                                nums = re.findall(r'[\d,]+\.?\d*', lines[j])
                                if nums and len(nums) >= 2:
                                    try:
                                        p1 = float(nums[0].replace(',', ''))
                                        p2 = float(nums[1].replace(',', ''))
                                        # 判断是否为价格区间和均价
                                        if abs(p1 - p2) < 5000 and 1000 < p1 < 200000:
                                            price = (p1 + p2) / 2
                                            price_range = f'{p1:.0f}~{p2:.0f}'
                                            # 查找涨跌
                                            if j + 1 < len(lines):
                                                chg_nums = re.findall(r'[\-+]?\d+', lines[j + 1])
                                                if chg_nums:
                                                    change = int(chg_nums[0])
                                            break
                                    except:
                                        pass
                                elif nums and len(nums) == 1:
                                    try:
                                        val = float(nums[0].replace(',', ''))
                                        if 1000 < val < 200000:
                                            if price is None and i + 1 < len(lines):
                                                # 可能第一个数是均价
                                                price_range = f'{val:.0f}'
                                            break
                                    except:
                                        pass
                            if price:
                                break
                    
                    if price:
                        results.append({
                            'name': name,
                            'spec': cfg['spec'],
                            'price': price,
                            'change': change,
                            'date': '',
                            'source': '上海有色网(SMM)',
                            'link': cfg['link'],
                            'range': price_range
                        })
                        print(f'[SMM] {name}: 均价={price}, 涨跌={change}')
                    else:
                        print(f'[SMM] {name}: 未提取到价格')
                        
                except Exception as e:
                    print(f'[SMM] {name} 抓取失败: {e}')
            
            await browser.close()
        
        return results
        
    except Exception as e:
        print(f'[SMM] 整体失败: {e}')
        import traceback
        traceback.print_exc()
    return []
