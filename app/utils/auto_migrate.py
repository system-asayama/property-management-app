"""
自動マイグレーション機能

アプリケーション起動時に自動的にデータベーススキーマをチェックし、
不足しているカラムやテーブルを追加します。
"""

import logging
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def get_table_columns(engine, table_name):
    """テーブルの既存カラム一覧を取得"""
    inspector = inspect(engine)
    try:
        columns = inspector.get_columns(table_name)
        return {col['name'] for col in columns}
    except Exception:
        return set()


def get_model_columns(model):
    """モデルの定義カラム一覧を取得"""
    return {col.name for col in model.__table__.columns}


def add_missing_columns(engine, model, table_name):
    """不足しているカラムを追加"""
    try:
        existing_columns = get_table_columns(engine, table_name)
    except Exception as e:
        logger.warning(f"テーブル '{table_name}' が存在しないためスキップ: {e}")
        return True
    
    try:
        model_columns = get_model_columns(model)
    except Exception as e:
        logger.error(f"モデルのカラム取得に失敗: {e}")
        return False
    
    missing_columns = model_columns - existing_columns
    
    if not missing_columns:
        logger.info(f"テーブル '{table_name}' に不足カラムはありません")
        return True
    
    logger.info(f"テーブル '{table_name}' に {len(missing_columns)} 個のカラムを追加します: {missing_columns}")
    
    # データベースの種類を判定
    db_type = engine.dialect.name
    
    with engine.begin() as conn:
        for col_name in missing_columns:
            try:
                column = model.__table__.columns[col_name]
                
                # カラムの型を取得
                col_type = column.type.compile(engine.dialect)
                
                # NULL制約を取得
                nullable = "NULL" if column.nullable else "NOT NULL"
                
                # デフォルト値を取得
                default = ""
                if column.server_default is not None:
                    default_value = column.server_default.arg
                    if hasattr(default_value, 'text'):
                        default = f"DEFAULT {default_value.text}"
                    else:
                        default = f"DEFAULT '{default_value}'"
                
                # ALTER TABLE文を構築
                if db_type == 'postgresql':
                    sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{col_name}" {col_type} {nullable} {default}'
                else:  # SQLite
                    sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{col_name}" {col_type} {nullable} {default}'
                
                logger.info(f"実行SQL: {sql}")
                conn.execute(text(sql))
                logger.info(f"✓ カラム '{col_name}' を追加しました")
                
            except SQLAlchemyError as e:
                logger.error(f"✗ カラム '{col_name}' の追加に失敗: {e}")
                # カラム追加に失敗しても続行
                continue
    
    return True


def auto_migrate_all(engine, models):
    """
    すべてのモデルに対して自動マイグレーションを実行
    
    Args:
        engine: SQLAlchemyエンジン
        models: [(model_class, table_name), ...] のリスト
    """
    logger.info("=" * 60)
    logger.info("自動マイグレーション開始")
    logger.info("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for model, table_name in models:
        try:
            logger.info(f"\nテーブル '{table_name}' をチェック中...")
            add_missing_columns(engine, model, table_name)
            success_count += 1
        except Exception as e:
            logger.error(f"テーブル '{table_name}' のマイグレーションに失敗: {e}")
            error_count += 1
    
    logger.info("=" * 60)
    logger.info(f"自動マイグレーション完了: 成功 {success_count}, 失敗 {error_count}")
    logger.info("=" * 60)
    
    return error_count == 0
