#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
百度搜索竞品 2026 年最新动态
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

# 竞品品牌
BRANDS = ['杜蕾斯', '杰士邦', '冈本']

def search_baidu(brand, year=2026):
    """百度搜索品牌最新动态"""
    
    results = []
    screenshot_path = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            # 百度搜索，按时间排序
            query = f"{brand} 新品 2026 发布"
            url = f"https://www.baidu.com/s?wd={query}&rtt=1&bsst=1"
            # rtt=1 表示按时间排序
            
            print(f"\n[百度搜索] {brand}")
            print(f"[关键词] {query}")
            print(f"[URL] {url}")
            
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # 获取页面标题
            title = page.title()
            print(f"[Page Title] {title}")
            
            # 查找搜索结果
            items = page.query_selector_all('.result.c-container')
            print(f"[Success] 找到 {len(items)} 条结果")
            
            for i, item in enumerate(items[:5], 1):
                try:
                    result = {}
                    
                    # 标题
                    title_el = item.query_selector('h3 a, .t a')
                    if title_el:
                        result['title'] = title_el.inner_text().strip()
                        result['link'] = title_el.get_attribute('href')
                    
                    # 摘要
                    abstract_el = item.query_selector('.c-abstract, .abstract')
                    if abstract_el:
                        result['abstract'] = abstract_el.inner_text().strip()[:200]
                    
                    # 来源和时间
                    info_el = item.query_selector('.c-showurl, .news-source')
                    if info_el:
                        result['source'] = info_el.inner_text().strip()[:100]
                    
                    if result.get('title'):
                        result['brand'] = brand
                        result['search_query'] = query
                        result['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                        results.append(result)
                        
                except Exception as e:
                    print(f"  [Error] 提取结果{i}失败：{e}")
                    continue
            
            # 截图
            screenshot_path = f'baidu_{brand}_2026.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[Screenshot] {screenshot_path}")
            
        except Exception as e:
            print(f"[Error] {brand}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()
    
    return results, screenshot_path


def main():
    print("="*60)
    print("竞品 2026 年最新动态 - 百度搜索")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    all_results = {}
    screenshots = []
    
    for brand in BRANDS:
        results, screenshot = search_baidu(brand, year=2026)
        all_results[brand] = results
        if screenshot:
            screenshots.append(screenshot)
        time.sleep(2)
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = f'baidu_2026_latest_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'search_query': '品牌 + 新品 +2026+ 发布',
            'brands': BRANDS,
            'results': all_results
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"[完成] 结果已保存到：{output_file}")
    print("="*60)
    
    # 输出摘要
    print("\n[2026 年最新动态摘要]")
    for brand, results in all_results.items():
        print(f"\n🔹 {brand} ({len(results)}条)")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('title', 'N/A')[:60]}")
            print(f"     来源：{result.get('source', 'N/A')}")
    
    return all_results, screenshots


if __name__ == '__main__':
    main()
