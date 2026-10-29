#!/usr/bin/env python3
"""Final consistency checks for the merged fifth volume."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
FINAL = PROJECT / "神探狄仁杰Ⅴ_重写稿.txt"
VOLUMES = [
    ROOT / "卷一_献俘疑云.txt",
    ROOT / "卷二_河北狼烟.txt",
    ROOT / "卷三_洛水纸人.txt",
    ROOT / "卷四_上阳残照.txt",
]

EXPECTED_COUNTS = [15, 15, 15, 15]

FORBIDDEN = [
    "老夫",
    "太子年轻",
    "儿臣这个太子",
    "长史司",
    "转运司",
    "书办",
    "驿丞",
    "马票",
    "折冲府挂号",
    "内卫府少卿",
    "春官尚书省",
    "火漆",
    "半串钱",
    "做一笔交易",
    "一笔交易",
    "朕的底线",
    "这是朕的底线",
    "手里的牌",
    "向陛下表态",
    "安排好了",
    "反应极快",
    "依法办",
    "算一笔账",
    "朝堂上的平衡",
    "教坊",
    "回國老",
]

MODERN = [
    "逻辑", "系统", "方案", "团队", "情绪", "信息差", "复盘", "搞定",
    "没问题", "执行", "流程", "项目", "数据", "反馈", "目标", "效率",
    "认知", "心理", "机制", "调查", "处理", "解决", "计划",
]

MIXED_OFFICES = ["天官", "地官", "春官", "夏官", "秋官", "冬官"]


def chars(text: str) -> int:
    return len(re.sub(r"\s", "", text))


def chapters(text: str) -> list[tuple[str, str]]:
    marks = list(re.finditer(r"(?m)^(第[一二三四五六七八九十百零〇0-9]+章.*)$", text))
    out: list[tuple[str, str]] = []
    for i, mark in enumerate(marks):
        start = mark.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((mark.group(1).strip(), text[start:end].strip()))
    return out


def sentence_duplicates(text: str) -> list[tuple[str, int]]:
    sentences = re.split(r"(?<=[。！？；])", re.sub(r"\s", "", text))
    counter = Counter(s.strip() for s in sentences if len(s.strip()) >= 40)
    return [(s, n) for s, n in counter.most_common(20) if n > 1]


def paragraph_duplicates(text: str) -> list[tuple[str, int]]:
    paragraphs = [re.sub(r"\s", "", p) for p in text.split("\n")]
    counter = Counter(p for p in paragraphs if len(p) >= 60)
    return [(p, n) for p, n in counter.most_common(20) if n > 1]


def main() -> int:
    problems: list[str] = []
    warnings: list[str] = []
    all_text = ""

    for i, path in enumerate(VOLUMES):
        if not path.exists():
            problems.append(f"缺少分卷：{path}")
            continue
        text = path.read_text(encoding="utf-8")
        all_text += "\n" + text
        count = chars(text)
        chs = chapters(text)
        print(f"{path.name}: {count} 字，{len(chs)} 章")
        if len(chs) != EXPECTED_COUNTS[i]:
            problems.append(f"{path.name}: 章数为 {len(chs)}，应为 {EXPECTED_COUNTS[i]}")
        for title, body in chs:
            length = chars(body)
            if length < 6500:
                problems.append(f"{path.name} / {title}: 仅 {length} 字")
        if "奉宸府" in text and i <= 1:
            problems.append(f"{path.name}: 圣历二年卷出现奉宸府")

    total = chars(all_text)
    print(f"四卷合计：{total} 字")
    if not 400_000 <= total <= 600_000:
        problems.append(f"总字数 {total} 不在 40 万至 60 万之间")

    for phrase in FORBIDDEN:
        count = all_text.count(phrase)
        if count:
            problems.append(f"禁用表述“{phrase}”出现 {count} 次")

    for word in MODERN:
        count = all_text.count(word)
        if count:
            problems.append(f"现代词“{word}”出现 {count} 次")

    for word in MIXED_OFFICES:
        count = all_text.count(word)
        if count:
            warnings.append(f"武周正名“{word}”出现 {count} 次，需确认无同段混用")

    for phrase in ["大理寺卿", "通天冠", "十二旒", "控鹤监", "奉宸府"]:
        count = all_text.count(phrase)
        if count:
            warnings.append(f"需人工核对“{phrase}”出现 {count} 次")

    dup_sentences = sentence_duplicates(all_text)
    for sentence, n in dup_sentences:
        warnings.append(f"重复长句 {n} 次：{sentence[:80]}")
    dup_paragraphs = paragraph_duplicates(all_text)
    for paragraph, n in dup_paragraphs:
        warnings.append(f"重复长段 {n} 次：{paragraph[:80]}")

    if not FINAL.exists():
        problems.append(f"未生成合并稿：{FINAL}")
    else:
        final_text = FINAL.read_text(encoding="utf-8")
        final_count = chars(final_text)
        print(f"合并稿：{final_count} 字")
        if final_count != total:
            warnings.append(f"合并稿字数 {final_count} 与分卷合计 {total} 不一致（标题行会造成少量差异）")
        final_chapters = chapters(final_text)
        if len(final_chapters) != 60:
            problems.append(f"合并稿章数为 {len(final_chapters)}，应为 60")

    if warnings:
        print("\n需人工复核：")
        for item in warnings[:80]:
            print(f"- {item}")

    if problems:
        print("\n未通过：")
        for item in problems:
            print(f"- {item}")
        return 1

    print("\n自动检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
