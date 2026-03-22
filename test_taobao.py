#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试淘宝抓取 - 使用 Playwright"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time

# 淘宝搜索 URL
url = "https://s.taobao.com/search?q=大象安全套"

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
        time.sleep(5)
        
        # 获取页面标题
        title = page.title()
        print(f"[Success] 页面加载完成！")
        print(f"[Title] 页面标题：{title}")
        print("=" * 60)
        
        # 检查是否有验证码或登录提示
        captcha_check = page.query_selector('iframe[src*="captcha"], .captcha, #login')
        if captcha_check:
            print("[Warning] 检测到验证码或登录要求")
        
        # 尝试抓取产品列表
        products = []
        
        # 尝试多种选择器
        product_selectors = [
            '.item',
            '.search-results-item',
            '[data-role="item"]',
            '.product-item',
            '.main-item'
        ]
        
        items = None
        for selector in product_selectors:
            items = page.query_selector_all(selector)
            if items and len(items) > 0:
                print(f"\n[Products] 找到产品列表，选择器：{selector}")
                print(f"   数量：{len(items)}")
                break
        
        if items and len(items) > 0:
            # 提取前 5 个产品信息
            for i, item in enumerate(items[:5], 1):
                try:
                    product_info = {}
                    
                    # 获取标题
                    title_el = item.query_selector('.title, .product-title, a[href*="item"]')
                    if title_el:
                        product_info['title'] = title_el.inner_text()[:100]
                    
                    # 获取价格
                    price_el = item.query_selector('.price, .product-price, .view-price')
                    if price_el:
                        product_info['price'] = price_el.inner_text()[:50]
                    
                    # 获取店铺名
                    shop_el = item.query_selector('.shop-name, .seller-name, .shop')
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
            # 获取页面内容预览
            content = page.content()
            print(f"\n[Preview] 页面内容长度：{len(content)} 字符")
            print("页面部分 HTML 预览：")
            print(content[:1500])
        
        # 截图保存
        page.screenshot(path='taobao_screenshot.png')
        print("\n[Debug] 已保存截图：taobao_screenshot.png")
        
        # 保存结果
        with open('taobao_大象安全套_抓取结果.json', 'w', encoding='utf-8') as f:
            json.dump({
                'url': url,
                'title': title,
                'products': products,
                'timestamp': '2026-03-18 08:43'
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n[Saved] 结果已保存到：taobao_大象安全套_抓取结果.json")
        
    except Exception as e:
        print(f"[Error] 抓取失败：{str(e)}")
        # 截图调试
        page.screenshot(path='taobao_error.png')
        print("[Debug] 已保存错误截图：taobao_error.png")
        
        import traceback
        traceback.print_exc()
    
    finally:
        browser.close()
