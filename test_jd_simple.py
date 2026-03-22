#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试京东抓取 - 使用普通商品关键词"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time

# 京东搜索 URL - 使用普通商品测试
url = "https://search.jd.com/Search?keyword=iPhone 手机"

print(f"[Spider] 开始抓取：{url}")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    page = context.new_page()
    
    try:
        print("[Browser] 正在加载页面...")
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        
        title = page.title()
        print(f"[Success] 页面加载完成！")
        print(f"[Title] 页面标题：{title}")
        print("=" * 60)
        
        products = []
        
        # 等待商品列表出现
        print("[Browser] 等待商品列表加载...")
        try:
            page.wait_for_selector('.gl-item', timeout=10000)
        except:
            print("[Warning] 商品列表加载超时")
        
        items = page.query_selector_all('.gl-item')
        print(f"\n[Products] 找到商品数量：{len(items)}")
        
        if len(items) > 0:
            for i, item in enumerate(items[:5], 1):
                try:
                    product_info = {}
                    
                    title_el = item.query_selector('.p-name em')
                    if title_el:
                        product_info['title'] = title_el.inner_text()[:100]
                    
                    price_el = item.query_selector('.p-price i')
                    if price_el:
                        product_info['price'] = price_el.inner_text()[:50]
                    
                    shop_el = item.query_selector('.p-shop a')
                    if shop_el:
                        product_info['shop'] = shop_el.inner_text()[:50]
                    
                    if product_info:
                        products.append(product_info)
                        print(f"\n   [商品 {i}]")
                        print(f"   标题：{product_info.get('title', 'N/A')}")
                        print(f"   价格：{product_info.get('price', 'N/A')}")
                        if 'shop' in product_info:
                            print(f"   店铺：{product_info.get('shop', 'N/A')}")
                except Exception as e:
                    print(f"   [Error] {e}")
                    continue
        
        page.screenshot(path='jd_iphone_screenshot.png')
        print("\n[Debug] 已保存截图：jd_iphone_screenshot.png")
        
        with open('jd_iphone_抓取结果.json', 'w', encoding='utf-8') as f:
            json.dump({
                'url': url,
                'title': title,
                'products': products,
                'timestamp': '2026-03-18 08:43'
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n[Saved] 结果已保存到：jd_iphone_抓取结果.json")
        
    except Exception as e:
        print(f"[Error] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()
