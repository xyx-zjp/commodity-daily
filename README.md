# 大宗商品每日价格日报

自动抓取钢材、生铁、有色金属价格，生成可视化报告并推送到钉钉。

## 数据源

| 来源 | 品种 | 方式 |
|------|------|------|
| [steelx2.com](https://www.steelx2.com) | 西本钢材指数 | HTTP 请求 |
| [feijs.com](http://www.feijs.com) | 铸造生铁 Z18、炼钢生铁 L8-10 | HTTP 请求 |
| [smm.cn](https://hq.smm.cn) | 411#硅、A00铝、0#锌锭、304/2B不锈钢 | Playwright 自动登录 |
| [ccmn.cn](https://www.ccmn.cn) | 1#铜、A00铝、0#锌 | HTTP 请求 |

## 功能

- 🕘 每日 9:00 自动抓取（GitHub Actions）
- 📊 生成交互式 HTML 报告（卡片 + 趋势图 + 月度记录表）
- 🌐 自动部署到 GitHub Pages
- 📱 推送到钉钉群机器人
- 📥 支持 CSV 导出

## 在线报告

部署后访问：`https://XYX-ZJP.github.io/commodity-daily/`

## 本地运行

```bash
pip install -r requirements.txt
playwright install chromium
python scripts/main.py
```

## 环境变量

在 GitHub 仓库 Settings → Secrets and variables → Actions 中设置：

| Secret | 说明 |
|--------|------|
| `SMM_USERNAME` | SMM 登录手机号 |
| `SMM_PASSWORD` | SMM 登录密码 |
| `DINGTALK_WEBHOOK` | 钉钉机器人 Webhook |
| `DINGTALK_SECRET` | 钉钉机器人加签密钥 |
