"""钉钉机器人推送 — 支持多群"""
import os
import time
import hmac
import hashlib
import base64
import urllib.request
import json

# 多个钉钉群的机器人配置
BOTS = [
    {
        'name': '默认群',
        'webhook': os.environ.get('DINGTALK_WEBHOOK', 'https://oapi.dingtalk.com/robot/send?access_token=760ac472be71a8072b05b6e2c9e9bbae47533430bd4f1736438a1e38e4fd9088'),
        'secret': os.environ.get('DINGTALK_SECRET', 'SEC4dc36e92f804f96511ecc85732efd853c84c352ea022edb77c1d2073c29caf10'),
    },
    {
        'name': '第二个群',
        'webhook': 'https://oapi.dingtalk.com/robot/send?access_token=7163cf68f7a31843a8a0f128fb14a4e5bfdcab891e54dfae3f35b613f23af4d5',
        'secret': 'SEC14cf2ff53159a39641f05e5392a28b3933814e9777c695ba68e7a2e89af5c769',
    },
]


def _send_to_bot(bot, content):
    """向单个机器人推送"""
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f'{timestamp}\n{bot["secret"]}'
    signature = base64.b64encode(
        hmac.new(
            bot['secret'].encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')

    url = f'{bot["webhook"]}&timestamp={timestamp}&sign={urllib.request.quote(signature, safe="")}'

    data = json.dumps({
        'msgtype': 'markdown',
        'markdown': {'title': '价格日报', 'text': content}
    }, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json; charset=utf-8'})
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read().decode())
    return result


def send_report(products, report_url, date_str):
    """推送价格日报到所有钉钉群"""
    # 构建消息内容
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

    # 注意：钉钉 Markdown 中 **[链接](url)** 会导致链接不可点击
    # 去掉加粗，使用普通 Markdown 链接
    content = f'''# 📊 大宗商品价格日报
## {date_str}

---

| 品种 | 均价(元/吨) | 涨跌 |
|:---|---:|:---|
{chr(10).join(rows)}

---

📈 [查看完整报告（趋势图+明细）]({report_url})

> ⏰ 每日14:00自动更新 | 数据：西本/废金属/SMM/长江有色'''

    # 推送到所有群
    success = 0
    for bot in BOTS:
        try:
            result = _send_to_bot(bot, content)
            if result.get('errcode') == 0:
                print(f'[钉钉] {bot["name"]} 推送成功')
                success += 1
            else:
                print(f'[钉钉] {bot["name"]} 推送失败: {result}')
        except Exception as e:
            print(f'[钉钉] {bot["name"]} 推送异常: {e}')

    print(f'[钉钉] 共 {success}/{len(BOTS)} 个群推送成功')
    return success > 0
