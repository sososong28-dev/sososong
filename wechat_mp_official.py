#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
访问微信官网，搜索品牌官方公众号
获取最近发布的文章列表
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

# 品牌官方公众号名称（ verified accounts）
OFFICIAL_ACCOUNTS = {
    '杜蕾斯': '杜蕾斯官方微博',
    '杰士邦': '杰士邦 JISSBON', 
    '冈本': '冈本 okamoto'
}

def search_official_account_page(account_name):
    """搜索公众号主页"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            # 微信搜一搜公众号
            url = f"https://weixin.sogou.com/weixin?type=1&query={account_name}"
            print(f"\n[搜索公众号] {account_name}")
            print(f"[URL] {url}")
            
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # 检查验证码
            captcha = page.query_selector('iframe[src*="captcha"]')
            if captcha:
                print("[Warning] 检测到验证码，需要人工干预")
                return None
            
            # 查找第一个公众号
            account_item = page.query_selector('.news-list2 li')
            if not account_item:
                print("[Warning] 未找到公众号")
                return None
            
            # 获取公众号信息
            name_el = account_item.query_selector('.name-txt em')
            account_name_found = name_el.inner_text().strip() if name_el else '未知'
            print(f"[公众号名称] {account_name_found}")
            
            # 获取公众号介绍
            desc_el = account_item.query_selector('.txt-info')
            description = desc_el.inner_text().strip() if desc_el else '未知'
            print(f"[介绍] {description[:100]}")
            
            # 查找"查看历史消息"或类似链接
            link_el = account_item.query_selector('a[href*="mp.weixin.qq.com"]')
            if link_el:
                mp_link = link_el.get_attribute('href')
                print(f"[公众号链接] {mp_link[:100]}")
                
                # 尝试访问公众号文章页面
                return {
                    'name': account_name_found,
                    'description': description,
                    'link': mp_link
                }
            
            return None
            
        except Exception as e:
            print(f"[Error] {e}")
            return None
        finally:
            browser.close()


def fetch_recent_articles_mp(mp_url, brand):
    """从微信公众号页面获取最近文章"""
    
    articles = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            print(f"\n[访问公众号] {brand} - {mp_url[:80]}...")
            page.goto(mp_url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(5)
            
            # 获取页面标题
            title = page.title()
            print(f"[页面标题] {title}")
            
            # 查找文章列表（公众号历史消息页面）
            articles_list = page.query_selector_all('.weui-msg__content .rich_media_area')
            
            if not articles_list or len(articles_list) == 0:
                # 尝试其他选择器
                articles_list = page.query_selector_all('a[href*="mp.weixin.qq.com/s"]')
            
            print(f"[文章数量] 找到 {len(articles_list)} 篇文章")
            
            # 提取前 5 篇
            for i, item in enumerate(articles_list[:5], 1):
                try:
                    article = {}
                    
                    # 标题
                    title_el = item.query_selector('.rich_media_title, h2, h3')
                    if title_el:
                        article['title'] = title_el.inner_text().strip()
                    
                    # 链接
                    if isinstance(item, type(page)):
                        article['link'] = item.get_attribute('href')
                    else:
                        article['link'] = item.get_attribute('href')
                    
                    # 发布时间
                    time_el = item.query_selector('.rich_media_meta_text, em')
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
            screenshot_path = f'{brand}_mp_recent.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[Screenshot] {screenshot_path}")
            
        except Exception as e:
            print(f"[Error] {e}")
        finally:
            browser.close()
    
    return articles


def main():
    print("="*60)
    print("品牌官方公众号 - 最近文章")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    all_results = {}
    
    for brand, account_name in OFFICIAL_ACCOUNTS.items():
        print(f"\n{'='*60}")
        print(f"[品牌] {brand}")
        print(f"[官方公众号] {account_name}")
        print('='*60)
        
        # 搜索公众号
        account_info = search_official_account_page(account_name)
        
        if account_info:
            all_results[brand] = {
                'account_info': account_info,
                'articles': []
            }
            
            # 如果有公众号链接，尝试获取文章
            if account_info.get('link'):
                articles = fetch_recent_articles_mp(account_info['link'], brand)
                all_results[brand]['articles'] = articles
        else:
            all_results[brand] = {
                'account_info': None,
                'articles': []
            }
        
        time.sleep(2)
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = f'wechat_official_mp_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'official_accounts': OFFICIAL_ACCOUNTS,
            'results': all_results
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"[完成] 结果已保存到：{output_file}")
    print("="*60)
    
    # 输出摘要
    print("\n[官方公众号最近文章]")
    for brand, data in all_results.items():
        print(f"\n🔹 {brand}")
        account = data.get('account_info')
        if account:
            print(f"   公众号：{account.get('name', 'N/A')}")
            print(f"   介绍：{account.get('description', 'N/A')[:50]}")
        
        articles = data.get('articles', [])
        if articles:
            print(f"   最近文章 ({len(articles)}篇):")
            for i, article in enumerate(articles, 1):
                print(f"     {i}. {article.get('title', 'N/A')[:50]}")
                print(f"        时间：{article.get('publish_date', 'N/A')}")
        else:
            print(f"   文章：未找到")
    
    return all_results


if __name__ == '__main__':
    main()
