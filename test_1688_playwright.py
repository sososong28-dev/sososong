#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 1688 抓取 - 使用 Playwright"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time

# 1688 搜索 URL
url = "https://s.1688.com/selloffer/offer_search.htm?keywords=大象安全套"

print(f"[Spider] 开始抓取：{url}")
print("=" * 60)

with sync_playwright() as p:
    # 启动浏览器
    browser = p.chromium.launch(headless=True)
    
    # 创建上下文，设置 user-agent
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    
    page = context.new_page()
    
    try:
        # 访问页面
        print("[Browser] 正在加载页面...")
        page.goto(url, wait_until='networkidle', timeout=30000)
        
        # 等待一下让页面完全加载
        time.sleep(3)
        
        # 获取页面标题
        title = page.title()
        print(f"[Success] 页面加载完成！")
        print(f"[Title] 页面标题：{title}")
        print("=" * 60)
        
        # 检查是否有验证码
        captcha_check = page.query_selector('iframe[src*="captcha"]')
        if captcha_check:
            print("[Warning] 检测到验证码，可能需要人工干预")
        
        # 尝试抓取产品列表
        products = []
        
        # 等待产品列表加载
        page.wait_for_selector('.offer-item, .search-result-offer, [data-role="offer-item"]', timeout=10000)
        
        # 查找产品
        product_selectors = [
            '.offer-item',
            '.search-result-offer', 
            '[data-role="offer-item"]',
            '.offer-list-item'
        ]
        
        items = None
        for selector in product_selectors:
            items = page.query_selector_all(selector)
            if items:
                print(f"\n[Products] 找到产品列表，选择器：{selector}")
                print(f"   数量：{len(items)}")
                break
        
        if items and len(items) > 0:
            # 提取前 5 个产品信息
            for i, item in enumerate(items[:5], 1):
                try:
                    product_info = {}
                    
                    # 获取标题
                    title_el = item.query_selector('h4, .title, .offer-title, a[href*="offer"]')
                    if title_el:
                        product_info['title'] = title_el.inner_text()[:100]
                    
                    # 获取价格
                    price_el = item.query_selector('.price, .money, [data-role="price"], .offer-price')
                    if price_el:
                        product_info['price'] = price_el.inner_text()[:50]
                    
                    # 获取店铺名
                    shop_el = item.query_selector('.shop-name, .seller-name')
                    if shop_el:
                        product_info['shop'] = shop_el.inner_text()[:50]
                    
                    if product_info:
                        products.append(product_info)
                        print(f"\n   [Product {i}]")
                        print(f"   标题：{product_info.get('title', 'N/A')}")
                        print(f"   价格：{product_info.get('price', 'N/A')}")
                        if 'shop' in product_info:
                            print(f"   店铺：{product_info.get('shop', 'N/A')}")
                except Exception as e:
                    print(f"   [Error] 提取产品{i}失败：{e}")
                    continue
        else:
            print("\n[Warning] 未找到产品列表")
            # 截图调试
            page.screenshot(path='1688_debug.png')
            print("[Debug] 已保存截图：1688_debug.png")
        
        # 保存结果
        with open('1688_大象安全套_抓取结果.json', 'w', encoding='utf-8') as f:
            json.dump({
                'url': url,
                'title': title,
                'products': products,
                'timestamp': '2026-03-18 08:41'
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n[Saved] 结果已保存到：1688_大象安全套_抓取结果.json")
        
    except Exception as e:
        print(f"[Error] 抓取失败：{str(e)}")
        # 截图调试
        page.screenshot(path='1688_error.png')
        print("[Debug] 已保存错误截图：1688_error.png")
        
        import traceback
        traceback.print_exc()
    
    finally:
        browser.close()
