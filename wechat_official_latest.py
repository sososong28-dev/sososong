#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接搜索品牌官方公众号，查看最近发布的文章
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

# 品牌官方公众号（常见名称）
BRANDS = {
    '杜蕾斯': ['杜蕾斯', '杜蕾斯官方', 'durex 杜蕾斯'],
    '杰士邦': ['杰士邦', '杰士邦官方', 'JISSBON 杰士邦'],
    '冈本': ['冈本', '冈本官方', 'okamoto 冈本']
}

def search_official_wechat(brand, keywords):
    """搜索品牌官方公众号文章"""
    
    results = []
    screenshot_path = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 有头模式
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            for keyword in keywords:
                url = f"https://weixin.sogou.com/weixin?type=2&query={keyword}"
                print(f"\n[搜索] {brand} - 关键词：{keyword}")
                print(f"[URL] {url}")
                
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)
                
                # 检查验证码
                captcha = page.query_selector('iframe[src*="captcha"]')
                if captcha:
                    print(f"[Warning] 检测到验证码")
                    continue
                
                # 查找文章
                items = page.query_selector_all('.news-list li')
                print(f"[结果] 找到 {len(items)} 篇文章")
                
                if len(items) > 0:
                    # 提取前 3 篇
                    for i, item in enumerate(items[:3], 1):
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
                                article['search_keyword'] = keyword
                                article['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                                results.append(article)
                                
                        except Exception as e:
                            print(f"  [Error] 提取文章{i}失败：{e}")
                            continue
                    
                    # 找到结果就停止
                    if len(results) > 0:
                        break
            
            # 截图
            screenshot_path = f'wechat_{brand}_official_latest.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[Screenshot] {screenshot_path}")
            
        except Exception as e:
            print(f"[Error] {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()
    
    return results, screenshot_path


def fetch_article_full_content(article_url):
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
            content_el = page.query_selector('#js_content')
            content = content_el.inner_text() if content_el else '无法提取内容'
            
            # 提取发布时间
            time_el = page.query_selector('em[id*="publish_time"]')
            publish_time = time_el.inner_text() if time_el else '未知'
            
            # 提取公众号
            account_el = page.query_selector('#js_name')
            account = account_el.inner_text() if account_el else '未知'
            
            return {
                'content': content,
                'publish_time': publish_time,
                'account': account
            }
            
        except Exception as e:
            return {'error': str(e)}
        finally:
            browser.close()


def main():
    print("="*60)
    print("品牌官方微信公众号 - 最新文章")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    all_results = {}
    screenshots = []
    
    for brand, keywords in BRANDS.items():
        articles, screenshot = search_official_wechat(brand, keywords)
        all_results[brand] = articles
        if screenshot:
            screenshots.append(screenshot)
        time.sleep(2)
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = f'wechat_official_articles_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'brands': BRANDS,
            'results': all_results
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"[完成] 结果已保存到：{output_file}")
    print("="*60)
    
    # 输出摘要
    print("\n[品牌官方公众号最新文章]")
    for brand, articles in all_results.items():
        print(f"\n🔹 {brand} ({len(articles)}条)")
        for i, article in enumerate(articles, 1):
            print(f"  {i}. 【{article.get('account', '未知')}】{article.get('title', 'N/A')}")
            print(f"     时间：{article.get('publish_date', 'N/A')}")
    
    return all_results, screenshots


if __name__ == '__main__':
    main()
