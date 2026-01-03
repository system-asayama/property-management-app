#!/usr/bin/env python3
"""
経費テーブル作成スクリプト

T_物件経費とT_部屋経費テーブルを手動で作成します。
"""

import os
import sys

# アプリケーションのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import engine, Base
from app.models_property import TBukkenKeihi, THeyaKeihi

def create_expense_tables():
    """経費テーブルを作成"""
    print("=" * 60)
    print("経費テーブル作成スクリプト")
    print("=" * 60)
    
    try:
        # T_物件経費テーブルを作成
        print("\nT_物件経費テーブルを作成中...")
        TBukkenKeihi.__table__.create(bind=engine, checkfirst=True)
        print("✅ T_物件経費テーブルを作成しました")
        
        # T_部屋経費テーブルを作成
        print("\nT_部屋経費テーブルを作成中...")
        THeyaKeihi.__table__.create(bind=engine, checkfirst=True)
        print("✅ T_部屋経費テーブルを作成しました")
        
        print("\n" + "=" * 60)
        print("✅ すべての経費テーブルの作成が完了しました")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    create_expense_tables()
