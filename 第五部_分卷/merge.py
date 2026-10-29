#!/usr/bin/env python3
"""Merge the four revised volumes into the final TXT."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
OUTPUT = PROJECT / "神探狄仁杰Ⅴ_重写稿.txt"

VOLUMES = [
    "卷一_献俘疑云.txt",
    "卷二_河北狼烟.txt",
    "卷三_洛水纸人.txt",
    "卷四_上阳残照.txt",
]


def clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main() -> None:
    parts = [clean((ROOT / name).read_text(encoding="utf-8")) for name in VOLUMES]
    body = "\n\n".join(parts)
    final = f"神探狄仁杰Ⅴ\n\n{body}\n"
    OUTPUT.write_text(final, encoding="utf-8")
    chars = len(re.sub(r"\s", "", final))
    print(f"已生成：{OUTPUT}")
    print(f"总字数（不含空白）：{chars}")


if __name__ == "__main__":
    main()
