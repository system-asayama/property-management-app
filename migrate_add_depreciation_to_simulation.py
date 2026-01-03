#!/usr/bin/env python3
"""
マイグレーションスクリプト: T_シミュレーションテーブルに減価償却費フィールドを追加

実行方法:
    python migrate_add_depreciation_to_simulation.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# データベース接続情報を取得
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("エラー: DATABASE_URLが設定されていません")
    sys.exit(1)

# HerokuのPostgreSQLのURLを修正（postgres:// -> postgresql://）
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"データベースに接続します...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # トランザクション開始
        trans = conn.begin()
        
        try:
            # 減価償却費カラムが存在するか確認
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'T_シミュレーション' 
                AND column_name = '減価償却費'
            """))
            
            if result.fetchone():
                print("減価償却費カラムは既に存在します")
            else:
                # 減価償却費カラムを追加
                print("T_シミュレーションテーブルに減価償却費カラムを追加します...")
                conn.execute(text("""
                    ALTER TABLE "T_シミュレーション" 
                    ADD COLUMN "減価償却費" NUMERIC(15, 2) DEFAULT 0
                """))
                print("✓ 減価償却費カラムを追加しました")
            
            # コミット
            trans.commit()
            print("\n✓ マイグレーションが正常に完了しました")
            
        except Exception as e:
            # ロールバック
            trans.rollback()
            print(f"\nエラーが発生しました: {e}")
            raise
            
except Exception as e:
    print(f"データベース接続エラー: {e}")
    sys.exit(1)
finally:
    engine.dispose()
