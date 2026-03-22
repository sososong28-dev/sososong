#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从单篇微信公众号文章链接
反推公众号主页和其他文章
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime
import re

# 测试文章链接
ARTICLE_URL = "https://mp.weixin.qq.com/s/sYcWk4jryvA6oaBL4LUd_Q"

def extract_article_info(url):
    """提取文章信息和公众号信息"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            print(f"[访问文章] {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # 获取页面标题
            title = page.title()
            print(f"[文章标题] {title}")
            
            # 提取公众号名称
            account_name = None
            account_el = page.query_selector('#js_name')
            if account_el:
                account_name = account_el.inner_text().strip()
                print(f"[公众号名称] {account_name}")
            
            # 提取发布时间
            publish_time = None
            time_el = page.query_selector('em[id="publish_time"]')
            if time_el:
                publish_time = time_el.inner_text().strip()
                print(f"[发布时间] {publish_time}")
            
            # 提取公众号 ID（从页面源码中查找）
            account_id = None
            content = page.content()
            
            # 尝试多种 pattern 查找公众号原始 ID
            patterns = [
                r'biz":"([a-zA-Z0-9=]+)"',
                r'__biz=([a-zA-Z0-9=]+)',
                r'biz:"([a-zA-Z0-9=]+)"',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    account_id = match.group(1)
                    print(f"[公众号 ID] {account_id}")
                    break
            
            # 查找公众号主页链接
            account_link = None
            account_link_el = page.query_selector('#js_profile_qrcode a, .profile_link')
            if account_link_el:
                account_link = account_link_el.get_attribute('href')
                print(f"[公众号链接] {account_link}")
            
            # 尝试查找"查看历史消息"或相关文章
            related_articles = []
            
            # 查找页面底部的"相关阅读"
            related_els = page.query_selector_all('#js_content a[href*="mp.weixin.qq.com/s"]')
            if related_els:
                print(f"\n[相关阅读] 找到 {len(related_els)} 篇")
                for i, el in enumerate(related_els[:5], 1):
                    related_articles.append({
                        'title': el.inner_text().strip()[:100],
                        'link': el.get_attribute('href')
                    })
                    print(f"  {i}. {related_articles[-1]['title']}")
            
            # 截图
            screenshot_path = 'article_info.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n[Screenshot] {screenshot_path}")
            
            return {
                'title': title,
                'account_name': account_name,
                'account_id': account_id,
                'account_link': account_link,
                'publish_time': publish_time,
                'related_articles': related_articles,
                'url': url
            }
            
        except Exception as e:
            print(f"[Error] {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            browser.close()


def search_account_articles(account_name, max_articles=10):
    """搜索公众号其他文章"""
    
    articles = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            # 用微信搜一搜搜索公众号名称
            url = f"https://weixin.sogou.com/weixin?type=2&query={account_name}"
            print(f"\n[搜索公众号文章] {account_name}")
            print(f"[URL] {url}")
            
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # 检查验证码
            captcha = page.query_selector('iframe[src*="captcha"]')
            if captcha:
                print("[Warning] 检测到验证码")
                return []
            
            # 查找文章
            items = page.query_selector_all('.news-list li')
            print(f"[结果] 找到 {len(items)} 篇文章")
            
            for i, item in enumerate(items[:max_articles], 1):
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
                    
                    # 时间
                    time_el = item.query_selector('span s')
                    if time_el:
                        article['publish_date'] = time_el.inner_text().strip()
                    
                    if article.get('title'):
                        articles.append(article)
                        
                except Exception as e:
                    print(f"  [Error] 提取文章{i}失败：{e}")
                    continue
            
            # 截图
            screenshot_path = f'{account_name}_articles.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[Screenshot] {screenshot_path}")
            
        except Exception as e:
            print(f"[Error] {e}")
        finally:
            browser.close()
    
    return articles


def fetch_account_profile(account_id):
    """尝试访问公众号主页"""
    
    if not account_id:
        return None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            # 构造公众号主页 URL
            profile_url = f"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={account_id}#wechat_redirect"
            print(f"\n[访问公众号主页] {profile_url[:80]}...")
            
            page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # 获取页面标题
            title = page.title()
            print(f"[主页标题] {title}")
            
            # 截图
            screenshot_path = 'account_profile.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[Screenshot] {screenshot_path}")
            
            return {
                'profile_url': profile_url,
                'title': title
            }
            
        except Exception as e:
            print(f"[Error] {e}")
            return None
        finally:
            browser.close()


def main():
    print("="*60)
    print("微信公众号文章反推公众号主页")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    # 1. 提取文章信息
    print("\n[步骤 1] 提取文章信息")
    print("="*60)
    article_info = extract_article_info(ARTICLE_URL)
    
    if not article_info:
        print("\n[Error] 无法提取文章信息")
        return
    
    # 2. 尝试访问公众号主页
    print("\n[步骤 2] 访问公众号主页")
    print("="*60)
    if article_info.get('account_id'):
        profile_info = fetch_account_profile(article_info['account_id'])
        article_info['profile_info'] = profile_info
    
    # 3. 搜索公众号其他文章
    print("\n[步骤 3] 搜索公众号其他文章")
    print("="*60)
    if article_info.get('account_name'):
        other_articles = search_account_articles(article_info['account_name'], max_articles=10)
        article_info['other_articles'] = other_articles
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = f'account_reverse_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(article_info, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"[完成] 结果已保存到：{output_file}")
    print("="*60)
    
    # 输出摘要
    print("\n[公众号信息]")
    print(f"  名称：{article_info.get('account_name', 'N/A')}")
    print(f"  文章：{article_info.get('title', 'N/A')}")
    print(f"  时间：{article_info.get('publish_time', 'N/A')}")
    
    print("\n[其他文章]")
    other_articles = article_info.get('other_articles', [])
    if other_articles:
        for i, article in enumerate(other_articles, 1):
            print(f"  {i}. {article.get('title', 'N/A')[:50]}")
            print(f"     公众号：{article.get('account', 'N/A')}")
            print(f"     时间：{article.get('publish_date', 'N/A')}")
    else:
        print("  未找到其他文章")
    
    return article_info


if __name__ == '__main__':
    main()
