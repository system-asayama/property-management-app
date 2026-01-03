#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
不動産管理アプリ - シミュレーション機能用テーブル追加マイグレーション
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from app.models_property import TSimulation, TSimulationResult
from app.db import Base

def get_database_url():
    """環境変数からデータベースURLを取得"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # HerokuのDATABASE_URLはpostgresql://で始まるが、SQLAlchemyはpostgresql+psycopg2://を期待
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    else:
        # デフォルトはSQLite
        database_url = 'sqlite:///app.db'
    return database_url

def table_exists(engine, table_name):
    """テーブルが存在するかチェック"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def main():
    """メイン処理"""
    print("=" * 60)
    print("不動産管理アプリ - シミュレーション機能用テーブル追加")
    print("=" * 60)
    
    # データベース接続
    database_url = get_database_url()
    print(f"\nデータベースURL: {database_url.split('@')[0]}...")
    
    engine = create_engine(database_url, echo=True)
    
    # テーブル作成
    tables_to_create = [
        ('T_シミュレーション', TSimulation),
        ('T_シミュレーション結果', TSimulationResult),
    ]
    
    created_tables = []
    skipped_tables = []
    
    for table_name, model_class in tables_to_create:
        if table_exists(engine, table_name):
            print(f"\n[スキップ] テーブル '{table_name}' は既に存在します")
            skipped_tables.append(table_name)
        else:
            print(f"\n[作成] テーブル '{table_name}' を作成します...")
            model_class.__table__.create(engine)
            created_tables.append(table_name)
            print(f"[完了] テーブル '{table_name}' の作成が完了しました")
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("マイグレーション完了")
    print("=" * 60)
    print(f"作成されたテーブル: {len(created_tables)}個")
    for table in created_tables:
        print(f"  - {table}")
    
    if skipped_tables:
        print(f"\nスキップされたテーブル: {len(skipped_tables)}個")
        for table in skipped_tables:
            print(f"  - {table}")
    
    print("\n✅ すべての処理が完了しました")

if __name__ == '__main__':
    main()
