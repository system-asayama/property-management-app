"""
不動産管理アプリ用のSQLAlchemyモデル
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Date
from sqlalchemy.sql import func
from app.db import Base


class TBukken(Base):
    """T_物件テーブル"""
    __tablename__ = 'T_物件'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey('T_テナント.id'), nullable=False)
    物件名 = Column(String(255), nullable=False)
    物件種別 = Column(String(50), nullable=True)
    郵便番号 = Column(String(10), nullable=True)
    住所 = Column(String(500), nullable=True)
    建築年月 = Column(Date, nullable=True)
    延床面積 = Column(Numeric(10, 2), nullable=True)
    構造 = Column(String(50), nullable=True)
    階数 = Column(Integer, nullable=True)
    部屋数 = Column(Integer, nullable=True)
    取得価額 = Column(Numeric(15, 2), nullable=True)
    取得年月日 = Column(Date, nullable=True)
    耐用年数 = Column(Integer, nullable=True)
    償却方法 = Column(String(20), nullable=True)
    残存価額 = Column(Numeric(15, 2), nullable=True)
    備考 = Column(Text, nullable=True)
    有効 = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class THeya(Base):
    """T_部屋テーブル"""
    __tablename__ = 'T_部屋'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey('T_物件.id'), nullable=False)
    部屋番号 = Column(String(50), nullable=False)
    間取り = Column(String(50), nullable=True)
    専有面積 = Column(Numeric(10, 2), nullable=True)
    賃料 = Column(Numeric(10, 0), nullable=True)
    管理費 = Column(Numeric(10, 0), nullable=True)
    敷金 = Column(Numeric(10, 0), nullable=True)
    礼金 = Column(Numeric(10, 0), nullable=True)
    入居状況 = Column(String(20), default='空室')
    備考 = Column(Text, nullable=True)
    有効 = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TNyukyosha(Base):
    """T_入居者テーブル"""
    __tablename__ = 'T_入居者'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey('T_テナント.id'), nullable=False)
    氏名 = Column(String(255), nullable=False)
    フリガナ = Column(String(255), nullable=True)
    生年月日 = Column(Date, nullable=True)
    電話番号 = Column(String(20), nullable=True)
    メールアドレス = Column(String(255), nullable=True)
    緊急連絡先名 = Column(String(255), nullable=True)
    緊急連絡先電話番号 = Column(String(20), nullable=True)
    備考 = Column(Text, nullable=True)
    有効 = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TKeiyaku(Base):
    """T_契約テーブル"""
    __tablename__ = 'T_契約'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('T_部屋.id'), nullable=False)
    tenant_person_id = Column(Integer, ForeignKey('T_入居者.id'), nullable=False)
    契約開始日 = Column(Date, nullable=False)
    契約終了日 = Column(Date, nullable=True)
    月額賃料 = Column(Numeric(10, 0), nullable=False)
    月額管理費 = Column(Numeric(10, 0), nullable=True)
    敷金 = Column(Numeric(10, 0), nullable=True)
    礼金 = Column(Numeric(10, 0), nullable=True)
    契約状況 = Column(String(20), default='契約中')
    備考 = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TYachinShushi(Base):
    """T_家賃収支テーブル"""
    __tablename__ = 'T_家賃収支'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey('T_契約.id'), nullable=False)
    対象年月 = Column(String(7), nullable=False)
    賃料 = Column(Numeric(10, 0), nullable=False)
    管理費 = Column(Numeric(10, 0), nullable=True)
    入金日 = Column(Date, nullable=True)
    入金状況 = Column(String(20), default='未入金')
    備考 = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TGenkashokaku(Base):
    """T_減価償却テーブル"""
    __tablename__ = 'T_減価償却'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey('T_物件.id'), nullable=False)
    年度 = Column(Integer, nullable=False)
    期首帳簿価額 = Column(Numeric(15, 2), nullable=False)
    償却額 = Column(Numeric(15, 2), nullable=False)
    期末帳簿価額 = Column(Numeric(15, 2), nullable=False)
    備考 = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
