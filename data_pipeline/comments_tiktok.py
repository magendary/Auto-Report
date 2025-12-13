# data_pipeline/comments_tiktok.py
# -*- coding: utf-8 -*-
"""
处理 TikTok 视频评论数据：
- 输入：原始 DataFrame（支持中英文列名）
- 输出：标准字段：
    - comment_text  评论内容
    - like_count    点赞数
    - reply_count   回复数量
    - created_at    （可选）时间
    - source        固定为 "tiktok"
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd


# 列名别名表：尽量兼容不同导出的格式
COLUMN_ALIASES: Dict[str, List[str]] = {
    "comment_text": ["评论内容", "评论", "content", "comment", "text", "body"],
    "created_at": ["发布时间", "时间", "创建时间", "created_at", "timestamp"],
    "like_count": ["点赞数", "点赞", "likes", "like_count"],
    "reply_count": ["回复数量", "回复数", "评论回复数", "replies", "reply_count"],
}


def _resolve_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    根据别名表，在原始列里寻找对应字段。
    返回：标准名 -> 原始列名 的映射。
    """
    resolved: Dict[str, str] = {}
    cols = list(df.columns)

    for std_name, candidates in COLUMN_ALIASES.items():
        for c in candidates:
            if c in cols:
                resolved[std_name] = c
                break

    if "comment_text" not in resolved:
        raise ValueError(
            f"无法在 TikTok 评论表中找到『评论内容』列。当前列名：{cols}"
        )

    return resolved


def clean_tiktok_comments(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    清洗 TikTok 视频评论，只保留：
    - comment_text
    - like_count
    - reply_count
    （可选）created_at
    """
    if raw_df is None or raw_df.empty:
        raise ValueError("TikTok 评论数据为空")

    col_map = _resolve_columns(raw_df)

    df = pd.DataFrame()
    df["comment_text"] = raw_df[col_map["comment_text"]].astype(str).str.strip()

    # 点赞数
    if "like_count" in col_map:
        df["like_count"] = (
            pd.to_numeric(raw_df[col_map["like_count"]], errors="coerce")
            .fillna(0)
            .astype(int)
        )
    else:
        df["like_count"] = 0

    # 回复数量
    if "reply_count" in col_map:
        df["reply_count"] = (
            pd.to_numeric(raw_df[col_map["reply_count"]], errors="coerce")
            .fillna(0)
            .astype(int)
        )
    else:
        df["reply_count"] = 0

    # 发布时间（可选）
    if "created_at" in col_map:
        df["created_at"] = pd.to_datetime(
            raw_df[col_map["created_at"]], errors="coerce"
        )
    else:
        df["created_at"] = pd.NaT

    # 去掉空白评论
    df = df[df["comment_text"].str.len() > 0].copy()
    df["source"] = "tiktok"

    return df.reset_index(drop=True)


def summarize_tiktok_comments(df: pd.DataFrame) -> dict:
    """
    对清洗后的 TikTok 评论做一个「轻量结构化摘要」，给后面 AI 用。
    不调用大模型，只做统计：
    - basic_stats：总评论数 / 点赞总数 / 平均点赞
    - top_by_likes：按点赞排序的 Top20 评论
    - top_by_replies：按回复数排序的 Top20 评论
    """
    if df is None or df.empty:
        return {
            "basic_stats": {
                "total_comments": 0,
                "total_likes": 0,
                "total_replies": 0,
                "avg_likes": 0.0,
                "avg_replies": 0.0,
            },
            "top_by_likes": [],
            "top_by_replies": [],
        }

    total_comments = int(len(df))
    total_likes = int(df["like_count"].sum())
    total_replies = int(df["reply_count"].sum())

    basic_stats = {
        "total_comments": total_comments,
        "total_likes": total_likes,
        "total_replies": total_replies,
        "avg_likes": float(df["like_count"].mean()) if total_comments else 0.0,
        "avg_replies": float(df["reply_count"].mean()) if total_comments else 0.0,
    }

    def _top_records(sort_col: str, n: int = 20) -> List[dict]:
        if sort_col not in df.columns:
            return []
        sub = (
            df.sort_values(sort_col, ascending=False)
            .head(n)[["comment_text", "like_count", "reply_count"]]
            .copy()
        )
        return sub.to_dict(orient="records")

    summary = {
        "basic_stats": basic_stats,
        "top_by_likes": _top_records("like_count", 20),
        "top_by_replies": _top_records("reply_count", 20),
    }

    return summary
