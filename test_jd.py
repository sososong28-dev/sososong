#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试京东抓取 - 相对友好的电商网站"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time

# 京东搜索 URL
url = "https://search.jd.com/Search?keyword=大象安全套"

print(f"[Spider] 开始抓取：{url}")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    
    page = context.new_page()
    
    try:
        print("[Browser] 正在加载页面...")
        # 使用 domcontentloaded 而不是 networkidle，加快加载
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        # 等待页面元素稳定
        time.sleep(3)
        
        title = page.title()
        print(f"[Success] 页面加载完成！")
        print(f"[Title] 页面标题：{title}")
        print("=" * 60)
        
        products = []
        
        # 京东商品选择器
        product_selectors = [
            '.gl-item',
            '.product-item',
            '[data-sku]'
        ]
        
        items = None
        for selector in product_selectors:
            items = page.query_selector_all(selector)
            if items and len(items) > 0:
                print(f"\n[Products] 找到商品列表，选择器：{selector}")
                print(f"   数量：{len(items)}")
                break
        
        if items and len(items) > 0:
            for i, item in enumerate(items[:5], 1):
                try:
                    product_info = {}
                    
                    # 标题
                    title_el = item.query_selector('.p-name em')
                    if title_el:
                        product_info['title'] = title_el.inner_text()[:100]
                    
                    # 价格
                    price_el = item.query_selector('.p-price i')
                    if price_el:
                        product_info['price'] = price_el.inner_text()[:50]
                    
                    # 店铺
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
                    print(f"   [Error] 提取商品{i}失败：{e}")
                    continue
        else:
            print("\n[Warning] 未找到商品列表")
        
        # 截图
        page.screenshot(path='jd_screenshot.png')
        print("\n[Debug] 已保存截图：jd_screenshot.png")
        
        # 保存结果
        with open('jd_大象安全套_抓取结果.json', 'w', encoding='utf-8') as f:
            json.dump({
                'url': url,
                'title': title,
                'products': products,
                'timestamp': '2026-03-18 08:43'
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n[Saved] 结果已保存到：jd_大象安全套_抓取结果.json")
        
    except Exception as e:
        print(f"[Error] 抓取失败：{str(e)}")
        page.screenshot(path='jd_error.png')
        print("[Debug] 已保存错误截图：jd_error.png")
        import traceback
        traceback.print_exc()
    
    finally:
        browser.close()
