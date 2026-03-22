#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
抓取用户提供的文章全文
并尝试找到公众号更多 2026 年文章
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

# 用户提供的文章链接
ARTICLE_URL = "https://mp.weixin.qq.com/s/sYcWk4jryvA6oaBL4LUd_Q"

def fetch_article_full(url):
    """抓取文章完整内容"""
    
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
            
            # 获取标题
            title = page.title()
            print(f"[标题] {title}")
            
            # 获取公众号名称
            account_name = None
            account_el = page.query_selector('#js_name')
            if account_el:
                account_name = account_el.inner_text().strip()
                print(f"[公众号] {account_name}")
            
            # 获取发布时间
            publish_time = None
            time_el = page.query_selector('em[id="publish_time"]')
            if time_el:
                publish_time = time_el.inner_text().strip()
                print(f"[发布时间] {publish_time}")
            
            # 获取正文内容
            content = None
            content_el = page.query_selector('#js_content')
            if content_el:
                content = content_el.inner_text()
                print(f"[正文字数] {len(content)} 字符")
            
            # 截图
            screenshot_path = 'article_full_2026.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[截图] {screenshot_path}")
            
            return {
                'title': title,
                'account_name': account_name,
                'publish_time': publish_time,
                'content': content,
                'url': url,
                'screenshot': screenshot_path,
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            
        except Exception as e:
            print(f"[Error] {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            browser.close()


def save_as_markdown(article, output_path):
    """保存为 Markdown"""
    
    md = f"""# {article.get('title', '无标题')}

**公众号**: {article.get('account_name', 'N/A')}
**发布时间**: {article.get('publish_time', 'N/A')}
**抓取时间**: {article.get('crawl_time', 'N/A')}
**原文链接**: {article.get('url', 'N/A')}

---

## 正文内容

{article.get('content', '无内容')}

---

*本文由 AI 自动抓取于 {article.get('crawl_time')}*
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"\n[Saved] Markdown: {output_path}")


def main():
    print("="*60)
    print("抓取 2026 年最新微信公众号文章")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    # 抓取文章
    article = fetch_article_full(ARTICLE_URL)
    
    if article:
        # 保存 Markdown
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        md_file = f'article_2026_durex_{timestamp}.md'
        save_as_markdown(article, md_file)
        
        # 保存 JSON
        json_file = f'article_2026_durex_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        print(f"[Saved] JSON: {json_file}")
        
        # 输出摘要
        print("\n" + "="*60)
        print("[文章摘要]")
        print("="*60)
        content = article.get('content', '')
        if len(content) > 1500:
            print(content[:1500] + "\n\n... (内容过长，已保存完整到文件)")
        else:
            print(content)
        
        return article
    else:
        print("\n[Error] 抓取失败")
        return None


if __name__ == '__main__':
    main()
