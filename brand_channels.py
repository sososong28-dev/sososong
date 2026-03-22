#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
访问品牌官网和电商页面，获取最新产品信息
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

# 品牌官方渠道
BRANDS = {
    '杜蕾斯': {
        '官网': 'https://www.durex.com.cn',
        '京东': 'https://mall.jd.com/index-1000003652.html',
        '天猫': 'https://durex.tmall.com'
    },
    '杰士邦': {
        '官网': 'https://www.jissbon.com',
        '京东': 'https://mall.jd.com/index-1000002736.html',
        '天猫': 'https://jissbon.tmall.com'
    },
    '冈本': {
        '官网': 'https://www.okamoto.com.cn',
        '京东': 'https://mall.jd.com/index-1000003439.html',
        '天猫': 'https://okamoto.tmall.com'
    }
}

def visit_brand_page(brand, channel, url):
    """访问品牌页面"""
    
    info = {}
    screenshot_path = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            print(f"\n[{brand}] 访问{channel}：{url[:50]}...")
            
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # 获取页面标题
            title = page.title()
            info['title'] = title
            print(f"[标题] {title}")
            
            # 尝试查找新品/热销产品
            products = []
            
            # 常见产品选择器
            selectors = [
                '.product-item', '.item', '.goods-item', 
                '[class*="product"]', '[class*="item"]'
            ]
            
            for selector in selectors:
                items = page.query_selector_all(selector)
                if items and len(items) > 0:
                    print(f"[产品] 找到 {len(items)} 个产品（选择器：{selector}）")
                    
                    # 提取前 3 个
                    for i, item in enumerate(items[:3], 1):
                        try:
                            p_info = {}
                            
                            # 产品名称
                            name_el = item.query_selector('[class*="name"], [class*="title"], h3, h4')
                            if name_el:
                                p_info['name'] = name_el.inner_text().strip()[:100]
                            
                            # 价格
                            price_el = item.query_selector('[class*="price"], .p-price')
                            if price_el:
                                p_info['price'] = price_el.inner_text().strip()[:50]
                            
                            if p_info.get('name'):
                                products.append(p_info)
                        except:
                            continue
                    
                    break
            
            info['products'] = products
            
            # 截图
            screenshot_path = f'{brand}_{channel.lower()}_2026.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[截图] {screenshot_path}")
            
        except Exception as e:
            print(f"[Error] {e}")
            info['error'] = str(e)
        finally:
            browser.close()
    
    return info, screenshot_path


def main():
    print("="*60)
    print("品牌官方渠道 - 最新产品追踪")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    all_results = {}
    screenshots = []
    
    for brand, channels in BRANDS.items():
        all_results[brand] = {}
        
        for channel, url in channels.items():
            info, screenshot = visit_brand_page(brand, channel, url)
            all_results[brand][channel] = info
            if screenshot:
                screenshots.append(screenshot)
            time.sleep(2)
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = f'brand_channels_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'brands': BRANDS,
            'results': all_results
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"[完成] 结果已保存到：{output_file}")
    print(f"[截图] {len(screenshots)} 张")
    print("="*60)
    
    # 输出摘要
    print("\n[品牌渠道摘要]")
    for brand, channels in all_results.items():
        print(f"\n🔹 {brand}")
        for channel, info in channels.items():
            title = info.get('title', 'N/A')[:50]
            products = info.get('products', [])
            print(f"   {channel}: {title}")
            if products:
                print(f"      产品 ({len(products)}个):")
                for p in products[:2]:
                    print(f"      - {p.get('name', 'N/A')} | {p.get('price', 'N/A')}")
    
    return all_results, screenshots


if __name__ == '__main__':
    main()
