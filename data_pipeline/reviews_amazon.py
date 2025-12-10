# data_pipeline/reviews_amazon.py
# -*- coding: utf-8 -*-
"""
处理 Amazon 商品评论：
- 输入：原始 DataFrame（xlsx/csv）
- 输出（clean_amazon_reviews）：
    - asin         产品 ASIN（如果有）
    - sku          变体 / SKU（如果有）
    - rating       评分
    - title        评论标题（可选）
    - comment_text 评论内容
    - date         评论日期
- summarize_amazon_reviews：
    - 评分分布
    - top5_products         按评论数排序的产品
    - top5_reviewers        （如有用户字段）
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd


COLUMN_ALIASES: Dict[str, List[str]] = {
    "asin": ["ASIN", "asin", "父ASIN", "商品ASIN"],
    "sku": ["SKU", "变体", "sku", "Variation"],
    "rating": ["评分", "星级", "rating", "star"],
    "title": ["标题", "review_title", "title"],
    "comment_text": ["评论内容", "评论", "review_text", "review"],
    "date": ["日期", "评论日期", "date", "review_date"],
    "reviewer": ["用户昵称", "用户名", "reviewer", "customer"],
}


def _first_match(cols: List[str], candidates: List[str]) -> str | None:
    for c in candidates:
        if c in cols:
            return c
    return None


def clean_amazon_reviews(raw_df: pd.DataFrame) -> pd.DataFrame:
    if raw_df is None or raw_df.empty:
        raise ValueError("Amazon 评论数据为空")

    cols = list(raw_df.columns)
    col_asin = _first_match(cols, COLUMN_ALIASES["asin"])
    col_sku = _first_match(cols, COLUMN_ALIASES["sku"])
    col_rating = _first_match(cols, COLUMN_ALIASES["rating"])
    col_title = _first_match(cols, COLUMN_ALIASES["title"])
    col_text = _first_match(cols, COLUMN_ALIASES["comment_text"])
    col_date = _first_match(cols, COLUMN_ALIASES["date"])
    col_reviewer = _first_match(cols, COLUMN_ALIASES["reviewer"])

    if col_text is None:
        raise ValueError(f"找不到 Amazon 评论文本列。当前列名：{cols}")

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

    if col_title is not None:
        df["title"] = raw_df[col_title].astype(str).str.strip()
    else:
        df["title"] = ""

    if col_date is not None:
        df["date"] = pd.to_datetime(raw_df[col_date], errors="coerce")
    else:
        df["date"] = pd.NaT

    if col_asin is not None:
        df["asin"] = raw_df[col_asin].astype(str).fillna("UNKNOWN")
    else:
        df["asin"] = "UNKNOWN"

    if col_sku is not None:
        df["sku"] = raw_df[col_sku].astype(str).fillna("")
    else:
        df["sku"] = ""

    if col_reviewer is not None:
        df["reviewer"] = raw_df[col_reviewer].astype(str).fillna("")
    else:
        df["reviewer"] = ""

    # 去掉空评论
    df = df[df["comment_text"].str.len() > 0].copy()
    return df.reset_index(drop=True)


def summarize_amazon_reviews(df: pd.DataFrame) -> dict:
    """
    结构化摘要：
    - rating_distribution: 各星级数量
    - top5_products: 按评论数排序的 asin
    - top5_reviewers: 按评论数排序的 reviewer
    """
    if df is None or df.empty:
        return {
            "rating_distribution": {},
            "top5_products": [],
            "top5_reviewers": [],
        }

    # 评分分布
    rating_counts = (
        df["rating"]
        .round()
        .value_counts()
        .sort_index()
        .to_dict()
    )

    # 产品 Top5（按评论数）
    if "asin" in df.columns:
        prod_counts = (
            df.groupby("asin")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(5)
        )
        top5_products = prod_counts.to_dict(orient="records")
    else:
        top5_products = []

    # 评论者 Top5
    if "reviewer" in df.columns and df["reviewer"].astype(str).str.len().gt(0).any():
        rev_counts = (
            df.groupby("reviewer")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(5)
        )
        top5_reviewers = rev_counts.to_dict(orient="records")
    else:
        top5_reviewers = []

    return {
        "rating_distribution": rating_counts,
        "top5_products": top5_products,
        "top5_reviewers": top5_reviewers,
    }
