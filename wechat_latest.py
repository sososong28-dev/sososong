#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
抓取指定品牌微信公众号最新 5 条信息 + 截图
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

# 目标品牌（只抓取这 3 个）
BRANDS = ['杜蕾斯', '杰士邦', '冈本']

def scrape_brand_articles(brand, max_articles=5):
    """抓取指定品牌的公众号文章"""
    
    articles = []
    screenshot_path = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            url = f"https://weixin.sogou.com/weixin?type=2&query={brand}"
            print(f"\n[抓取] {brand}")
            print(f"[URL] {url}")
            
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # 检查验证码
            captcha = page.query_selector('iframe[src*="captcha"], #captcha')
            if captcha:
                print(f"[Warning] {brand}: 检测到验证码")
                return [], None
            
            # 查找文章列表
            items = page.query_selector_all('.news-list li')
            print(f"[Success] 找到 {len(items)} 篇文章")
            
            # 提取前 5 条
            for i, item in enumerate(items[:max_articles], 1):
                try:
                    article = {}
                    
                    # 标题
                    title_el = item.query_selector('h3 a')
                    if title_el:
                        article['title'] = title_el.inner_text().strip()
                    
                    # 链接
                    if title_el:
                        article['link'] = title_el.get_attribute('href')
                    
                    # 摘要
                    abstract_el = item.query_selector('.txt-info')
                    if abstract_el:
                        article['abstract'] = abstract_el.inner_text().strip()[:200]
                    
                    # 公众号名称
                    account_el = item.query_selector('.account-wrap a')
                    if account_el:
                        article['account'] = account_el.inner_text().strip()
                    
                    # 发布时间
                    time_el = item.query_selector('span s')
                    if time_el:
                        article['publish_date'] = time_el.inner_text().strip()
                    
                    if article.get('title'):
                        article['brand'] = brand
                        article['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                        articles.append(article)
                        
                except Exception as e:
                    print(f"  [Error] 提取文章{i}失败：{e}")
                    continue
            
            # 截图
            screenshot_path = f'wechat_{brand}_latest.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[Screenshot] {screenshot_path}")
            
        except Exception as e:
            print(f"[Error] {brand}: {e}")
        finally:
            browser.close()
    
    return articles, screenshot_path


def main():
    print("="*60)
    print("微信公众号竞品追踪 - 最新 5 条")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"品牌：{', '.join(BRANDS)}")
    print("="*60)
    
    all_results = {}
    screenshots = []
    
    for brand in BRANDS:
        articles, screenshot = scrape_brand_articles(brand, max_articles=5)
        all_results[brand] = articles
        if screenshot:
            screenshots.append(screenshot)
        time.sleep(2)
    
    # 保存 JSON 结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = f'wechat_latest_{timestamp}.json'
    
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
    print("\n[抓取结果摘要]")
    for brand in BRANDS:
        articles = all_results.get(brand, [])
        print(f"\n🔹 {brand} ({len(articles)} 条)")
        for i, article in enumerate(articles, 1):
            print(f"  {i}. {article.get('title', 'N/A')[:60]}")
            print(f"     公众号：{article.get('account', 'N/A')}")
            print(f"     时间：{article.get('publish_date', 'N/A')}")
            print()
    
    # 返回截图列表供后续使用
    print("\n[截图文件列表]")
    for ss in screenshots:
        print(f"  - {ss}")
    
    return screenshots


if __name__ == '__main__':
    main()
