#!/usr/bin/env python3
"""Validate the four-volume rewrite before merging."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

EXPECTED = {
    "卷一_献俘疑云.txt": [
        "第一章　凯旋献俘",
        "第二章　鸿胪夜宴",
        "第三章　通天宫落书",
        "第四章　司天台密室",
        "第五章　狄公勘浑仪",
        "第六章　铜匦第七书",
        "第七章　东宫惊变",
        "第八章　梁王府夜宴",
        "第九章　推事院旧档",
        "第十章　天津桥伏杀",
        "第十一章　通天宫火起",
        "第十二章　武皇临轩",
        "第十三章　太子自辩",
        "第十四章　天书真相",
        "第十五章　河北急报",
    ],
    "卷二_河北狼烟.txt": [
        "第十六章　狄公督河北",
        "第十七章　白狼水覆舟",
        "第十八章　营州降将",
        "第十九章　杀良冒功",
        "第二十章　军仓空账",
        "第二十一章　燕山夜猎",
        "第二十二章　崇州疑城",
        "第二十三章　元芳陷阵",
        "第二十四章　如燕探营",
        "第二十五章　曾泰断粮案",
        "第二十六章　突勒使者",
        "第二十七章　默啜反间",
        "第二十八章　幽州会战",
        "第二十九章　献俘余波",
        "第三十章　凯旋受谗",
    ],
    "卷三_洛水纸人.txt": [
        "第三十一章　纸人夜哭",
        "第三十二章　韩矩之死",
        "第三十三章　中元鬼轿",
        "第三十四章　纸马铺",
        "第三十五章　白雀观",
        "第三十六章　太平公主",
        "第三十七章　罗织旧经",
        "第三十八章　嵩山投简",
        "第三十九章　投龙坛",
        "第四十章　金简真伪",
        "第四十一章　武三思之谋",
        "第四十二章　太子蒙冤",
        "第四十三章　上阳宫对质",
        "第四十四章　纸雀归天",
        "第四十五章　江州来客",
    ],
    "卷四_上阳残照.txt": [
        "第四十六章　奉宸府",
        "第四十七章　二张弄权",
        "第四十八章　张柬之忧",
        "第四十九章　狄公病笃",
        "第五十章　太子监国",
        "第五十一章　突勒请和",
        "第五十二章　武三思复起",
        "第五十三章　太平再谋",
        "第五十四章　上阳宫夜诏",
        "第五十五章　金简再现",
        "第五十六章　狄公谏武",
        "第五十七章　群臣廷辩",
        "第五十八章　狄公辞官",
        "第五十九章　荐张柬之",
        "第六十章　上阳残照",
    ],
}

MODERN_WORDS = [
    "逻辑", "系统", "方案", "团队", "情绪", "信息差", "复盘", "搞定",
    "没问题", "执行", "流程", "项目", "数据", "反馈", "目标", "效率",
    "认知", "心理", "机制",
]

DEAD_NAMES = [
    "吉利可汗", "沙尔汗", "亚喀", "塞班", "差斥", "娜鲁", "武攸德",
    "来俊臣", "周兴", "金木兰", "肖清芳", "袁天罡", "虺文忠",
]


def char_count(text: str) -> int:
    return len(re.sub(r"\s", "", text))


def split_chapters(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?m)^(第[一二三四五六七八九十百零〇0-9]+章.*)$", text))
    result: list[tuple[str, str]] = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        result.append((match.group(1).strip(), text[start:end].strip()))
    return result


def main() -> int:
    errors: list[str] = []
    grand_total = 0

    for filename, expected_titles in EXPECTED.items():
        path = ROOT / filename
        if not path.exists():
            errors.append(f"{filename}: 文件不存在")
            continue

        text = path.read_text(encoding="utf-8")
        total = char_count(text)
        grand_total += total
        chapters = split_chapters(text)
        titles = [title for title, _ in chapters]

        print(f"\n{filename}: {total} 字，{len(chapters)} 章")
        if titles != expected_titles:
            errors.append(f"{filename}: 章题不符或缺失\n  实际: {titles}\n  期望: {expected_titles}")

        for title, body in chapters:
            length = char_count(body)
            marker = "OK" if length >= 6500 else "TOO SHORT"
            print(f"  {title}: {length} 字 [{marker}]")
            if length < 6500:
                errors.append(f"{filename} / {title}: 仅 {length} 字，低于 6500")

        for word in MODERN_WORDS:
            count = text.count(word)
            if count:
                errors.append(f"{filename}: 出现现代词“{word}” {count} 次")

        laofu = text.count("老夫")
        print(f"  “老夫”出现 {laofu} 次")
        if laofu:
            errors.append(f"{filename}: “老夫”出现 {laofu} 次，应为 0")

        for name in DEAD_NAMES:
            count = text.count(name)
            if count:
                print(f"  已死人物提及“{name}” {count} 次（需人工核验是否仅为追述）")

    print(f"\n四卷合计：{grand_total} 字")
    if grand_total < 420_000:
        errors.append(f"四卷合计仅 {grand_total} 字，低于 42 万字")
    if grand_total > 560_000:
        errors.append(f"四卷合计 {grand_total} 字，超过 56 万字")

    if errors:
        print("\n发现问题：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\n全部硬指标通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
