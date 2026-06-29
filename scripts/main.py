"""主入口 - 大宗商品每日价格抓取与报告生成"""
import os, sys, json, asyncio, traceback
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from fetchers.steel import fetch_steel_index
from fetchers.shengti import fetch_shengti
from fetchers.smm import fetch_smm
from fetchers.ccmn import fetch_ccmn
from fetchers import update_product_history
from report import build_html
from dingtalk import send_report

REPORT_URL = os.environ.get('REPORT_URL', '')

async def main():
    print('=' * 60)
    print('DaZong ShangPin JiaGe RiBao')
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('=' * 60)

    today = datetime.now().strftime('%Y-%m-%d')
    all_products = []

    print('[1/4] XiBen GangCai ZhiShu...')
    try:
        steel = fetch_steel_index()
        if steel:
            steel['date'] = today
            all_products.append(steel)
            update_product_history(steel['name'], steel['price'], steel.get('change', 0), today)
            print(f'  OK: {steel["price"]}')
        else:
            print('  No data')
    except Exception as e:
        print(f'  ERROR: {e}')
        traceback.print_exc()

    print('[2/4] ShangHai ShengTie...')
    try:
        shengti = fetch_shengti()
        if shengti:
            for st in shengti:
                st['date'] = st.get('date') or today
                all_products.append(st)
                update_product_history(st['name'], st['price'], st.get('change', 0), st['date'])
            print(f'  OK: {len(shengti)} items')
        else:
            print('  No data')
    except Exception as e:
        print(f'  ERROR: {e}')
        traceback.print_exc()

    print('[3/4] SMM YouSe JinShu...')
    try:
        smm_data = await fetch_smm()
        for s in smm_data:
            s['date'] = today
            all_products.append(s)
            update_product_history(s['name'], s['price'], s.get('change', 0), today)
        print(f'  OK: {len(smm_data)} items')
    except Exception as e:
        print(f'  ERROR: {e}')
        traceback.print_exc()

    print('[4/4] ChangJiang YouSe (CCMN)...')
    try:
        ccmn = await asyncio.to_thread(fetch_ccmn)
        if ccmn:
            for c in ccmn:
                c['date'] = today
                all_products.append(c)
                update_product_history(c['name'], c['price'], c.get('change', 0), today)
            print(f'  OK: {len(ccmn)} items')
        else:
            print('  No data')
    except Exception as e:
        print(f'  ERROR: {e}')
        traceback.print_exc()

    print(f'Total: {len(all_products)} products')
    if not all_products:
        print('WARNING: No data, skipping report generation')
        return

    for p in all_products:
        chg = p.get('change')
        chg_str = f'(+{chg})' if chg and chg > 0 else f'({chg})' if chg and chg < 0 else '(0)'
        print(f'  {p["name"]}: {p["price"]:,.0f} {chg_str}')

    date_str = datetime.now().strftime('%Y%m%d')
    html = build_html(all_products, date_str, REPORT_URL)

    output_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Report saved: {output_path}')

    send_report(all_products, REPORT_URL, date_str)
    print('All done!')

if __name__ == '__main__':
    asyncio.run(main())
