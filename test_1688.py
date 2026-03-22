#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 1688 抓取 - 大象安全套"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from scrapling.fetchers import StealthyFetcher
import json

# 1688 搜索 URL
url = "https://s.1688.com/selloffer/offer_search.htm?keywords=大象安全套"

print(f"[Spider] 开始抓取：{url}")
print("=" * 60)

try:
    # 使用 StealthyFetcher 绕过反爬
    page = StealthyFetcher.fetch(url, solve_cloudflare=True, headless=True)
    
    print(f"[Success] 抓取成功！状态码：{page.status}")
    
    # 获取页面标题
    title_elem = page.css('title').get()
    page_title = title_elem.strip() if title_elem else 'N/A'
    print(f"[Title] 页面标题：{page_title}")
    print("=" * 60)
    
    # 尝试抓取产品名称和价格
    # 1688 的产品列表通常在 offer 相关的 div 中
    products = []
    
    # 尝试常见的选择器
    selectors_to_try = [
        '.offer-item',
        '.search-result-offer',
        '[data-role="offer-item"]',
        '.offer-list-item',
        '.swim-content',
    ]
    
    for selector in selectors_to_try:
        items = page.css(selector).getall()
        if items:
            print(f"\n[Products] 找到产品列表，选择器：{selector}")
            print(f"   数量：{len(items)}")
            
            # 提取前 5 个产品的信息
            for i, item in enumerate(items[:5], 1):
                product_info = {}
                
                # 尝试提取标题
                title_selectors = ['h4', '.title', '.offer-title', 'a[href*="offer"]']
                for ts in title_selectors:
                    title = item.css(ts).get()
                    if title:
                        # 清理文本
                        title_text = title.strip()[:100]
                        if title_text:
                            product_info['title'] = title_text
                            break
                
                # 尝试提取价格
                price_selectors = ['.price', '.money', '[data-role="price"]', '.offer-price']
                for ps in price_selectors:
                    price = item.css(ps).get()
                    if price:
                        price_text = price.strip()[:50]
                        if price_text:
                            product_info['price'] = price_text
                            break
                
                if product_info:
                    products.append(product_info)
                    print(f"\n   [Product {i}]")
                    print(f"   标题：{product_info.get('title', 'N/A')}")
                    print(f"   价格：{product_info.get('price', 'N/A')}")
            
            break
    
    if not products:
        print("\n[Warning] 未找到产品列表，可能是页面结构变化或需要登录")
        print("\n[Preview] 页面部分内容预览：")
        print(page.text[:2000])
    
    # 保存结果
    with open('1688_大象安全套_抓取结果.json', 'w', encoding='utf-8') as f:
        json.dump({
            'url': url,
            'title': page_title,
            'status': page.status,
            'products': products,
            'timestamp': '2026-03-18 08:40'
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Saved] 结果已保存到：1688_大象安全套_抓取结果.json")
    
except Exception as e:
    print(f"[Error] 抓取失败：{str(e)}")
    import traceback
    traceback.print_exc()
