#!/usr/bin/env python3
"""
完全自動マイグレーションのテスト

Base.metadata.create_all() + auto_migrate_all()の組み合わせをテストします。
"""

import os
import sys

# アプリケーションのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import inspect
from app.db import Base, engine
from app import models_login, models_auth, models_property
from app.utils.auto_migrate import auto_migrate_all

def test_full_auto_migration():
    """完全自動マイグレーションをテスト"""
    print("=" * 80)
    print("完全自動マイグレーションのテスト")
    print("=" * 80)
    
    # ステップ1: Base.metadata.create_all()を実行
    print("\n【ステップ1】Base.metadata.create_all()を実行（テーブル作成）")
    print("-" * 80)
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ テーブル作成成功")
    except Exception as e:
        print(f"❌ テーブル作成失敗: {e}")
        return False
    
    # ステップ2: auto_migrate_all()を実行
    print("\n【ステップ2】auto_migrate_all()を実行（カラム追加）")
    print("-" * 80)
    
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
        (models_property.TBukkenKeihi, 'T_物件経費'),
        (models_property.THeyaKeihi, 'T_部屋経費'),
    ]
    
    try:
        auto_migrate_all(engine, migration_targets)
        print("✅ 自動マイグレーション成功")
    except Exception as e:
        print(f"❌ 自動マイグレーション失敗: {e}")
        return False
    
    # ステップ3: 検証
    print("\n【ステップ3】すべてのカラムが存在するか検証")
    print("-" * 80)
    
    inspector = inspect(engine)
    all_ok = True
    
    for table_name, table in Base.metadata.tables.items():
        expected_cols = {col.name for col in table.columns}
        actual_cols_data = inspector.get_columns(table_name)
        actual_cols = {col['name'] for col in actual_cols_data}
        
        missing_cols = expected_cols - actual_cols
        
        if missing_cols:
            print(f"❌ テーブル '{table_name}' に不足カラム: {missing_cols}")
            all_ok = False
        else:
            print(f"✅ テーブル '{table_name}': すべてのカラムが存在（{len(expected_cols)}カラム）")
    
    # 結果サマリー
    print("\n" + "=" * 80)
    if all_ok:
        print("✅ すべてのテーブルとカラムが正しく自動作成されています")
        print("\n【結論】")
        print("Base.metadata.create_all() + auto_migrate_all()の組み合わせにより、")
        print("すべてのテーブルとカラムが自動作成されます。")
    else:
        print("❌ 一部のテーブルまたはカラムが不足しています")
    print("=" * 80)
    
    return all_ok

if __name__ == '__main__':
    success = test_full_auto_migration()
    sys.exit(0 if success else 1)
