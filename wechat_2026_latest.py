#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
抓取微信公众号最新文章（2026 年）
按时间排序，获取最新内容
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime, timedelta

# 目标品牌
BRANDS = ['杜蕾斯', '杰士邦', '冈本']

def search_latest_articles(brand, year=2026):
    """搜索指定品牌的最新文章"""
    
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
            # 使用微信搜一搜，添加年份关键词
            url = f"https://weixin.sogou.com/weixin?type=2&query={brand}%20{year}&tsn=1&ft=&et="
            # tsn=1 表示按时间排序
            
            print(f"\n[搜索] {brand} ({year}年最新)")
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
            for i, item in enumerate(items[:5], 1):
                try:
                    article = {}
                    
                    # 标题
                    title_el = item.query_selector('h3 a')
                    if title_el:
                        article['title'] = title_el.inner_text().strip()
                    
                    # 链接（补全为完整 URL）
                    if title_el:
                        link = title_el.get_attribute('href')
                        if link.startswith('/'):
                            link = f"https://weixin.sogou.com{link}"
                        article['link'] = link
                    
                    # 摘要
                    abstract_el = item.query_selector('.txt-info')
                    if abstract_el:
                        article['abstract'] = abstract_el.inner_text().strip()[:200]
                    
                    # 公众号名称
                    account_el = item.query_selector('.account-wrap a')
                    if account_el:
                        article['account'] = account_el.inner_text().strip()
                    
                    # 发布时间（从页面提取）
                    time_el = item.query_selector('span s')
                    if time_el:
                        article['publish_date'] = time_el.inner_text().strip()
                    
                    # 尝试从摘要中提取年份
                    if article.get('abstract'):
                        if '2026' in article['abstract'] or '2025' in article['abstract']:
                            article['is_recent'] = True
                        else:
                            article['is_recent'] = False
                    
                    if article.get('title'):
                        article['brand'] = brand
                        article['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                        articles.append(article)
                        
                except Exception as e:
                    print(f"  [Error] 提取文章{i}失败：{e}")
                    continue
            
            # 截图
            screenshot_path = f'wechat_{brand}_2026_latest.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[Screenshot] {screenshot_path}")
            
        except Exception as e:
            print(f"[Error] {brand}: {e}")
        finally:
            browser.close()
    
    return articles, screenshot_path


def fetch_article_content(article_url):
    """抓取文章完整内容"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            page.goto(article_url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(2)
            
            # 提取正文
            content_el = page.query_selector('#js_content, .rich_media_content')
            content = content_el.inner_text() if content_el else None
            
            # 提取发布时间
            time_el = page.query_selector('em[id*="publish_time"]')
            publish_time = time_el.inner_text() if time_el else None
            
            return {
                'content': content,
                'publish_time': publish_time
            }
            
        except Exception as e:
            print(f"[Error] 抓取全文失败：{e}")
            return None
        finally:
            browser.close()


def main():
    print("="*60)
    print("微信公众号竞品追踪 - 2026 年最新内容")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    all_results = {}
    screenshots = []
    
    for brand in BRANDS:
        articles, screenshot = search_latest_articles(brand, year=2026)
        all_results[brand] = articles
        if screenshot:
            screenshots.append(screenshot)
        time.sleep(2)
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = f'wechat_2026_latest_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'search_year': 2026,
            'brands': BRANDS,
            'results': all_results
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"[完成] 结果已保存到：{output_file}")
    print("="*60)
    
    # 输出摘要
    print("\n[2026 年最新文章摘要]")
    for brand in BRANDS:
        articles = all_results.get(brand, [])
        recent_count = sum(1 for a in articles if a.get('is_recent'))
        print(f"\n🔹 {brand} (共{len(articles)}条，2026 年约{recent_count}条)")
        for i, article in enumerate(articles, 1):
            year_tag = "🆕" if article.get('is_recent') else "📅"
            print(f"  {year_tag} {i}. {article.get('title', 'N/A')[:50]}")
            print(f"      公众号：{article.get('account', 'N/A')}")
            print(f"      时间：{article.get('publish_date', 'N/A')}")
    
    return all_results, screenshots


if __name__ == '__main__':
    main()
