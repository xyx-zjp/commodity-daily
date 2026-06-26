"""钉钉机器人推送"""
import os
import time
import hmac
import hashlib
import base64
import urllib.request
import json

DINGTALK_WEBHOOK = os.environ.get('DINGTALK_WEBHOOK', '')
DINGTALK_SECRET = os.environ.get('DINGTALK_SECRET', '')

def send_report(products, report_url, date_str):
    """推送价格日报到钉钉"""
    if not DINGTALK_WEBHOOK or not DINGTALK_SECRET:
        print('[钉钉] 未配置 Webhook/Secret，跳过推送')
        return False
    
    try:
        # 计算签名
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f'{timestamp}\n{DINGTALK_SECRET}'
        signature = base64.b64encode(
            hmac.new(
                DINGTALK_SECRET.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        url = f'{DINGTALK_WEBHOOK}&timestamp={timestamp}&sign={urllib.request.quote(signature, safe="")}'
        
        # 构建表格
        rows = []
        for p in products:
            name = p['name']
            price = f"{p['price']:,.0f}"
            chg = p.get('change')
            if chg is None:
                chg_str = '—'
            elif chg > 0:
                chg_str = f'🔺 +{chg}'
            elif chg < 0:
                chg_str = f'🔻 {chg}'
            else:
                chg_str = '持平'
            rows.append(f'| {name} | {price} | {chg_str} |')
        
        content = f'''# 📊 大宗商品价格日报
## {date_str}

---

| 品种 | 均价(元/吨) | 涨跌 |
|:---|---:|:---|
{chr(10).join(rows)}

---

📈 **[查看完整报告（趋势图+明细）]({report_url})**

> ⏰ 每日9:00自动更新 | 数据：西本/废金属/SMM/长江有色'''
        
        data = json.dumps({
            'msgtype': 'markdown',
            'markdown': {'title': '价格日报', 'text': content}
        }, ensure_ascii=False).encode('utf-8')
        
        req = urllib.request.Request(
            url, data=data,
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode())
        
        if result.get('errcode') == 0:
            print('[钉钉] 推送成功')
            return True
        else:
            print(f'[钉钉] 推送失败: {result}')
            return False
            
    except Exception as e:
        print(f'[钉钉] 推送异常: {e}')
        return False
