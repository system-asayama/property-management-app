#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マイグレーションスクリプト: T_シミュレーションテーブルに減価償却費フィールドを追加
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
    print("T_シミュレーションテーブルに減価償却費カラムを追加")
    print("=" * 60)
    
    # データベース接続
    database_url = get_database_url()
    print(f"\nデータベースURL: {database_url.split('@')[0] if '@' in database_url else database_url}...")
    
    engine = create_engine(database_url, echo=False)
    
    try:
        # カラムが存在するか確認
        if column_exists(engine, 'T_シミュレーション', '減価償却費'):
            print("\n✓ 減価償却費カラムは既に存在します")
            return
        
        # カラムを追加
        print("\n減価償却費カラムを追加します...")
        
        with engine.connect() as conn:
            # トランザクション開始
            trans = conn.begin()
            
            try:
                # データベースの種類を判定
                if 'postgresql' in database_url:
                    # PostgreSQL
                    conn.execute(text("""
                        ALTER TABLE "T_シミュレーション" 
                        ADD COLUMN "減価償却費" NUMERIC(15, 2) DEFAULT 0
                    """))
                else:
                    # SQLite
                    conn.execute(text("""
                        ALTER TABLE "T_シミュレーション" 
                        ADD COLUMN "減価償却費" REAL DEFAULT 0
                    """))
                
                # コミット
                trans.commit()
                print("✓ 減価償却費カラムを追加しました")
                
            except Exception as e:
                # ロールバック
                trans.rollback()
                print(f"\nエラーが発生しました: {e}")
                raise
        
        print("\n" + "=" * 60)
        print("✓ マイグレーションが正常に完了しました")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nエラー: {e}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == '__main__':
    main()
