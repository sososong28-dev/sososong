#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
点击微信公众号文章链接，抓取完整内容并保存为 Markdown
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

# 测试文章链接（从之前抓取结果中选取）
# 注意：搜狗的链接是中转贴，需要处理
TEST_ARTICLES = [
    {
        'brand': '杰士邦',
        'title': '杰士邦新广告比电视剧还好看……',
        'url': 'https://weixin.sogou.com/weixin?type=2&query=杰士邦'  # 先搜索再点击
    },
    {
        'brand': '冈本',
        'title': '冈本创业史',
        'url': 'https://weixin.sogou.com/weixin?type=2&query=冈本'
    }
]

def extract_article_content(page, article_url):
    """进入文章页面并提取完整内容"""
    
    try:
        # 直接访问文章链接
        print(f"[Browser] 访问文章：{article_url[:80]}...")
        page.goto(article_url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        
        # 获取页面标题
        title = page.title()
        print(f"[Title] {title}")
        
        # 尝试多种选择器提取正文
        content_selectors = [
            '#js_content',      # 微信公众号标准正文容器
            '.rich_media_content',
            'article',
            '[role="article"]',
            '.content'
        ]
        
        content = None
        for selector in content_selectors:
            element = page.query_selector(selector)
            if element:
                content = element.inner_text()
                print(f"[Success] 使用选择器提取：{selector}")
                print(f"[Length] 内容长度：{len(content)} 字符")
                break
        
        if not content:
            # 如果选择器失败，尝试获取整个页面文本
            content = page.inner_text('body')
            print(f"[Fallback] 获取整个页面文本：{len(content)} 字符")
        
        # 获取作者信息
        author = None
        author_el = page.query_selector('#js_name, .rich_media_meta_nickname')
        if author_el:
            author = author_el.inner_text().strip()
        
        # 获取发布时间
        publish_time = None
        time_el = page.query_selector('em[id*="publish_time"], .rich_media_meta_text')
        if time_el:
            publish_time = time_el.inner_text().strip()
        
        # 截图
        screenshot_path = f'article_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"[Screenshot] {screenshot_path}")
        
        return {
            'title': title,
            'author': author,
            'publish_time': publish_time,
            'content': content,
            'url': article_url,
            'screenshot': screenshot_path,
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
    except Exception as e:
        print(f"[Error] 提取失败：{e}")
        return None


def search_and_click_first_article(brand, keyword):
    """搜索品牌并点击第一篇文章"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 有头模式便于调试
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            # 搜索
            url = f"https://weixin.sogou.com/weixin?type=2&query={keyword}"
            print(f"\n[搜索] {brand} - {keyword}")
            print(f"[URL] {url}")
            
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            
            # 检查验证码
            captcha = page.query_selector('iframe[src*="captcha"]')
            if captcha:
                print("[Warning] 检测到验证码，需要人工干预")
                return None
            
            # 找到第一篇文章
            first_item = page.query_selector('.news-list li')
            if not first_item:
                print("[Error] 未找到文章列表")
                return None
            
            # 获取文章链接
            link_el = first_item.query_selector('h3 a')
            if not link_el:
                print("[Error] 未找到文章链接")
                return None
            
            article_title = link_el.inner_text().strip()
            article_link = link_el.get_attribute('href')
            
            # 如果是相对路径，补全域名
            if article_link.startswith('/'):
                article_link = f"https://weixin.sogou.com{article_link}"
            
            print(f"\n[点击] 第一篇文章：{article_title}")
            print(f"[链接] {article_link[:80]}...")
            
            # 提取文章内容
            result = extract_article_content(page, article_link)
            
            if result:
                result['brand'] = brand
                result['search_keyword'] = keyword
            
            return result
            
        except Exception as e:
            print(f"[Error] {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            browser.close()


def save_as_markdown(article, output_path):
    """将文章保存为 Markdown 格式"""
    
    md_content = f"""# {article.get('title', '无标题')}

**品牌**: {article.get('brand', 'N/A')}
**作者**: {article.get('author', 'N/A')}
**发布时间**: {article.get('publish_time', 'N/A')}
**抓取时间**: {article.get('crawl_time', 'N/A')}
**原文链接**: {article.get('url', 'N/A')}

---

## 正文内容

{article.get('content', '无内容')}

---

*本文由 AI 自动抓取并整理*
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n[Saved] Markdown 已保存：{output_path}")
    return output_path


def main():
    print("="*60)
    print("微信公众号文章全文抓取")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    # 测试：搜索并抓取杰士邦第一篇文章
    result = search_and_click_first_article('杰士邦', '杰士邦新广告')
    
    if result:
        # 保存为 Markdown
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        md_file = f'article_{timestamp}.md'
        save_as_markdown(result, md_file)
        
        # 同时保存 JSON
        json_file = f'article_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[Saved] JSON 已保存：{json_file}")
        
        # 返回内容预览
        print("\n" + "="*60)
        print("[内容预览]")
        print("="*60)
        content = result.get('content', '')
        if len(content) > 1000:
            print(content[:1000] + "\n... (内容过长，已截断)")
        else:
            print(content)
        
        return result, md_file
    else:
        print("\n[Error] 抓取失败")
        return None, None


if __name__ == '__main__':
    main()
