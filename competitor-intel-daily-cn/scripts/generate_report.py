#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


BRANDS = ["杜蕾斯", "冈本", "杰士邦", "大象", "名流", "羽感", "BeU"]
BRAND_KEY_MAP = {
    "杜蕾斯": "durex",
    "冈本": "okamoto",
    "杰士邦": "jissbon",
    "大象": "donless",
    "名流": "mingliu",
    "羽感": "yugan",
    "BeU": "beu",
}
IMPORTANCE_SCORE = {"high": 3, "medium": 2, "low": 1}
CREDIBILITY_SCORE = {"official": 4, "high": 3, "medium": 2, "low": 1}
PRICE_PATTERN = re.compile(r"(\d+(?:\.\d+)?\s*[-~到]\s*\d+(?:\.\d+)?)\s*元")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate competitor-intel daily report from collected JSON items.")
    parser.add_argument("--input", required=True, help="Path to raw collected items JSON.")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--output-dir", help="Override output directory.")
    parser.add_argument("--skip-pdf", action="store_true", help="Do not attempt PDF rendering.")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def render_template(template: str, mapping: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        value = mapping.get(key, "-")
        if isinstance(value, list):
            return ", ".join(str(item) for item in value) if value else "-"
        return str(value) if value not in (None, "") else "-"

    return re.sub(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", replace, template)


def parse_dt(value: str | None) -> datetime:
    if not value:
        return datetime.min
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return datetime.min


def score_item(item: dict[str, Any]) -> tuple[int, int, int, int]:
    return (
        CREDIBILITY_SCORE.get(item.get("credibility", "low"), 1),
        IMPORTANCE_SCORE.get(item.get("importance", "low"), 1),
        int(bool(item.get("summary"))),
        len(item.get("summary", "")),
    )


def dedupe_items(items: list[dict[str, Any]], threshold: float) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    unique_by_url: dict[str, dict[str, Any]] = {}
    duplicates: list[dict[str, str]] = []

    for item in items:
        url = item.get("url", "").strip()
        if not url:
            continue
        existing = unique_by_url.get(url)
        if not existing:
            unique_by_url[url] = item
            continue
        if score_item(item) > score_item(existing):
            duplicates.append({"reason": "same_url", "kept": item.get("title", ""), "removed": existing.get("title", "")})
            unique_by_url[url] = item
        else:
            duplicates.append({"reason": "same_url", "kept": existing.get("title", ""), "removed": item.get("title", "")})

    deduped = list(unique_by_url.values())
    final_items: list[dict[str, Any]] = []
    for candidate in sorted(deduped, key=lambda x: parse_dt(x.get("publish_time")), reverse=True):
        replace_index: int | None = None
        for idx, existing in enumerate(final_items):
            similarity = SequenceMatcher(None, candidate.get("title", ""), existing.get("title", "")).ratio()
            if similarity >= threshold:
                better = candidate if score_item(candidate) > score_item(existing) else existing
                removed = existing if better is candidate else candidate
                duplicates.append({"reason": f"similar_title:{similarity:.2f}", "kept": better.get("title", ""), "removed": removed.get("title", "")})
                if better is candidate:
                    replace_index = idx
                else:
                    replace_index = -1
                break
        if replace_index is None:
            final_items.append(candidate)
        elif replace_index >= 0:
            final_items[replace_index] = candidate

    final_items.sort(key=lambda x: (parse_dt(x.get("publish_time")), score_item(x)), reverse=True)
    return final_items, duplicates


def summarize_brand(items: list[dict[str, Any]]) -> dict[str, str]:
    if not items:
        return {
            "update": "今日未捕获到高置信新动态，建议继续观察。",
            "price": "暂无有效价格变化样本。",
            "launch": "暂无明确新品/活动信号。",
            "reviews": "暂无足够评论样本。",
        }

    sorted_items = sorted(items, key=lambda x: (IMPORTANCE_SCORE.get(x.get("importance", "low"), 1), parse_dt(x.get("publish_time"))), reverse=True)
    top = sorted_items[0]
    price_item = next((item for item in sorted_items if item.get("signal_type") == "价格" or item.get("price_band")), None)
    launch_item = next((item for item in sorted_items if item.get("signal_type") in {"新品", "活动"}), None)
    review_item = next((item for item in sorted_items if item.get("signal_type") in {"评论", "舆情"}), None)
    return {
        "update": top.get("summary") or top.get("title") or "暂无更新。",
        "price": format_price_line(price_item),
        "launch": (launch_item.get("summary") or launch_item.get("title")) if launch_item else "暂无明确新品/活动信号。",
        "reviews": format_review_line(review_item),
    }


def format_price_line(item: dict[str, Any] | None) -> str:
    if not item:
        return "暂无有效价格变化样本。"
    if item.get("price_band"):
        promo = item.get("promotion") or "无明确促销描述"
        return f"价格带 {item['price_band']}；促销方式：{promo}。"
    text = " ".join(filter(None, [item.get("title"), item.get("summary")]))
    match = PRICE_PATTERN.search(text)
    if match:
        return f"价格带 {match.group(1)} 元；需结合页面进一步确认促销细节。"
    return item.get("summary") or item.get("title") or "暂无有效价格变化样本。"


def format_review_line(item: dict[str, Any] | None) -> str:
    if not item:
        return "暂无足够评论样本。"
    negatives = item.get("feedback_negative") or []
    positives = item.get("feedback_positive") or []
    pieces = []
    if positives:
        pieces.append("好评聚焦：" + "、".join(positives[:2]))
    if negatives:
        pieces.append("差评聚焦：" + "、".join(negatives[:3]))
    if not pieces:
        pieces.append(item.get("summary") or item.get("title") or "暂无足够评论样本。")
    return "；".join(pieces) + "。"


def collect_feedback(items: list[dict[str, Any]], key: str) -> list[str]:
    counter: Counter[str] = Counter()
    for item in items:
        for entry in item.get(key, []) or []:
            counter[str(entry)] += 1
    return [text for text, _ in counter.most_common(3)]


def build_recommendations(items: list[dict[str, Any]]) -> tuple[list[str], list[str], list[str]]:
    ecommerce_items = [item for item in items if item.get("source_type") == "电商平台"]
    official_items = [item for item in items if item.get("source_type") == "国家网站"]
    review_items = [item for item in items if item.get("signal_type") in {"评论", "舆情"}]
    opportunities: list[str] = []
    risks: list[str] = []
    actions: list[str] = []

    if ecommerce_items:
        price_bands = [item.get("price_band") for item in ecommerce_items if item.get("price_band")]
        if price_bands:
            opportunities.append(f"重点竞争仍集中在 {price_bands[0]} 价格带，可评估是否切入更高毛利礼盒或女性向细分。")
        opportunities.append("电商主卖点集中在超薄、礼盒与润滑体验，可围绕差异化内容继续验证。")
    else:
        opportunities.append("当前电商样本不足，建议优先补齐平台价格与评论数据。")

    if official_items:
        risks.append("官方/合规源已有更新，需持续核查是否涉及抽检、备案或知识产权风险。")
    else:
        risks.append("今日未见高风险官方异常，但仍需保持对药监和处罚公示的日常监控。")

    negative_terms = collect_feedback(review_items, "feedback_negative")
    if negative_terms:
        risks.append("消费者差评集中在“{}”，若自有产品存在同类短板需尽快核查。".format("、".join(negative_terms[:3])))
        actions.append("把高频差评词纳入周度 VOC 看板，并回看对应 SKU 的售后与评价波动。")
    else:
        actions.append("继续扩大评论样本量，确保差评词与场景标签具备可比性。")

    actions.append("对价格异常或促销增强的链接建立连续监测，至少观察 7 天。")
    actions.append("将新品、联名、达人合作单独归档，便于周报比较品牌动作节奏。")

    while len(opportunities) < 3:
        opportunities.append("继续跟踪平台内容和价格带分布，寻找尚未充分占位的卖点组合。")
    while len(risks) < 3:
        risks.append("注意低价竞争、合规舆情和评论异常增长带来的连锁影响。")
    while len(actions) < 3:
        actions.append("补充样本并复核重点结论，避免因单日数据不足导致误判。")

    return opportunities[:3], risks[:3], actions[:3]


def build_context(items: list[dict[str, Any]], duplicates: list[dict[str, str]], report_date: str, config: dict[str, Any], keywords: dict[str, Any]) -> dict[str, Any]:
    brand_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        brand = item.get("brand")
        if brand in BRANDS:
            brand_groups[brand].append(item)

    brand_context = {brand: summarize_brand(brand_groups.get(brand, [])) for brand in BRANDS}
    ecommerce_items = [item for item in items if item.get("source_type") == "电商平台"]
    official_items = [item for item in items if item.get("source_type") == "国家网站"]
    review_items = [item for item in items if item.get("signal_type") in {"评论", "舆情"}]

    top_items = sorted(items, key=lambda x: (IMPORTANCE_SCORE.get(x.get("importance", "low"), 1), CREDIBILITY_SCORE.get(x.get("credibility", "low"), 1), parse_dt(x.get("publish_time"))), reverse=True)
    takeaways = [f"{item.get('brand', '行业')}：{item.get('summary') or item.get('title')}" for item in top_items[:5]]
    while len(takeaways) < 5:
        takeaways.append("样本不足，建议继续扩充当日高置信来源。")

    rows = ecommerce_items[:3]
    positive_feedback = collect_feedback(review_items, "feedback_positive")
    negative_feedback = collect_feedback(review_items, "feedback_negative")
    controversy = collect_feedback(review_items, "controversy")
    opportunities, risks, actions = build_recommendations(items)

    source_links = [f"[{item.get('platform')}] {item.get('title')} - {item.get('url')}" for item in items[:5]]
    while len(source_links) < 5:
        source_links.append("-")

    official_updates = [item.get("summary") or item.get("title") for item in official_items[:3]]
    while len(official_updates) < 3:
        official_updates.append("今日未发现新增高优先级官方动态。")

    compliance_updates = [
        item.get("summary") or item.get("title")
        for item in items
        if item.get("signal_type") in {"备案", "处罚", "抽检", "召回", "报告"} and item not in official_items
    ][:2]
    while len(compliance_updates) < 2:
        compliance_updates.append("暂无新增企业资质/知识产权/招投标重点信号。")

    capture_times = [parse_dt(item.get("capture_time")) for item in items if item.get("capture_time")]
    if capture_times and max(capture_times) != datetime.min:
        capture_window = f"{min(capture_times).strftime('%Y-%m-%d %H:%M')} 至 {max(capture_times).strftime('%Y-%m-%d %H:%M')}"
        capture_log_summary = f"共采集 {len(items)} 条有效记录；最早抓取 {min(capture_times).strftime('%Y-%m-%d %H:%M')}，最晚抓取 {max(capture_times).strftime('%Y-%m-%d %H:%M')}。"
    else:
        capture_window = f"{report_date} 00:00 至 {report_date} 23:59"
        capture_log_summary = f"共采集 {len(items)} 条有效记录。"

    price_band_summary = "、".join([item.get("price_band") for item in ecommerce_items if item.get("price_band")][:3]) or "暂无稳定价格带结论"
    selling_points = Counter()
    for item in items:
        for word in item.get("keyword_hit", []) or []:
            if word in {"超薄", "礼盒", "玻尿酸", "延时", "聚氨酯", "润滑"}:
                selling_points[word] += 1
    selling_points_summary = "、".join([word for word, _ in selling_points.most_common(3)]) or "超薄、礼盒、润滑体验"
    complaint_summary = "、".join(negative_feedback[:3]) or "暂无稳定差评词结论"

    context: dict[str, Any] = {
        "report_title": config.get("report_title", "避孕套行业竞品情报日报"),
        "report_date": report_date,
        "brand_scope": "、".join(BRANDS),
        "capture_window": capture_window,
        "executive_one_liner": takeaways[0],
        "key_takeaway_1": takeaways[0],
        "key_takeaway_2": takeaways[1],
        "key_takeaway_3": takeaways[2],
        "key_takeaway_4": takeaways[3],
        "key_takeaway_5": takeaways[4],
        "positive_feedback_1": positive_feedback[0] if len(positive_feedback) > 0 else "暂无足够高频好评词",
        "positive_feedback_2": positive_feedback[1] if len(positive_feedback) > 1 else "继续补充评论样本",
        "positive_feedback_3": positive_feedback[2] if len(positive_feedback) > 2 else "关注与卖点的一致性",
        "negative_feedback_1": negative_feedback[0] if len(negative_feedback) > 0 else "暂无足够高频差评词",
        "negative_feedback_2": negative_feedback[1] if len(negative_feedback) > 1 else "继续补充评论样本",
        "negative_feedback_3": negative_feedback[2] if len(negative_feedback) > 2 else "观察是否与价格带相关",
        "controversy_1": controversy[0] if len(controversy) > 0 else "暂无明显争议点",
        "controversy_2": controversy[1] if len(controversy) > 1 else "继续关注平台讨论热度",
        "opportunity_1": opportunities[0],
        "opportunity_2": opportunities[1],
        "opportunity_3": opportunities[2],
        "risk_1": risks[0],
        "risk_2": risks[1],
        "risk_3": risks[2],
        "recommended_action_1": actions[0],
        "recommended_action_2": actions[1],
        "recommended_action_3": actions[2],
        "source_link_1": source_links[0],
        "source_link_2": source_links[1],
        "source_link_3": source_links[2],
        "source_link_4": source_links[3],
        "source_link_5": source_links[4],
        "capture_log_summary": capture_log_summary,
        "keyword_list": "、".join((keywords.get("core") or []) + (keywords.get("brands") or []) + (keywords.get("extensions") or [])[:8]),
        "dedupe_note": f"按 URL 和标题近似度去重，去除 {len(duplicates)} 条重复或近重复记录。",
        "failed_sources_note": "本次样例运行未接入真实抓取器；如外部源抓取失败，请在此处记录失败源与原因。",
        "headline_1": takeaways[0],
        "headline_2": takeaways[1],
        "headline_3": takeaways[2],
        "headline_4": takeaways[3],
        "price_band_summary": price_band_summary,
        "selling_points_summary": selling_points_summary,
        "complaint_summary": complaint_summary,
        "advice_1": actions[0],
        "advice_2": actions[1],
        "advice_3": actions[2],
        "coverage_summary": f"有效记录 {len(items)} 条，去重 {len(duplicates)} 条，覆盖品牌 {len([b for b in BRANDS if brand_groups.get(b)])} 个。",
        "official_status_summary": official_updates[0],
        "exception_summary": "本次为本地样例试跑，未执行真实在线采集。",
    }

    for brand, key in BRAND_KEY_MAP.items():
        summary = brand_context[brand]
        context[f"{key}_update"] = summary["update"]
        context[f"{key}_price"] = summary["price"]
        context[f"{key}_launch"] = summary["launch"]
        context[f"{key}_reviews"] = summary["reviews"]

    for idx in range(3):
        if idx < len(rows):
            item = rows[idx]
            context[f"platform_{idx + 1}"] = item.get("platform", "-")
            context[f"brand_{idx + 1}"] = item.get("brand", "-")
            context[f"product_{idx + 1}"] = item.get("title", "-")
            context[f"price_band_{idx + 1}"] = item.get("price_band", "-")
            context[f"promotion_{idx + 1}"] = item.get("promotion", "-")
            context[f"review_trend_{idx + 1}"] = item.get("review_trend", item.get("summary", "-"))
            context[f"remark_{idx + 1}"] = item.get("remark", item.get("credibility", "-"))
        else:
            for field in ("platform", "brand", "product", "price_band", "promotion", "review_trend", "remark"):
                context[f"{field}_{idx + 1}"] = "-"

    context["official_update_1"] = official_updates[0]
    context["official_update_2"] = official_updates[1]
    context["official_update_3"] = official_updates[2]
    context["compliance_update_1"] = compliance_updates[0]
    context["compliance_update_2"] = compliance_updates[1]
    return context


def maybe_write_pdf_stub(report_md_path: Path, skip_pdf: bool) -> tuple[str, str | None]:
    if skip_pdf:
        return "skipped", None
    pdf_path = report_md_path.with_suffix(".pdf")
    html_path = report_md_path.with_suffix(".html")
    markdown = report_md_path.read_text(encoding="utf-8")
    html = "<html><meta charset='utf-8'><body><pre style='white-space: pre-wrap; font-family: Arial, sans-serif;'>" + markdown.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</pre></body></html>"
    html_path.write_text(html, encoding="utf-8")
    return "not_rendered", str(html_path)


def main() -> None:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parents[1]
    report_date = args.date or datetime.now().strftime("%Y-%m-%d")

    config = load_json(skill_dir / "config.json")
    keywords = load_json(skill_dir / "keywords.json")
    raw_items = load_json(Path(args.input))
    if not isinstance(raw_items, list):
        raise SystemExit("Input JSON must be a list of collected items.")

    cleaned_items, duplicates = dedupe_items(deepcopy(raw_items), float(config.get("dedupe_similarity_threshold", 0.85)))
    context = build_context(cleaned_items, duplicates, report_date, config, keywords)

    output_dir = Path(args.output_dir) if args.output_dir else (skill_dir / "output" / report_date.replace("-", ""))
    output_dir.mkdir(parents=True, exist_ok=True)

    report_template = (skill_dir / "templates" / "report_template.md").read_text(encoding="utf-8")
    summary_template = (skill_dir / "templates" / "summary_template.txt").read_text(encoding="utf-8")
    report_content = render_template(report_template, context)
    summary_content = render_template(summary_template, context)

    basename = f"避孕套行业竞品情报日报_{report_date.replace('-', '')}"
    report_md_path = output_dir / f"{basename}.md"
    summary_path = output_dir / f"{basename}_摘要.txt"
    cleaned_path = output_dir / "cleaned_items.json"
    duplicates_path = output_dir / "duplicates.json"
    manifest_path = output_dir / "report_manifest.json"

    report_md_path.write_text(report_content, encoding="utf-8")
    summary_path.write_text(summary_content, encoding="utf-8")
    dump_json(cleaned_path, cleaned_items)
    dump_json(duplicates_path, duplicates)
    pdf_status, pdf_artifact = maybe_write_pdf_stub(report_md_path, args.skip_pdf)

    manifest = {
        "report_date": report_date,
        "input_items": len(raw_items),
        "cleaned_items": len(cleaned_items),
        "duplicates_removed": len(duplicates),
        "report_markdown": str(report_md_path),
        "summary_text": str(summary_path),
        "pdf_status": pdf_status,
        "pdf_artifact": pdf_artifact,
    }
    dump_json(manifest_path, manifest)

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
