#!/usr/bin/env python3
"""
自動作成機能の検証スクリプト

すべてのテーブルとカラムが自動作成されることを検証します。
"""

import os
import sys

# アプリケーションのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import inspect
from app.db import Base, engine
from app import models_login, models_auth, models_property

def verify_auto_creation():
    """自動作成機能を検証"""
    print("=" * 80)
    print("自動作成機能の検証")
    print("=" * 80)
    
    # ステップ1: モデルから期待されるテーブルとカラムを取得
    print("\n【ステップ1】モデル定義から期待されるテーブルとカラムを取得")
    print("-" * 80)
    
    expected_tables = {}
    for table_name, table in Base.metadata.tables.items():
        expected_tables[table_name] = {col.name for col in table.columns}
        print(f"✓ {table_name}: {len(expected_tables[table_name])}カラム")
    
    print(f"\n合計: {len(expected_tables)}テーブル")
    
    # ステップ2: Base.metadata.create_all()を実行
    print("\n【ステップ2】Base.metadata.create_all()を実行")
    print("-" * 80)
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ テーブル作成成功")
    except Exception as e:
        print(f"❌ テーブル作成失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ステップ3: データベースから実際のテーブルとカラムを取得
    print("\n【ステップ3】データベースから実際のテーブルとカラムを取得")
    print("-" * 80)
    
    inspector = inspect(engine)
    actual_tables = {}
    
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        actual_tables[table_name] = {col['name'] for col in columns}
        print(f"✓ {table_name}: {len(actual_tables[table_name])}カラム")
    
    print(f"\n合計: {len(actual_tables)}テーブル")
    
    # ステップ4: 比較
    print("\n【ステップ4】期待値と実際の値を比較")
    print("-" * 80)
    
    all_ok = True
    
    # テーブルの存在チェック
    for table_name in expected_tables:
        if table_name not in actual_tables:
            print(f"❌ テーブル '{table_name}' が存在しません")
            all_ok = False
        else:
            # カラムの存在チェック
            expected_cols = expected_tables[table_name]
            actual_cols = actual_tables[table_name]
            
            missing_cols = expected_cols - actual_cols
            extra_cols = actual_cols - expected_cols
            
            if missing_cols:
                print(f"❌ テーブル '{table_name}' に不足カラム: {missing_cols}")
                all_ok = False
            
            if extra_cols:
                print(f"⚠️  テーブル '{table_name}' に余分なカラム: {extra_cols}")
            
            if not missing_cols and not extra_cols:
                print(f"✅ テーブル '{table_name}': すべてのカラムが一致")
    
    # データベースにのみ存在するテーブル
    extra_tables = set(actual_tables.keys()) - set(expected_tables.keys())
    if extra_tables:
        print(f"\n⚠️  データベースにのみ存在するテーブル: {extra_tables}")
    
    # 結果サマリー
    print("\n" + "=" * 80)
    if all_ok:
        print("✅ すべてのテーブルとカラムが正しく自動作成されています")
    else:
        print("❌ 一部のテーブルまたはカラムが不足しています")
    print("=" * 80)
    
    return all_ok

if __name__ == '__main__':
    success = verify_auto_creation()
    sys.exit(0 if success else 1)
