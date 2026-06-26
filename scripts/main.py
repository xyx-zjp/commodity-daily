"""Commodity Daily Price Report - Main Entry"""
import os, sys, json, asyncio, traceback
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

REPORT_URL = os.environ.get('REPORT_URL', '')

try:
    from fetchers.steel import fetch_steel_index
    from fetchers.shengti import fetch_shengti
    from fetchers.smm import fetch_smm
    from fetchers.ccmn import fetch_ccmn
    from fetchers import update_product_history
    from report import build_html
    from dingtalk import send_report
    print("All imports OK")
except Exception as e:
    print(f"IMPORT ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

async def main():
    try:
        print("=" * 60)
        print("> Start commodity data fetch")
        print("> Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 60)

        today = datetime.now().strftime("%Y-%m-%d")
        all_products = []

        # 1. Steel Index
        print("\n[1/4] Steel Index...")
        try:
            steel = fetch_steel_index()
            if steel:
                steel['date'] = today
                all_products.append(steel)
                update_product_history(steel['name'], steel['price'], steel.get('change', 0), today)
                print("  Steel OK:", steel['price'])
            else:
                print("  Steel: no data")
        except Exception as e:
            print(f"  Steel ERROR: {e}")
            traceback.print_exc()

        # 2. ShengTie
        print("\n[2/4] ShengTie...")
        try:
            shengti = fetch_shengti()
            if shengti:
                for st in shengti:
                    st['date'] = st.get('date') or today
                    all_products.append(st)
                    update_product_history(st['name'], st['price'], st.get('change', 0), st['date'])
                print(f"  ShengTie OK: {len(shengti)} items")
            else:
                print("  ShengTie: no data")
        except Exception as e:
            print(f"  ShengTie ERROR: {e}")
            traceback.print_exc()

        # 3. SMM
        print("\n[3/4] SMM...")
        try:
            smm_data = await fetch_smm()
            for s in smm_data:
                s['date'] = today
                all_products.append(s)
                update_product_history(s['name'], s['price'], s.get('change', 0), today)
            print(f"  SMM OK: {len(smm_data)} items")
        except Exception as e:
            print(f"  SMM ERROR: {e}")
            traceback.print_exc()

        # 4. CCMN
        print("\n[4/4] CCMN...")
        try:
            ccmn = fetch_ccmn()
            if ccmn:
                for c in ccmn:
                    c['date'] = today
                    all_products.append(c)
                    update_product_history(c['name'], c['price'], c.get('change', 0), today)
                print(f"  CCMN OK: {len(ccmn)} items")
            else:
                print("  CCMN: no data")
        except Exception as e:
            print(f"  CCMN ERROR: {e}")
            traceback.print_exc()

        print(f"\nTotal products: {len(all_products)}")
        if not all_products:
            print("WARNING: No data fetched!")
            return

        for p in all_products:
            chg = p.get('change')
            chg_str = f'(+{chg})' if chg and chg > 0 else f'({chg})' if chg and chg < 0 else '(0)'
            print(f"  {p['name']}: {p['price']:,.0f} {chg_str}")

        # Generate HTML
        print("\n> Generating HTML report...")
        date_str = datetime.now().strftime('%Y%m%d')
        html = build_html(all_products, date_str, REPORT_URL)

        output_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"> Report saved: {output_path}")

        # DingTalk push
        print("\n> DingTalk push...")
        send_report(all_products, REPORT_URL, date_str)

        print("\n> Done!")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
