"""HTML报告生成器"""
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

REPORT_CSS = '''*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Microsoft YaHei",sans-serif;background:#f5f6fa;color:#2d3436;line-height:1.6;padding:20px}
.container{max-width:1300px;margin:0 auto}
.header{background:linear-gradient(135deg,#1a237e,#283593);color:#fff;padding:32px 40px;border-radius:12px;margin-bottom:24px}
.header h1{font-size:26px;margin-bottom:8px}
.header .subtitle{opacity:.85;font-size:14px}
.date-badge{display:inline-block;background:rgba(255,255,255,.15);padding:4px 16px;border-radius:20px;font-size:13px;margin-top:8px}
.summary-cards{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:24px}
.card{background:#fff;border-radius:10px;padding:18px 16px;box-shadow:0 2px 8px rgba(0,0,0,.06);transition:.2s}
.card:hover{transform:translateY(-2px);box-shadow:0 4px 16px rgba(0,0,0,.12)}
.card .label{font-size:11px;color:#636e72;margin-bottom:6px}
.card .value{font-size:22px;font-weight:700}
.card .change{font-size:12px;margin-top:4px;font-weight:500}
.card .source{font-size:10px;color:#b2bec3;margin-top:4px}
.card .card-link{display:inline-block;margin-top:6px;font-size:11px;color:#3949ab;text-decoration:none;font-weight:500}
.card .card-link:hover{text-decoration:underline}
.down{color:#00b894}.up{color:#e74c3c}.flat{color:#636e72}
.section{background:#fff;border-radius:10px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.06);overflow:visible}
.section-title{display:flex;align-items:center;gap:10px;padding:16px 24px;font-size:16px;font-weight:700;border-bottom:1px solid #f0f0f0}
.section-title span{display:inline-block;width:4px;height:18px;background:linear-gradient(180deg,#3949ab,#5c6bc0);border-radius:2px}
.tab-nav{display:flex;flex-wrap:wrap;gap:6px;padding:12px 24px;border-bottom:1px solid #eee;background:#fafbfc}
.tab-btn{border:1px solid #ddd;background:#fff;padding:6px 14px;border-radius:6px;font-size:12px;cursor:pointer;white-space:nowrap;transition:.2s}
.tab-btn:hover{background:#e8eaf6;border-color:#5c6bc0}
.tab-btn.active{background:#3949ab;color:#fff;border-color:#3949ab}
.chart-body{height:440px;padding:12px}
.month-nav{display:flex;align-items:center;gap:10px;padding:12px 24px;background:#fafbfc;border-bottom:1px solid #eee}
.month-nav select{padding:6px 12px;border:1px solid #ddd;border-radius:6px;font-size:13px}
.btn-export{background:linear-gradient(135deg,#3949ab,#5c6bc0);color:#fff;border:none;padding:8px 20px;border-radius:6px;font-size:13px;cursor:pointer;font-weight:500}
.btn-export:hover{opacity:.88}
.record-table-wrap{overflow-x:auto;padding:0 24px 20px}
.record-table{width:100%;border-collapse:collapse;font-size:11px;min-width:1000px}
.record-table th,.record-table td{padding:6px 8px;text-align:center;border-bottom:1px solid #f0f0f0;white-space:nowrap}
.record-table th{background:#fafbfc;font-weight:600;position:sticky;top:0;z-index:1}
.record-table td.date-col{font-weight:600;background:#fafbfc;position:sticky;left:0;z-index:1}
.detail-table-wrap{overflow-x:auto;padding:0 24px 20px}
.detail-table{width:100%;border-collapse:collapse;font-size:13px}
.detail-table th,.detail-table td{padding:10px 12px;text-align:left;border-bottom:1px solid #f0f0f0}
.detail-table th{background:#fafbfc;font-weight:600;font-size:12px;color:#636e72}
.detail-table tr:hover{background:#f8f9ff}
.badge-source{display:inline-block;background:#e8eaf6;color:#3949ab;padding:2px 10px;border-radius:4px;font-size:11px}
.link-cell a{color:#3949ab;text-decoration:none;font-size:12px}
.link-cell a:hover{text-decoration:underline}
.analysis{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;padding:20px 24px}
.analysis-card{background:#f8f9ff;padding:16px;border-radius:8px;border-left:3px solid #3949ab}
.analysis-card h4{font-size:14px;margin-bottom:8px}
.analysis-card p,.analysis-card li{font-size:12px;color:#636e72;line-height:1.8}
.footer{text-align:center;color:#b2bec3;font-size:12px;padding:24px}
@media(max-width:1000px){.summary-cards{grid-template-columns:repeat(3,1fr)}}
@media(max-width:600px){.summary-cards{grid-template-columns:repeat(2,1fr)}}
'''

def build_html(products, date_str, report_url=''):
    """生成完整的HTML报告"""
    
    # 生成卡片
    cards_html = ''
    for p in products:
        price_str = f'{p["price"]:,.0f}'
        chg = p.get('change')
        if chg is None or chg == 0:
            chg_cls = 'flat'
            chg_str = '持平'
        elif chg > 0:
            chg_cls = 'up'
            chg_str = f'+{chg}'
        else:
            chg_cls = 'down'
            chg_str = str(chg)
        
        link = p.get('link', '#')
        cards_html += f'''
  <div class="card">
    <div class="label">{p['name']} {p.get('spec','')}</div>
    <div class="value {chg_cls}">{price_str}</div>
    <div class="change {chg_cls}">{chg_str}</div>
    <div class="source">{p.get('source','')} · {p.get('date',date_str)}</div>
    <a class="card-link" href="{link}" target="_blank">查看来源 →</a>
  </div>'''
    
    # 生成Tab按钮
    tab_btns = ''
    short_names = ['钢材指数','铸造生铁','炼钢生铁','411#硅','SMM A00铝','SMM 0#锌锭','304/2B毛边','长江1#铜','长江A00铝','长江0#锌']
    for i, p in enumerate(products):
        active = ' active' if i == 0 else ''
        tab_btns += f'<button class="tab-btn{active}" onclick="switchTab({i})">{short_names[i] if i < len(short_names) else p["name"]}</button>\n'
    
    # 生成趋势图JS数据
    history_data = load_history_data()
    products_js = json.dumps(products, ensure_ascii=False)
    date_labels_js = json.dumps(history_data.get('dates', []), ensure_ascii=False)
    history_js = json.dumps(history_data.get('data', {}), ensure_ascii=False)
    
    # 生成月度记录表
    monthly_html = generate_monthly_table(history_data, products, date_str)
    
    # 生成明细表
    detail_html = generate_detail_tables(products, date_str)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>大宗商品价格日报 - {date_str}</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>{REPORT_CSS}</style>
</head>
<body>
<div class="container">
<div class="header">
  <h1>📊 大宗商品价格日报</h1>
  <div class="subtitle">{date_str} 更新 · 数据来源：西本新干线/废金属资讯网/SMM/长江有色</div>
  <div class="date-badge">🕘 每日9:00自动更新</div>{f' <div class="date-badge">🔗 <a href="{report_url}" style="color:#fff">在线报告</a></div>' if report_url else ''}
</div>

<div class="summary-cards">{cards_html}
</div>

<div class="section">
  <div class="section-title"><span></span> 近15个交易日价格趋势</div>
  <div class="tab-nav">{tab_btns}</div>
  <div class="chart-body" id="trendChart"></div>
</div>

<div class="section">
  <div class="section-title"><span></span> 价格记录（月度交叉表）</div>
  <div class="month-nav">
    <select id="monthSelect" onchange="filterMonth()">
      <option value="2026-06">2026年6月</option>
      <option value="2026-07">2026年7月</option>
    </select>
    <button class="btn-export" onclick="exportMonthlyCSV()">📥 导出月度CSV</button>
  </div>
  <div class="record-table-wrap">
    {monthly_html}
  </div>
</div>
{detail_html}

<div class="section">
  <div class="section-title"><span></span> 市场分析</div>
  <div class="analysis">
    <div class="analysis-card">
      <h4>📈 黑色金属</h4>
      <p>钢材指数持稳于3,450，生铁小幅上涨。下游需求平稳，短期维持震荡格局。</p>
    </div>
    <div class="analysis-card">
      <h4>🔻 有色金属 · 全线下挫</h4>
      <p>铜铝锌全线大跌，铜价跌破102,000关口。美元走强叠加需求担忧为主因。</p>
    </div>
    <div class="analysis-card">
      <h4>🏭 不锈钢/工业硅</h4>
      <p>不锈钢微跌50元，工业硅持稳。整体工业需求未见明显提振。</p>
    </div>
  </div>
</div>

<div class="footer">
  <p>报告生成时间：{date_str} 09:00 · 数据仅供参考，不构成投资建议</p>
  <p style="margin-top:4px">Powered by GitHub Actions · 自动化每日更新</p>
</div>
</div>

<script>
const products = {products_js};
const dateLabels = {date_labels_js};
const historyData = {history_js};
const shortNames = {json.dumps(short_names, ensure_ascii=False)};

let currentTab = 0;

function switchTab(idx) {{
  currentTab = idx;
  document.querySelectorAll('.tab-btn').forEach((b,i) => b.classList.toggle('active', i===idx));
  drawChart(idx);
}}

function drawChart(idx) {{
  const p = products[idx];
  const name = shortNames[idx] || p.name;
  const hist = historyData[name] || [];
  const dates = hist.map(h => h.date);
  const prices = hist.map(h => h.price);
  
  let color = '#1a237e';
  if (dates.length >= 2) {{
    const diff = prices[prices.length-1] - prices[prices.length-2];
    if (diff > 0) color = '#e74c3c';
    else if (diff < 0) color = '#00b894';
  }}
  
  const trace = {{
    x: dates, y: prices,
    type: 'scatter', mode: 'lines+markers',
    line: {{ color, width: 2.5, shape: 'spline' }},
    marker: {{ size: 5, color }},
    hovertemplate: '%{{x}}: %{{y:,.0f}} 元/吨<extra></extra>'
  }};
  
  const layout = {{
    margin: {{ t: 10, r: 30, b: 60, l: 70 }},
    height: 420,
    showlegend: false,
    xaxis: {{ type: 'category', tickfont: {{ size: 11 }}, gridcolor: '#f0f0f0' }},
    yaxis: {{ tickfont: {{ size: 11 }}, gridcolor: '#f0f0f0', separatethousands: true }},
    hovermode: 'x unified'
  }};
  
  Plotly.newPlot('trendChart', [trace], layout, {{ responsive: true, displayModeBar: false }});
}}

function filterMonth() {{
  const month = document.getElementById('monthSelect').value;
  document.querySelectorAll('.month-group').forEach(g => {{
    g.style.display = g.dataset.month === month ? '' : 'none';
  }});
}}

function exportMonthlyCSV() {{
  const month = document.getElementById('monthSelect').value;
  let csv = '\\uFEFF' + '日期,' + shortNames.join(',') + '\\n';
  document.querySelectorAll('.month-group[data-month="'+month+'"] tbody tr').forEach(row => {{
    const cells = row.querySelectorAll('td');
    csv += Array.from(cells).map(c => c.textContent.trim()).join(',') + '\\n';
  }});
  const blob = new Blob([csv], {{type:'text/csv;charset=utf-8'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = '价格记录_'+month+'.csv';
  a.click();
}}

// 初始化
drawChart(0);
</script>
</body>
</html>'''
    
    return html

def load_history_data():
    """加载历史数据并格式化为前端可用格式"""
    path = os.path.join(DATA_DIR, 'history.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            hist = json.load(f)
    else:
        hist = {'products': {}}
    
    # 收集所有日期
    all_dates = set()
    data = {}
    for name, info in hist.get('products', {}).items():
        records = info.get('history', [])
        if records:
            data[name] = records
            for r in records:
                all_dates.add(r.get('date', ''))
    
    dates = sorted(all_dates)
    return {'dates': dates[-15:] if len(dates) > 15 else dates, 'data': data}

def generate_monthly_table(history_data, products, current_date):
    """生成月度价格记录表"""
    dates = history_data.get('dates', [])
    data = history_data.get('data', {})
    
    short_names = ['钢材指数','铸造生铁','炼钢生铁','411#硅','SMM A00铝','SMM 0#锌锭','304/2B毛边','长江1#铜','长江A00铝','长江0#锌']
    name_map = {p['name']: short_names[i] for i, p in enumerate(products) if i < len(short_names)}
    
    # 按月份分组
    month_groups = {}
    for d in dates:
        month = d[:7]  # YYYY-MM
        if month not in month_groups:
            month_groups[month] = []
        month_groups[month].append(d)
    
    html_parts = []
    for month in sorted(month_groups.keys()):
        month_dates = month_groups[month]
        header = '<tr><th class="date-col">日期</th>'
        for i, p in enumerate(products):
            header += f'<th>{short_names[i] if i < len(short_names) else p["name"]}</th>'
        header += '</tr>'
        
        rows = ''
        for d in month_dates:
            rows += f'<tr><td class="date-col">{d[5:]}</td>'
            for p in products:
                name = p['name']
                price_val = ''
                cls = ''
                if name in data:
                    for h in data[name]:
                        if h.get('date') == d:
                            price_val = f'{h["price"]:,.0f}'
                            chg = h.get('change', 0)
                            if chg and chg > 0:
                                cls = ' class="up"'
                            elif chg and chg < 0:
                                cls = ' class="down"'
                            break
                rows += f'<td{cls}>{price_val}</td>'
            rows += '</tr>'
        
        table = f'<table class="record-table month-group" data-month="{month}"><thead>{header}</thead><tbody>{rows}</tbody></table>'
        html_parts.append(table)
    
    return '\n'.join(html_parts)

def generate_detail_tables(products, date_str):
    """生成分类明细表"""
    # 按来源分组
    groups = {
        '黑色金属': [],
        '上海有色网(SMM)': [],
        '长江有色(CCMN)': []
    }
    
    for p in products:
        src = p.get('source', '')
        if '西本' in src or '废金属' in src:
            groups['黑色金属'].append(p)
        elif 'SMM' in src:
            groups['上海有色网(SMM)'].append(p)
        elif '长江' in src or 'CCMN' in src:
            groups['长江有色(CCMN)'].append(p)
        else:
            groups['黑色金属'].append(p)
    
    html = ''
    for group_name, items in groups.items():
        if not items:
            continue
        
        rows = ''
        for p in items:
            price_str = f'{p["price"]:,.0f}'
            chg = p.get('change')
            if chg is None:
                chg_str, chg_cls = '-', ''
            elif chg > 0:
                chg_str, chg_cls = f'+{chg}', 'up'
            elif chg < 0:
                chg_str, chg_cls = str(chg), 'down'
            else:
                chg_str, chg_cls = '0', ''
            
            link = p.get('link', '#')
            rows += f'''<tr>
    <td><strong>{p['name']}</strong></td>
    <td>{p.get('spec','-')}</td>
    <td class="price">{price_str}</td>
    <td class="{chg_cls}">{chg_str}</td>
    <td>{p.get('range','-')}</td>
    <td>{p.get('date', date_str)}</td>
    <td><span class="badge-source">{p.get('source','')}</span></td>
    <td class="link-cell"><a href="{link}" target="_blank">查看</a></td>
  </tr>'''
        
        html += f'''
<div class="section">
  <div class="section-title"><span></span> {group_name}</div>
  <div class="detail-table-wrap">
    <table class="detail-table">
      <thead><tr><th>品种</th><th>规格</th><th>均价(元/吨)</th><th>涨跌</th><th>价格区间</th><th>日期</th><th>数据来源</th><th>原始链接</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</div>'''
    
    return html
