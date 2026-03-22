#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试微信公众号相关抓取"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time

# 测试方案
test_sites = [
    {
        'name': '微信搜一搜 - 大象安全套',
        'url': 'https://weixin.sogou.com/weixin?type=2&query=大象安全套',
        'selector': '.news-list li'
    },
    {
        'name': '搜狗微信搜索',
        'url': 'https://weixin.sogou.com/',
        'selector': 'ul.news-list'
    }
]

for site in test_sites:
    print(f"\n{'='*60}")
    print(f"[测试] {site['name']}")
    print(f"[URL] {site['url']}")
    print('='*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            print("[Browser] 加载页面...")
            page.goto(site['url'], wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            title = page.title()
            print(f"[Success] 页面标题：{title}")
            
            # 检查是否有验证码
            captcha = page.query_selector('iframe[src*="captcha"], #captcha')
            if captcha:
                print("[Warning] 检测到验证码")
            
            # 查找内容
            items = page.query_selector_all(site['selector'])
            print(f"[Items] 找到元素数量：{len(items)}")
            
            if len(items) > 0:
                print(f"[Success] ✅ 抓取成功！")
                for i, item in enumerate(items[:3], 1):
                    text = item.inner_text()[:200].replace('\n', ' | ')
                    print(f"   {i}. {text}")
            else:
                print(f"[Warning] 未找到元素")
                # 截图
                page.screenshot(path=f'wechat_test_{test_sites.index(site)}.png')
                print(f"[Debug] 已保存截图")
            
        except Exception as e:
            print(f"[Error] {e}")
            page.screenshot(path=f'wechat_error_{test_sites.index(site)}.png')
        finally:
            browser.close()
    
    time.sleep(1)

print("\n" + "="*60)
print("[总结] 测试完成")
print("="*60)
