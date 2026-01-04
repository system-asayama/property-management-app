#!/usr/bin/env python3
"""
ローン条件テーブル作成スクリプト
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.db import engine

def create_loan_condition_table():
    """ローン条件テーブルを作成"""
    with engine.connect() as conn:
        # TLoanCondition テーブル作成
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS t_loan_condition (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                シミュレーションid INTEGER NOT NULL,
                借入日 DATE NOT NULL,
                返済日 INTEGER NOT NULL COMMENT '毎月の返済日(1-31)',
                返済開始年月 VARCHAR(7) NOT NULL COMMENT 'YYYY-MM形式',
                据置期間終了年月 VARCHAR(7) COMMENT 'YYYY-MM形式、NULLの場合は据置なし',
                初回利息支払方法 INTEGER NOT NULL DEFAULT 1 COMMENT '1:初回にまとめて, 2:月末に支払, 3:無視',
                作成日時 DATETIME DEFAULT CURRENT_TIMESTAMP,
                更新日時 DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (シミュレーションid) REFERENCES t_simulation(id) ON DELETE CASCADE,
                INDEX idx_simulation (シミュレーションid)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            COMMENT='ローン返済条件テーブル（詳細モード用）'
        """))
        conn.commit()
        print("✅ TLoanCondition テーブルを作成しました")

def create_loan_interest_schedule_table():
    """ローン金利スケジュールテーブルを作成"""
    with engine.connect() as conn:
        # TLoanInterestSchedule テーブル作成
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS t_loan_interest_schedule (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                シミュレーションid INTEGER NOT NULL,
                開始年月 VARCHAR(7) NOT NULL COMMENT 'YYYY-MM形式',
                終了年月 VARCHAR(7) COMMENT 'YYYY-MM形式、NULLは最終年度まで',
                金利 DECIMAL(5,3) NOT NULL COMMENT '年利率(%)',
                備考 VARCHAR(200) COMMENT '説明文',
                作成日時 DATETIME DEFAULT CURRENT_TIMESTAMP,
                更新日時 DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (シミュレーションid) REFERENCES t_simulation(id) ON DELETE CASCADE,
                INDEX idx_simulation (シミュレーションid),
                INDEX idx_period (開始年月, 終了年月)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            COMMENT='ローン金利スケジュールテーブル（詳細モード用）'
        """))
        conn.commit()
        print("✅ TLoanInterestSchedule テーブルを作成しました")

def add_loan_calculation_mode_column():
    """TSimulationテーブルにローン計算モードカラムを追加"""
    with engine.connect() as conn:
        # カラムが既に存在するかチェック
        result = conn.execute(text("""
            SELECT COUNT(*) as cnt
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 't_simulation'
            AND COLUMN_NAME = 'ローン計算モード'
        """))
        exists = result.fetchone()[0] > 0
        
        if not exists:
            conn.execute(text("""
                ALTER TABLE t_simulation
                ADD COLUMN ローン計算モード INTEGER NOT NULL DEFAULT 1
                COMMENT '1:簡易モード, 2:詳細モード'
                AFTER ローン年間返済額
            """))
            conn.commit()
            print("✅ TSimulation テーブルに「ローン計算モード」カラムを追加しました")
        else:
            print("ℹ️  「ローン計算モード」カラムは既に存在します")

if __name__ == '__main__':
    try:
        print("ローン詳細モード用テーブルを作成します...")
        create_loan_condition_table()
        create_loan_interest_schedule_table()
        add_loan_calculation_mode_column()
        print("\n✅ すべてのテーブル作成が完了しました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)
