#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试抓取 - 使用友好网站验证工具"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time

# 测试网站列表
test_sites = [
    {
        'name': '什么值得买 - 安全套搜索',
        'url': 'https://search.smzdm.com/?c=home&s=安全套',
        'selector': '.feed-row'
    },
    {
        'name': 'GitHub 趋势榜',
        'url': 'https://github.com/trending',
        'selector': 'article.Box-row'
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
            time.sleep(2)
            
            title = page.title()
            print(f"[Success] 页面标题：{title}")
            
            # 查找内容
            items = page.query_selector_all(site['selector'])
            print(f"[Items] 找到元素数量：{len(items)}")
            
            if len(items) > 0:
                print(f"[Success] ✅ 抓取成功！")
                for i, item in enumerate(items[:3], 1):
                    text = item.inner_text()[:150].replace('\n', ' ')
                    print(f"   {i}. {text}")
            else:
                print(f"[Warning] 未找到元素")
            
        except Exception as e:
            print(f"[Error] {e}")
        finally:
            browser.close()
    
    time.sleep(1)

print("\n" + "="*60)
print("[总结] 测试完成")
print("="*60)
