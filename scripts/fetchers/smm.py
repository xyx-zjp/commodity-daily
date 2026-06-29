"""SMM 有色金属抓取器 - 需要 Playwright 自动登录"""
import os
import sys
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

SMM_USERNAME = os.environ.get('SMM_USERNAME', '15267450959')
SMM_PASSWORD = os.environ.get('SMM_PASSWORD', 'Tc123456')

SMM_PAGES = {
    '441#硅(昆明)': {
        'url': 'https://hq.smm.cn/silicon',
        'keyword': '441#硅(昆明)',
        'spec': '工业硅',
        'link': 'https://hq.smm.cn/silicon'
    },
    'SMM A00铝': {
        'url': 'https://hq.smm.cn/aluminum',
        'keyword': 'SMM A00铝',
        'spec': '电解铝',
        'link': 'https://hq.smm.cn/aluminum'
    },
    'SMM 0#锌锭': {
        'url': 'https://hq.smm.cn/zinc',
        'keyword': 'SMM 0#锌锭',
        'spec': '0#锌',
        'link': 'https://hq.smm.cn/zinc'
    },
    '304/2B毛边(无锡)': {
        'url': 'https://hq.smm.cn/stainless-steel',
        'keyword': '304/2B卷-毛边(无锡)',
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
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            # 登录 SMM
            print('[SMM] 开始登录...')
            await page.goto('https://hq.smm.cn/silicon', wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(1500)

            # 点击登录按钮（顶部导航的登录链接）
            try:
                await page.click('a:has-text("登录")', timeout=5000)
            except Exception:
                try:
                    await page.click('text=登录', timeout=5000)
                except Exception:
                    print('[SMM] 未找到登录入口，可能已登录')
            await page.wait_for_timeout(2000)

            # 等待登录弹窗/表单出现
            try:
                await page.wait_for_selector('input[type="tel"], input[placeholder*="手机"], input[placeholder*="用户名"], input[type="password"], input[type="text"]', timeout=10000, state='visible')
            except Exception as e:
                print(f'[SMM] 等待登录表单失败: {e}')

            # 填写登录表单 - 优先使用 type="tel" 和 type="password"
            username_input = await page.query_selector('input[type="tel"], input[placeholder*="手机"], input[placeholder*="邮箱"], input[name="phone"], input[name="username"]')
            password_input = await page.query_selector('input[type="password"]')

            if not username_input:
                inputs = await page.query_selector_all('input:visible')
                if len(inputs) >= 2:
                    username_input = inputs[0]
                    password_input = inputs[1]

            if username_input and password_input:
                await username_input.fill(SMM_USERNAME)
                await password_input.fill(SMM_PASSWORD)
                print(f'[SMM] 填入账号: {SMM_USERNAME}')

                # 点击登录按钮 - 使用可见的登录按钮
                try:
                    await page.click('button:visible:has-text("登录")', timeout=10000)
                except Exception:
                    try:
                        await page.click('button[type="submit"]:visible', timeout=10000)
                    except Exception:
                        # 兜底：用 JS 点击最后一个 form 内的 button
                        await page.evaluate('''() => {
                            const btns = Array.from(document.querySelectorAll('button'));
                            const loginBtn = btns.find(b => b.textContent.includes('登录') && b.offsetParent !== null);
                            if (loginBtn) loginBtn.click();
                        }''')
                await page.wait_for_timeout(5000)
                print('[SMM] 登录完成')
            else:
                print('[SMM] 未找到登录输入框，跳过登录')

            # 依次抓取各品类
            for name, cfg in SMM_PAGES.items():
                try:
                    print(f'[SMM] 抓取 {name}...')
                    await page.goto(cfg['url'], wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_timeout(2500)

                    # 使用 inner_text 保留表格中的制表符
                    text = await page.inner_text('body')

                    # 提取价格数据 - 页面表格为制表分隔：名称\t价格范围\t均价\t涨跌\t单位\t日期
                    price = None
                    change = None
                    price_range = ''

                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    for line in lines:
                        if cfg['keyword'] not in line:
                            continue
                        # 过滤掉升贴水、地区价差等衍生行
                        if any(skip in line for skip in ['升贴水', '地区价差', 'CIF', 'FOB', '废不锈钢', '边料']):
                            continue
                        cols = [c.strip() for c in line.split('\t') if c.strip()]
                        if len(cols) >= 3:
                            # cols[1] 是价格范围，如 9500~9700；cols[2] 是均价
                            range_str = cols[1]
                            avg_str = cols[2]
                            # 从均价列提取数字
                            avg_match = re.search(r'[\d,]+\.?\d*', avg_str)
                            if avg_match:
                                try:
                                    price = float(avg_match.group().replace(',', ''))
                                    price_range = range_str
                                    break
                                except Exception:
                                    pass
                        # 兜底：用正则从整行提取
                        nums = re.findall(r'[\d,]+\.?\d*', line)
                        if len(nums) >= 3:
                            try:
                                p_vals = [float(n.replace(',', '')) for n in nums[:3]]
                                # 第三个数通常是均价
                                if 1000 < p_vals[2] < 200000:
                                    price = p_vals[2]
                                    price_range = f'{p_vals[0]:.0f}~{p_vals[1]:.0f}'
                                    break
                            except Exception:
                                pass

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
