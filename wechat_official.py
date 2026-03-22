#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
抓取品牌官方公众号最新文章
直接搜索公众号名称 + 文章
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

# 品牌官方公众号名称
BRANDS = {
    '杜蕾斯': '杜蕾斯官方微博',
    '杰士邦': '杰士邦 JISSBON',
    '冈本': '冈本 okamoto'
}

def search_official_account(brand, account_name):
    """搜索指定公众号的文章"""
    
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
            # 搜索公众号名称
            url = f"https://weixin.sogou.com/weixin?type=1&query={account_name}"
            print(f"\n[搜索公众号] {brand} - {account_name}")
            print(f"[URL] {url}")
            
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # 检查验证码
            captcha = page.query_selector('iframe[src*="captcha"]')
            if captcha:
                print(f"[Warning] 检测到验证码")
                return [], None
            
            # 查找公众号
            account_item = page.query_selector('.news-list2 li')
            if account_item:
                print("[Success] 找到公众号")
                
                # 获取公众号名称
                name_el = account_item.query_selector('.name-txt em')
                if name_el:
                    print(f"[公众号] {name_el.inner_text().strip()}")
                
                # 查找该公众号的文章（切换到文章搜索）
                print(f"\n[搜索文章] {brand} 最新文章")
                
                # 重新搜索文章
                article_url = f"https://weixin.sogou.com/weixin?type=2&query={brand}&tsn=1"
                page.goto(article_url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)
                
                # 提取文章列表
                items = page.query_selector_all('.news-list li')
                print(f"[Success] 找到 {len(items)} 篇文章")
                
                for i, item in enumerate(items[:5], 1):
                    try:
                        article = {}
                        
                        # 标题
                        title_el = item.query_selector('h3 a')
                        if title_el:
                            article['title'] = title_el.inner_text().strip()
                        
                        # 链接
                        if title_el:
                            link = title_el.get_attribute('href')
                            if link.startswith('/'):
                                link = f"https://weixin.sogou.com{link}"
                            article['link'] = link
                        
                        # 摘要
                        abstract_el = item.query_selector('.txt-info')
                        if abstract_el:
                            article['abstract'] = abstract_el.inner_text().strip()[:200]
                        
                        # 公众号
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
            else:
                print("[Warning] 未找到公众号")
                # 直接搜索品牌文章
                article_url = f"https://weixin.sogou.com/weixin?type=2&query={brand}&tsn=1"
                page.goto(article_url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)
                
                items = page.query_selector_all('.news-list li')
                for i, item in enumerate(items[:5], 1):
                    try:
                        article = {}
                        title_el = item.query_selector('h3 a')
                        if title_el:
                            article['title'] = title_el.inner_text().strip()
                            link = title_el.get_attribute('href')
                            if link.startswith('/'):
                                link = f"https://weixin.sogou.com{link}"
                            article['link'] = link
                            
                        abstract_el = item.query_selector('.txt-info')
                        if abstract_el:
                            article['abstract'] = abstract_el.inner_text().strip()[:200]
                        
                        account_el = item.query_selector('.account-wrap a')
                        if account_el:
                            article['account'] = account_el.inner_text().strip()
                        
                        time_el = item.query_selector('span s')
                        if time_el:
                            article['publish_date'] = time_el.inner_text().strip()
                        
                        if article.get('title'):
                            article['brand'] = brand
                            article['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                            articles.append(article)
                    except:
                        continue
            
            # 截图
            screenshot_path = f'wechat_{brand}_official.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[Screenshot] {screenshot_path}")
            
        except Exception as e:
            print(f"[Error] {brand}: {e}")
        finally:
            browser.close()
    
    return articles, screenshot_path


def main():
    print("="*60)
    print("品牌官方公众号 - 最新文章追踪")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    all_results = {}
    screenshots = []
    
    for brand, account in BRANDS.items():
        articles, screenshot = search_official_account(brand, account)
        all_results[brand] = articles
        if screenshot:
            screenshots.append(screenshot)
        time.sleep(2)
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = f'wechat_official_latest_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'official_accounts': BRANDS,
            'results': all_results
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"[完成] 结果已保存到：{output_file}")
    print("="*60)
    
    # 输出摘要
    print("\n[最新文章摘要]")
    for brand, articles in all_results.items():
        print(f"\n🔹 {brand} ({len(articles)}条)")
        for i, article in enumerate(articles, 1):
            print(f"  {i}. {article.get('title', 'N/A')[:50]}")
            print(f"     公众号：{article.get('account', 'N/A')}")
            print(f"     时间：{article.get('publish_date', 'N/A')}")
    
    return all_results, screenshots


if __name__ == '__main__':
    main()
