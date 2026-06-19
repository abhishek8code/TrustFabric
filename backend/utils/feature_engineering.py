from __future__ import annotations

import pandas as pd


CATEGORICAL_COLS = ["ProductCD", "card4", "card6", "P_emaildomain", "R_emaildomain", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"]


def build_uid(df: pd.DataFrame) -> pd.Series:
    d1_norm = (df["D1"].fillna(0) - df["TransactionDT"].fillna(0) / 86400).round(0)
    return df["card1"].astype(str) + "_" + df["card2"].astype(str) + "_" + df["addr1"].astype(str) + "_" + d1_norm.astype(str)


def add_uid_aggregations(df: pd.DataFrame, uid: pd.Series) -> pd.DataFrame:
    df = df.copy()
    df["uid"] = uid
    agg = df.groupby("uid")["TransactionAmt"].agg(uid_tx_count="count", uid_amount_mean="mean", uid_amount_std="std").reset_index()
    df = df.merge(agg, on="uid", how="left")
    df["uid_amount_std"] = df["uid_amount_std"].fillna(0)
    d1_norm = df["D1"].fillna(0) - df["TransactionDT"].fillna(0) / 86400
    df["uid_d1_diff"] = (d1_norm - d1_norm.groupby(df["uid"]).transform("mean")).abs()
    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["tx_hour"] = (df["TransactionDT"] // 3600) % 24
    df["tx_day"] = (df["TransactionDT"] // 86400) % 7
    return df


def add_email_match(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["email_match"] = (df["P_emaildomain"] == df["R_emaildomain"]).astype(int)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    uid = build_uid(df)
    df = add_uid_aggregations(df, uid)
    df = add_time_features(df)
    df = add_email_match(df)
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype("category")
    for col in df.columns:
        if df[col].dtype == "object" and col != "uid":
            df[col] = df[col].astype("category")
    return df


def time_based_split(df: pd.DataFrame, train_frac: float = 0.8):
    cutoff = int(len(df) * train_frac)
    return df.iloc[:cutoff], df.iloc[cutoff:]
