"""从历史数据重新生成HTML报告（不进行网络抓取）"""
import os, sys, json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
from report import build_html

data_dir = os.path.join(os.path.dirname(__file__), 'data')
with open(os.path.join(data_dir, 'history.json'), 'r', encoding='utf-8') as f:
    hist = json.load(f)

products = []
for name, info in hist['products'].items():
    records = info['history']
    if records:
        latest = records[-1]
        p = {
            'name': name, 'price': latest['price'],
            'change': latest.get('change', 0), 'date': latest['date']
        }
        if '钢材' in name:
            p['spec'] = '指数'; p['source'] = '西本新干线'
            p['link'] = 'https://www.steelx2.com/indices/65/index.html'; p['range'] = str(int(latest['price']))
        elif '生铁' in name:
            p['spec'] = 'Z18' if '铸造' in name else 'L8-10'; p['source'] = '废金属资讯网'
            p['link'] = 'http://www.feijs.com/news/news_detail.asp?class=stzq&id=885092'; p['range'] = str(int(latest['price']))
        elif '硅' in name:
            p['spec'] = '441#'; p['source'] = '上海有色网(SMM)'
            p['link'] = 'https://hq.smm.cn/silicon'; p['range'] = '9200~9400'
        elif 'A00铝' in name and 'SMM' in name:
            p['spec'] = 'A00'; p['source'] = '上海有色网(SMM)'
            p['link'] = 'https://hq.smm.cn/aluminum'; p['range'] = '22860~22900'
        elif '锌锭' in name and 'SMM' in name:
            p['spec'] = '0#'; p['source'] = '上海有色网(SMM)'
            p['link'] = 'https://hq.smm.cn/zinc'; p['range'] = '23680~23780'
        elif '304' in name:
            p['spec'] = '304/2B'; p['source'] = '上海有色网(SMM)'
            p['link'] = 'https://hq.smm.cn/stainless-steel'; p['range'] = '14900~15400'
        elif '长江' in name:
            p['spec'] = '1#' if '铜' in name else ('A00' if '铝' in name else '0#')
            p['source'] = '长江有色(CCMN)'; p['link'] = 'https://www.ccmn.cn/'
            p['range'] = str(int(latest['price']))
        products.append(p)

order = ['西本钢材指数','铸造生铁Z18','炼钢生铁L8-10','441#硅(昆明)','SMM A00铝','SMM 0#锌锭','304/2B毛边(无锡)','长江1#铜','长江A00铝','长江0#锌']
products.sort(key=lambda x: order.index(x['name']) if x['name'] in order else 99)

date_str = f"{hist['last_updated'][:4]}年{hist['last_updated'][5:7]}月{hist['last_updated'][8:10]}日"
html = build_html(products, date_str, 'https://xyx-zjp.github.io/commodity-daily/')

output_path = os.path.join(os.path.dirname(__file__), 'docs', 'index.html')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'✅ 报告已生成: {output_path}')
for p in products:
    chg = p.get('change')
    chg_str = f'(+{chg})' if chg and chg > 0 else f'({chg})' if chg and chg < 0 else '(持平)'
    print(f'  {p["name"]}: {p["price"]:,.0f} {chg_str}')
