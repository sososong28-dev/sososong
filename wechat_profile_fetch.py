#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从文章链接提取公众号 __biz 参数
然后访问公众号主页获取文章列表
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
import re
from datetime import datetime

# 用户提供的文章链接
ARTICLE_URL = "https://mp.weixin.qq.com/s/sYcWk4jryvA6oaBL4LUd_Q"

def extract_biz_from_article(url):
    """从文章页面提取公众号 __biz 参数"""
    
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
            
            # 获取页面源码
            content = page.content()
            
            # 提取公众号名称
            account_name = None
            account_el = page.query_selector('#js_name')
            if account_el:
                account_name = account_el.inner_text().strip()
                print(f"[公众号名称] {account_name}")
            
            # 尝试多种方式提取 __biz
            biz = None
            patterns = [
                r'var\s+biz\s*=\s*"([^"]+)"',
                r'biz\s*:\s*"([^"]+)"',
                r'__biz=([a-zA-Z0-9=]+)',
                r'data-js="[^"]*__biz=([a-zA-Z0-9=]+)"',
                r'window\.var\s*=\s*\{[^}]*biz\s*:\s*"([^"]+)"',
            ]
            
            print("\n[尝试提取 __biz]")
            for i, pattern in enumerate(patterns, 1):
                match = re.search(pattern, content)
                if match:
                    biz = match.group(1)
                    print(f"  匹配成功 (pattern {i}): {biz[:30]}...")
                    break
            
            if not biz:
                print("  未找到 __biz 参数")
                # 尝试从页面 URL 中提取
                current_url = page.url
                print(f"\n[当前 URL] {current_url}")
                url_match = re.search(r'__biz=([a-zA-Z0-9=]+)', current_url)
                if url_match:
                    biz = url_match.group(1)
                    print(f"  从 URL 提取：{biz[:30]}...")
            
            # 查找公众号主页链接
            print("\n[查找公众号主页链接]")
            profile_links = []
            
            # 尝试查找"查看公众号"等链接
            link_selectors = [
                '#js_profile_qrcode a',
                '.profile_link a',
                'a[href*="mp.weixin.qq.com/mp/profile"]',
                'a[href*="__biz="]'
            ]
            
            for selector in link_selectors:
                links = page.query_selector_all(selector)
                if links:
                    for link in links:
                        href = link.get_attribute('href')
                        if href and 'mp.weixin.qq.com' in href:
                            profile_links.append(href)
                            print(f"  找到链接：{href[:100]}")
            
            # 截图
            screenshot_path = 'article_biz_extract.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n[截图] {screenshot_path}")
            
            return {
                'account_name': account_name,
                'biz': biz,
                'profile_links': profile_links,
                'page_url': page.url
            }
            
        except Exception as e:
            print(f"[Error] {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            browser.close()


def visit_profile_page(biz, account_name):
    """访问公众号主页"""
    
    if not biz:
        print("\n[跳过] 没有 __biz 参数，无法访问公众号主页")
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
            profile_url = f"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}#wechat_redirect"
            print(f"\n[访问公众号主页]")
            print(f"[URL] {profile_url[:100]}...")
            
            page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(5)
            
            # 获取页面标题
            title = page.title()
            print(f"[页面标题] {title}")
            
            # 尝试查找文章列表
            articles = []
            
            # 查找历史消息文章
            article_els = page.query_selector_all('a[href*="/mp/appmsg/show"]')
            if not article_els:
                article_els = page.query_selector_all('a[href*="/s/"]')
            
            print(f"\n[文章列表] 找到 {len(article_els)} 篇文章")
            
            for i, el in enumerate(article_els[:10], 1):
                try:
                    title = el.inner_text().strip()[:100]
                    href = el.get_attribute('href')
                    if title and href:
                        articles.append({
                            'title': title,
                            'link': href
                        })
                        print(f"  {i}. {title}")
                except:
                    continue
            
            # 截图
            screenshot_path = f'{account_name}_profile.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n[截图] {screenshot_path}")
            
            return {
                'profile_url': profile_url,
                'title': title,
                'articles': articles,
                'screenshot': screenshot_path
            }
            
        except Exception as e:
            print(f"[Error] {e}")
            # 截图错误页面
            try:
                screenshot_path = f'{account_name}_profile_error.png'
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"[错误截图] {screenshot_path}")
            except:
                pass
            return None
        finally:
            browser.close()


def main():
    print("="*60)
    print("从文章链接提取公众号并访问主页")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    # 1. 提取 __biz
    print("\n[步骤 1] 从文章提取 __biz 参数")
    print("="*60)
    extract_result = extract_biz_from_article(ARTICLE_URL)
    
    if not extract_result:
        print("\n[Error] 提取失败")
        return
    
    # 保存提取结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    # 2. 访问公众号主页
    print("\n[步骤 2] 访问公众号主页拉取文章")
    print("="*60)
    biz = extract_result.get('biz')
    account_name = extract_result.get('account_name', 'unknown')
    
    profile_result = visit_profile_page(biz, account_name)
    
    # 合并结果
    final_result = {
        'extract_result': extract_result,
        'profile_result': profile_result,
        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    # 保存 JSON
    json_file = f'account_profile_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"[完成] 结果已保存到：{json_file}")
    print("="*60)
    
    # 输出摘要
    print("\n[公众号信息]")
    print(f"  名称：{extract_result.get('account_name', 'N/A')}")
    print(f"  __biz: {extract_result.get('biz', 'N/A')[:30] if extract_result.get('biz') else 'N/A'}...")
    
    if profile_result:
        print("\n[公众号主页]")
        print(f"  标题：{profile_result.get('title', 'N/A')}")
        articles = profile_result.get('articles', [])
        print(f"  文章数：{len(articles)}")
    else:
        print("\n[公众号主页] 无法访问")
    
    return final_result


if __name__ == '__main__':
    main()
