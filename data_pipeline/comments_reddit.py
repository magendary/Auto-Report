# data_pipeline/comments_reddit.py
# -*- coding: utf-8 -*-
"""
处理 Reddit 评论数据：
- 输入：原始 DataFrame（支持多种导出格式）
- 输出：标准字段：
    - comment_text
    - score      （相当于点赞数）
    - created_at
    - source = "reddit"
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd


COLUMN_ALIASES: Dict[str, List[str]] = {
    "comment_text": ["body", "comment", "text", "selftext", "内容"],
    "score": ["score", "ups", "upvotes", "点赞数"],
    "created_at": ["created_utc", "created_at", "time", "日期", "timestamp"],
}


def _resolve_columns(df: pd.DataFrame) -> Dict[str, str]:
    resolved: Dict[str, str] = {}
    cols = list(df.columns)

    for std_name, candidates in COLUMN_ALIASES.items():
        for c in candidates:
            if c in cols:
                resolved[std_name] = c
                break

    if "comment_text" not in resolved:
        raise ValueError(
            f"无法在 Reddit 评论表中找到评论文本列。当前列名：{cols}"
        )

    return resolved


def clean_reddit_comments(raw_df: pd.DataFrame) -> pd.DataFrame:
    if raw_df is None or raw_df.empty:
        raise ValueError("Reddit 评论数据为空")

    col_map = _resolve_columns(raw_df)

    df = pd.DataFrame()
    df["comment_text"] = raw_df[col_map["comment_text"]].astype(str).str.strip()

    if "score" in col_map:
        df["score"] = (
            pd.to_numeric(raw_df[col_map["score"]], errors="coerce")
            .fillna(0)
            .astype(int)
        )
    else:
        df["score"] = 0

    if "created_at" in col_map:
        df["created_at"] = pd.to_datetime(
            raw_df[col_map["created_at"]], errors="coerce"
        )
    else:
        df["created_at"] = pd.NaT

    df = df[df["comment_text"].str.len() > 0].copy()
    df["source"] = "reddit"
    return df.reset_index(drop=True)


def summarize_reddit_comments(df: pd.DataFrame) -> dict:
    """
    基础统计：
    - total_comments
    - total_score
    - avg_score
    - top_by_score
    """
    if df is None or df.empty:
        return {
            "basic_stats": {
                "total_comments": 0,
                "total_score": 0,
                "avg_score": 0.0,
            },
            "top_by_score": [],
        }

    total_comments = int(len(df))
    total_score = int(df["score"].sum())
    avg_score = float(df["score"].mean()) if total_comments else 0.0

    basic_stats = {
        "total_comments": total_comments,
        "total_score": total_score,
        "avg_score": avg_score,
    }

    sub = (
        df.sort_values("score", ascending=False)
        .head(50)[["comment_text", "score"]]
        .copy()
    )
    top_by_score = sub.to_dict(orient="records")

    return {
        "basic_stats": basic_stats,
        "top_by_score": top_by_score,
    }
