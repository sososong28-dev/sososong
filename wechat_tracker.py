#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
微信公众号竞品追踪爬虫
抓取指定品牌的公众号文章信息
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

# 竞品品牌列表
BRANDS = [
    '大象安全套',
    '杜蕾斯',
    '杰士邦',
    '冈本',
    '名流安全套',
    '赤尾',
    '羽感'
]

def scrape_wechat_articles(brand, max_pages=2):
    """抓取指定品牌的公众号文章"""
    
    articles = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            # 搜索 URL
            url = f"https://weixin.sogou.com/weixin?type=2&query={brand}"
            print(f"\n[抓取] {brand}")
            print(f"[URL] {url}")
            
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # 检查验证码
            captcha = page.query_selector('iframe[src*="captcha"], #captcha')
            if captcha:
                print(f"[Warning] {brand}: 检测到验证码，可能需要人工干预")
                return []
            
            # 查找文章列表
            items = page.query_selector_all('.news-list li')
            print(f"[Success] 找到 {len(items)} 篇文章")
            
            for i, item in enumerate(items, 1):
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
                    
                    # 公众号信息
                    account_el = item.query_selector('.account-wrap a')
                    if account_el:
                        article['account'] = account_el.inner_text().strip()
                    
                    # 发布时间
                    time_el = item.query_selector('span s')
                    if time_el:
                        article['publish_date'] = time_el.inner_text().strip()
                    
                    # 只保留有标题的文章
                    if article.get('title'):
                        article['brand'] = brand
                        article['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                        articles.append(article)
                        
                except Exception as e:
                    print(f"  [Error] 提取文章{i}失败：{e}")
                    continue
            
            # 截图保存
            screenshot_path = f'wechat_{brand}_screenshot.png'
            page.screenshot(path=screenshot_path)
            print(f"[Screenshot] {screenshot_path}")
            
        except Exception as e:
            print(f"[Error] {brand}: {e}")
        finally:
            browser.close()
    
    return articles


def main():
    print("="*60)
    print("微信公众号竞品追踪爬虫")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    all_articles = []
    
    for brand in BRANDS:
        articles = scrape_wechat_articles(brand)
        all_articles.extend(articles)
        time.sleep(2)  # 避免请求过快
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = f'wechat_articles_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'brands': BRANDS,
            'total_articles': len(all_articles),
            'articles': all_articles
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"[完成] 共抓取 {len(all_articles)} 篇文章")
    print(f"[保存] {output_file}")
    print("="*60)
    
    # 输出摘要
    print("\n[文章摘要]")
    for i, article in enumerate(all_articles[:10], 1):
        print(f"{i}. [{article.get('brand')}] {article.get('title', 'N/A')}")
        print(f"   公众号：{article.get('account', 'N/A')}")
        print(f"   时间：{article.get('publish_date', 'N/A')}")
        print()


if __name__ == '__main__':
    main()
