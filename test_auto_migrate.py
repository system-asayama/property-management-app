#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動マイグレーション機能のテストスクリプト
"""

import os
import sys

# テスト用のSQLiteデータベースを使用
os.environ['DATABASE_URL'] = 'sqlite:///test_migration.db'

# アプリケーションをインポート
sys.path.insert(0, '.')

print("=" * 60)
print("自動マイグレーション機能のテスト")
print("=" * 60)

try:
    from app.utils.auto_migrate import auto_migrate_all
    from app.db import engine
    from app import models_login, models_property
    
    print("\n✅ モジュールのインポート成功")
    
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
    
    print(f"\n対象テーブル数: {len(migration_targets)}")
    
    # 自動マイグレーション実行
    result = auto_migrate_all(engine, migration_targets)
    
    if result:
        print("\n" + "=" * 60)
        print("✅ 自動マイグレーション機能のテスト成功")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("✗ 自動マイグレーション機能のテスト失敗")
        print("=" * 60)
        sys.exit(1)
        
except Exception as e:
    print(f"\n✗ エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    # テスト用データベースを削除
    if os.path.exists('test_migration.db'):
        os.remove('test_migration.db')
        print("\n✅ テスト用データベースを削除しました")
