#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
不動産管理アプリのテーブルを追加するマイグレーションスクリプト
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# データベースURLを取得
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # デフォルトはSQLite
    DATABASE_URL = 'sqlite:///database/project.db'

print(f"データベースURL: {DATABASE_URL}")

# エンジンを作成
engine = create_engine(DATABASE_URL)

# マイグレーションSQL
migration_sql = """
-- T_物件テーブル
CREATE TABLE IF NOT EXISTS T_物件 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    物件名 VARCHAR(255) NOT NULL,
    物件種別 VARCHAR(50),
    郵便番号 VARCHAR(10),
    住所 VARCHAR(500),
    建築年月 DATE,
    延床面積 DECIMAL(10, 2),
    構造 VARCHAR(50),
    階数 INTEGER,
    部屋数 INTEGER,
    取得価額 DECIMAL(15, 2),
    取得年月日 DATE,
    耐用年数 INTEGER,
    償却方法 VARCHAR(20),
    残存価額 DECIMAL(15, 2),
    備考 TEXT,
    有効 INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES T_テナント(id)
);

-- T_部屋テーブル
CREATE TABLE IF NOT EXISTS T_部屋 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    部屋番号 VARCHAR(50) NOT NULL,
    間取り VARCHAR(50),
    専有面積 DECIMAL(10, 2),
    賃料 DECIMAL(10, 0),
    管理費 DECIMAL(10, 0),
    敷金 DECIMAL(10, 0),
    礼金 DECIMAL(10, 0),
    入居状況 VARCHAR(20) DEFAULT '空室',
    備考 TEXT,
    有効 INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES T_物件(id)
);

-- T_入居者テーブル
CREATE TABLE IF NOT EXISTS T_入居者 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    氏名 VARCHAR(255) NOT NULL,
    フリガナ VARCHAR(255),
    生年月日 DATE,
    電話番号 VARCHAR(20),
    メールアドレス VARCHAR(255),
    緊急連絡先名 VARCHAR(255),
    緊急連絡先電話番号 VARCHAR(20),
    備考 TEXT,
    有効 INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES T_テナント(id)
);

-- T_契約テーブル
CREATE TABLE IF NOT EXISTS T_契約 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    tenant_person_id INTEGER NOT NULL,
    契約開始日 DATE NOT NULL,
    契約終了日 DATE,
    月額賃料 DECIMAL(10, 0) NOT NULL,
    月額管理費 DECIMAL(10, 0),
    敷金 DECIMAL(10, 0),
    礼金 DECIMAL(10, 0),
    契約状況 VARCHAR(20) DEFAULT '契約中',
    備考 TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES T_部屋(id),
    FOREIGN KEY (tenant_person_id) REFERENCES T_入居者(id)
);

-- T_家賃収支テーブル
CREATE TABLE IF NOT EXISTS T_家賃収支 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    対象年月 VARCHAR(7) NOT NULL,
    賃料 DECIMAL(10, 0) NOT NULL,
    管理費 DECIMAL(10, 0),
    入金日 DATE,
    入金状況 VARCHAR(20) DEFAULT '未入金',
    備考 TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES T_契約(id)
);

-- T_減価償却テーブル
CREATE TABLE IF NOT EXISTS T_減価償却 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    年度 INTEGER NOT NULL,
    期首帳簿価額 DECIMAL(15, 2) NOT NULL,
    償却額 DECIMAL(15, 2) NOT NULL,
    期末帳簿価額 DECIMAL(15, 2) NOT NULL,
    備考 TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES T_物件(id)
);
"""

try:
    with engine.connect() as conn:
        # トランザクション開始
        trans = conn.begin()
        try:
            # SQLを実行
            for statement in migration_sql.split(';'):
                statement = statement.strip()
                if statement:
                    print(f"実行中: {statement[:50]}...")
                    conn.execute(text(statement))
            
            # コミット
            trans.commit()
            print("\n✓ マイグレーション完了")
            
        except Exception as e:
            # ロールバック
            trans.rollback()
            print(f"\n✗ マイグレーション失敗: {e}")
            sys.exit(1)
            
except Exception as e:
    print(f"\n✗ データベース接続エラー: {e}")
    sys.exit(1)
