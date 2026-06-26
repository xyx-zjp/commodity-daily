"""主入口 - 大宗商品每日价格抓取与报告生成"""
import os
import sys
import json
import asyncio
from datetime import datetime

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from fetchers.steel import fetch_steel_index
from fetchers.shengti import fetch_shengti
from fetchers.smm import fetch_smm
from fetchers.ccmn import fetch_ccmn
from fetchers import update_product_history
from report import build_html
from dingtalk import send_report

# GitHub Pages URL（部署后自动设为 https://<username>.github.io/<repo>/）
REPORT_URL = os.environ.get('REPORT_URL', '')

async # auto-trigger workflow test
def main():
    print('='*60)
    print('📊 大宗商品价格抓取开始')
    print(f'⏰ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('='*60)
    
    today = datetime.now().strftime('%Y-%m-%d')
    all_products = []
    
    # 1. 西本钢材指数
    print('\n[1/4] 抓取西本钢材指数...')
    steel = fetch_steel_index()
    if steel:
        steel['date'] = today
        all_products.append(steel)
        update_product_history(steel['name'], steel['price'], steel.get('change', 0), today)
    
    # 2. 上海生铁
    print('\n[2/4] 抓取上海生铁价格...')
    shengti = fetch_shengti()
    if shengti:
        for st in shengti:
            st['date'] = st.get('date') or today
            all_products.append(st)
            update_product_history(st['name'], st['price'], st.get('change', 0), st['date'])
    
    # 3. SMM 有色金属
    print('\n[3/4] 抓取SMM有色金属...')
    smm_data = await fetch_smm()
    for s in smm_data:
        s['date'] = today
        all_products.append(s)
        update_product_history(s['name'], s['price'], s.get('change', 0), today)
    
    # 4. 长江有色
    print('\n[4/4] 抓取长江有色价格...')
    ccmn = fetch_ccmn()
    if ccmn:
        for c in ccmn:
            c['date'] = today
            all_products.append(c)
            update_product_history(c['name'], c['price'], c.get('change', 0), today)
    
    print(f'\n{"="*60}')
    print(f'📋 共抓取 {len(all_products)} 个品种')
    
    if not all_products:
        print('❌ 没有抓取到任何数据！')
        return
    
    for p in all_products:
        chg = p.get('change')
        chg_str = f'(+{chg})' if chg and chg > 0 else f'({chg})' if chg and chg < 0 else '(持平)'
        print(f'  {p["name"]}: {p["price"]:,.0f} {chg_str}')
    
    # 生成HTML报告
    print('\n📝 生成HTML报告...')
    date_str = datetime.now().strftime('%Y年%m月%d日')
    html = build_html(all_products, date_str, REPORT_URL)
    
    # 输出到 GitHub Pages 目录
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'✅ 报告已保存: {output_path}')
    
    # 推送钉钉
    print('\n📱 推送钉钉通知...')
    send_report(all_products, REPORT_URL, date_str)
    
    print('\n🎉 全部完成！')

if __name__ == '__main__':
    asyncio.run(main())
# Triggered at 2026-06-26 10:16:56
