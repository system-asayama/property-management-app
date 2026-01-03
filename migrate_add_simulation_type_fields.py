#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マイグレーションスクリプト: T_シミュレーションテーブルに2パターン対応フィールドを追加
PostgreSQLとSQLiteの両方に対応
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

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

def column_exists(engine, table_name, column_name):
    """カラムが存在するかチェック"""
    inspector = inspect(engine)
    
    # テーブルが存在するか確認
    if table_name not in inspector.get_table_names():
        return False
    
    # カラムが存在するか確認
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def main():
    """メイン処理"""
    print("=" * 60)
    print("T_シミュレーションテーブルに2パターン対応フィールドを追加")
    print("=" * 60)
    
    # データベース接続
    database_url = get_database_url()
    print(f"\nデータベースURL: {database_url.split('@')[0] if '@' in database_url else database_url}...")
    
    engine = create_engine(database_url, echo=False)
    
    try:
        # データベースの種類を判定
        is_postgresql = 'postgresql' in database_url
        
        with engine.connect() as conn:
            # トランザクション開始
            trans = conn.begin()
            
            try:
                # 1. シミュレーション種別カラムを追加
                if not column_exists(engine, 'T_シミュレーション', 'シミュレーション種別'):
                    print("\n1. シミュレーション種別カラムを追加します...")
                    if is_postgresql:
                        conn.execute(text("""
                            ALTER TABLE "T_シミュレーション" 
                            ADD COLUMN "シミュレーション種別" VARCHAR(20) DEFAULT '物件ベース' NOT NULL
                        """))
                    else:
                        conn.execute(text("""
                            ALTER TABLE "T_シミュレーション" 
                            ADD COLUMN "シミュレーション種別" TEXT DEFAULT '物件ベース' NOT NULL
                        """))
                    print("   ✓ シミュレーション種別カラムを追加しました")
                else:
                    print("\n1. ✓ シミュレーション種別カラムは既に存在します")
                
                # 2. 年間家賃収入カラムを追加
                if not column_exists(engine, 'T_シミュレーション', '年間家賃収入'):
                    print("\n2. 年間家賃収入カラムを追加します...")
                    if is_postgresql:
                        conn.execute(text("""
                            ALTER TABLE "T_シミュレーション" 
                            ADD COLUMN "年間家賃収入" NUMERIC(15, 2)
                        """))
                    else:
                        conn.execute(text("""
                            ALTER TABLE "T_シミュレーション" 
                            ADD COLUMN "年間家賃収入" REAL
                        """))
                    print("   ✓ 年間家賃収入カラムを追加しました")
                else:
                    print("\n2. ✓ 年間家賃収入カラムは既に存在します")
                
                # 3. 部屋数カラムを追加
                if not column_exists(engine, 'T_シミュレーション', '部屋数'):
                    print("\n3. 部屋数カラムを追加します...")
                    if is_postgresql:
                        conn.execute(text("""
                            ALTER TABLE "T_シミュレーション" 
                            ADD COLUMN "部屋数" INTEGER
                        """))
                    else:
                        conn.execute(text("""
                            ALTER TABLE "T_シミュレーション" 
                            ADD COLUMN "部屋数" INTEGER
                        """))
                    print("   ✓ 部屋数カラムを追加しました")
                else:
                    print("\n3. ✓ 部屋数カラムは既に存在します")
                
                # コミット
                trans.commit()
                
                print("\n" + "=" * 60)
                print("✓ マイグレーションが正常に完了しました")
                print("=" * 60)
                print("\n追加されたカラム:")
                print("  - シミュレーション種別 (VARCHAR/TEXT, DEFAULT '物件ベース')")
                print("  - 年間家賃収入 (NUMERIC/REAL)")
                print("  - 部屋数 (INTEGER)")
                
            except Exception as e:
                # ロールバック
                trans.rollback()
                print(f"\nエラーが発生しました: {e}")
                raise
        
    except Exception as e:
        print(f"\nエラー: {e}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == '__main__':
    main()
