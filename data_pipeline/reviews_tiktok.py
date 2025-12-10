# data_pipeline/reviews_tiktok.py
# -*- coding: utf-8 -*-
"""
处理 TikTok Shop 商品评论：
- 输入：原始 DataFrame（例：评分 / 评论 / 日期 / SKU）
- 输出（clean_tiktok_reviews）：
    - rating
    - comment_text
    - date
    - sku
- summarize_tiktok_reviews：
    - rating_distribution
    - top5_sku_by_reviews
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd


COLUMN_ALIASES: Dict[str, List[str]] = {
    "rating": ["评分", "星级", "rating", "star"],
    "comment_text": ["评论", "评论内容", "content", "review_text"],
    "date": ["日期", "时间", "评论时间", "date"],
    "sku": ["SKU", "sku", "变体", "规格"],
}


def _first_match(cols: List[str], candidates: List[str]) -> str | None:
    for c in candidates:
        if c in cols:
            return c
    return None


def clean_tiktok_reviews(raw_df: pd.DataFrame) -> pd.DataFrame:
    if raw_df is None or raw_df.empty:
        raise ValueError("TikTok 商品评论数据为空")

    cols = list(raw_df.columns)
    col_rating = _first_match(cols, COLUMN_ALIASES["rating"])
    col_text = _first_match(cols, COLUMN_ALIASES["comment_text"])
    col_date = _first_match(cols, COLUMN_ALIASES["date"])
    col_sku = _first_match(cols, COLUMN_ALIASES["sku"])

    if col_text is None:
        raise ValueError(f"找不到 TikTok 评论内容列。当前列名：{cols}")

    df = pd.DataFrame()
    df["comment_text"] = raw_df[col_text].astype(str).str.strip()

    if col_rating is not None:
        df["rating"] = (
            pd.to_numeric(raw_df[col_rating], errors="coerce")
            .clip(lower=1, upper=5)
            .fillna(0)
        )
    else:
        df["rating"] = 0

    if col_date is not None:
        df["date"] = pd.to_datetime(raw_df[col_date], errors="coerce")
    else:
        df["date"] = pd.NaT

    if col_sku is not None:
        df["sku"] = raw_df[col_sku].astype(str).fillna("")
    else:
        df["sku"] = ""

    df = df[df["comment_text"].str.len() > 0].copy()
    return df.reset_index(drop=True)


def summarize_tiktok_reviews(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {
            "rating_distribution": {},
            "top5_sku_by_reviews": [],
        }

    rating_counts = (
        df["rating"]
        .round()
        .value_counts()
        .sort_index()
        .to_dict()
    )

    if "sku" in df.columns:
        sku_counts = (
            df.groupby("sku")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(5)
        )
        top5_sku = sku_counts.to_dict(orient="records")
    else:
        top5_sku = []

    return {
        "rating_distribution": rating_counts,
        "top5_sku_by_reviews": top5_sku,
    }
