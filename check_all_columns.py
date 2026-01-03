#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
すべてのモデルのカラム定義を確認するスクリプト
"""

import os
import sys

# テスト用のSQLiteデータベースを使用
os.environ['DATABASE_URL'] = 'sqlite:///check_columns.db'

# アプリケーションをインポート
sys.path.insert(0, '.')

from app import models_login, models_property
from app.db import Base, engine
from sqlalchemy import inspect

print("=" * 80)
print("すべてのモデルのカラム定義確認")
print("=" * 80)

# テーブルを作成
Base.metadata.create_all(engine)

# マイグレーション対象のモデルとテーブル名のリスト
migration_targets = [
    # models_login
    (models_login.TKanrisha, 'T_管理者'),
    (models_login.TJugyoin, 'T_従業員'),
    (models_login.TTenant, 'T_テナント'),
    (models_login.TTenpo, 'T_店舗'),
    (models_login.TKanrishaTenpo, 'T_管理者_店舗'),
    (models_login.TJugyoinTenpo, 'T_従業員_店舗'),
    # models_property
    (models_property.TBukken, 'T_物件'),
    (models_property.THeya, 'T_部屋'),
    (models_property.TNyukyosha, 'T_入居者'),
    (models_property.TKeiyaku, 'T_契約'),
    (models_property.TYachinShushi, 'T_家賃収支'),
    (models_property.TGenkashokaku, 'T_減価償却'),
    (models_property.TSimulation, 'T_シミュレーション'),
    (models_property.TSimulationResult, 'T_シミュレーション結果'),
]

inspector = inspect(engine)

for model, table_name in migration_targets:
    print(f"\n{'=' * 80}")
    print(f"テーブル: {table_name}")
    print(f"モデル: {model.__name__}")
    print(f"{'=' * 80}")
    
    # モデル定義のカラム
    model_columns = {col.name for col in model.__table__.columns}
    print(f"\nモデル定義のカラム数: {len(model_columns)}")
    print("カラム一覧:")
    for col_name in sorted(model_columns):
        col = model.__table__.columns[col_name]
        col_type = str(col.type)
        nullable = "NULL" if col.nullable else "NOT NULL"
        default = ""
        if col.server_default is not None:
            default = f" DEFAULT {col.server_default.arg}"
        print(f"  - {col_name:30s} {col_type:20s} {nullable:10s}{default}")
    
    # データベースの実際のカラム
    try:
        db_columns = inspector.get_columns(table_name)
        db_column_names = {col['name'] for col in db_columns}
        print(f"\nデータベースの実際のカラム数: {len(db_column_names)}")
        
        # 差分チェック
        missing_in_db = model_columns - db_column_names
        extra_in_db = db_column_names - model_columns
        
        if missing_in_db:
            print(f"\n⚠️  データベースに不足しているカラム ({len(missing_in_db)}個):")
            for col_name in sorted(missing_in_db):
                print(f"  - {col_name}")
        
        if extra_in_db:
            print(f"\n⚠️  データベースに余分なカラム ({len(extra_in_db)}個):")
            for col_name in sorted(extra_in_db):
                print(f"  - {col_name}")
        
        if not missing_in_db and not extra_in_db:
            print("\n✅ モデル定義とデータベーススキーマが完全に一致しています")
    
    except Exception as e:
        print(f"\n✗ エラー: {e}")

print("\n" + "=" * 80)
print("確認完了")
print("=" * 80)

# テスト用データベースを削除
if os.path.exists('check_columns.db'):
    os.remove('check_columns.db')
