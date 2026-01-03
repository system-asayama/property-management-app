# -*- coding: utf-8 -*-
"""
不動産管理アプリのBlueprint
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import select, update, delete
from datetime import datetime, date
from decimal import Decimal
from app.db import SessionLocal
from app.models_property import TBukken, THeya, TNyukyosha, TKeiyaku, TYachinShushi, TGenkashokaku, TSimulation, TSimulationResult, TBukkenKeihi, THeyaKeihi

property_bp = Blueprint('property', __name__, url_prefix='/property')


def require_tenant_admin(f):
    """テナント管理者またはシステム管理者のみアクセス可能にするデコレータ"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = session.get('role')
        if 'user_id' not in session or role not in ['tenant_admin', 'system_admin']:
            flash('この機能にはテナント管理者権限が必要です', 'danger')
            return redirect(url_for('auth.select_login'))
        
        # テナントIDがセッションに設定されているか確認
        if 'tenant_id' not in session:
            flash('テナントが選択されていません', 'warning')
            return redirect(url_for('tenant_admin.tenant_apps'))
        
        return f(*args, **kwargs)
    return decorated_function


@property_bp.route('/')
@require_tenant_admin
def index():
    """不動産管理トップページ（ダッシュボード）"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # 統計情報を取得
    properties_count = db.execute(
        select(TBukken).where(TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
    ).scalars().all()
    
    rooms_count = 0
    vacant_rooms_count = 0
    occupied_rooms_count = 0
    
    for prop in properties_count:
        rooms = db.execute(
            select(THeya).where(THeya.property_id == prop.id, THeya.有効 == 1)
        ).scalars().all()
        rooms_count += len(rooms)
        vacant_rooms_count += sum(1 for r in rooms if r.入居状況 == '空室')
        occupied_rooms_count += sum(1 for r in rooms if r.入居状況 == '入居中')
    
    tenants_count = db.execute(
        select(TNyukyosha).where(TNyukyosha.tenant_id == tenant_id, TNyukyosha.有効 == 1)
    ).scalars().all()
    
    contracts_count = db.execute(
        select(TKeiyaku).where(TKeiyaku.契約状況 == '契約中')
    ).scalars().all()
    
    # 契約中の契約のみをフィルタリング（テナントIDで絞り込み）
    active_contracts = []
    for contract in contracts_count:
        room = db.execute(
            select(THeya).where(THeya.id == contract.room_id)
        ).scalar_one_or_none()
        if room:
            prop = db.execute(
                select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id)
            ).scalar_one_or_none()
            if prop:
                active_contracts.append(contract)
    
    return render_template('property_dashboard.html',
                         properties_count=len(properties_count),
                         rooms_count=rooms_count,
                         vacant_rooms_count=vacant_rooms_count,
                         occupied_rooms_count=occupied_rooms_count,
                         tenants_count=len(tenants_count),
                         contracts_count=len(active_contracts))


# ==================== 物件管理 ====================

@property_bp.route('/properties')
@require_tenant_admin
def properties():
    """物件一覧"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    properties = db.execute(
        select(TBukken).where(TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
        .order_by(TBukken.created_at.desc())
    ).scalars().all()
    
    return render_template('property_properties.html', properties=properties)


@property_bp.route('/properties/new', methods=['GET', 'POST'])
@require_tenant_admin
def property_new():
    """物件登録"""
    if request.method == 'POST':
        db = SessionLocal()
        tenant_id = session.get('tenant_id')
        
        # フォームデータを取得
        property_data = TBukken(
            tenant_id=tenant_id,
            物件名=request.form.get('物件名'),
            物件種別=request.form.get('物件種別'),
            郵便番号=request.form.get('郵便番号'),
            住所=request.form.get('住所'),
            建築年月=datetime.strptime(request.form.get('建築年月'), '%Y-%m-%d').date() if request.form.get('建築年月') else None,
            延床面積=Decimal(request.form.get('延床面積')) if request.form.get('延床面積') else None,
            構造=request.form.get('構造'),
            階数=int(request.form.get('階数')) if request.form.get('階数') else None,
            部屋数=int(request.form.get('部屋数')) if request.form.get('部屋数') else None,
            取得価額=Decimal(request.form.get('取得価額')) if request.form.get('取得価額') else None,
            取得年月日=datetime.strptime(request.form.get('取得年月日'), '%Y-%m-%d').date() if request.form.get('取得年月日') else None,
            耐用年数=int(request.form.get('耐用年数')) if request.form.get('耐用年数') else None,
            償却方法=request.form.get('償却方法'),
            残存価額=Decimal(request.form.get('残存価額')) if request.form.get('残存価額') else None,
            備考=request.form.get('備考')
        )
        
        db.add(property_data)
        db.commit()
        
        flash('物件を登録しました', 'success')
        return redirect(url_for('property.properties'))
    
    return render_template('property_property_new.html')


@property_bp.route('/properties/<int:id>')
@require_tenant_admin
def property_detail(id):
    """物件詳細"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    property_data = db.execute(
        select(TBukken).where(TBukken.id == id, TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 部屋一覧を取得
    rooms = db.execute(
        select(THeya).where(THeya.property_id == id, THeya.有効 == 1)
        .order_by(THeya.部屋番号)
    ).scalars().all()
    
    return render_template('property_property_detail.html', property=property_data, rooms=rooms)


@property_bp.route('/properties/<int:id>/edit', methods=['GET', 'POST'])
@require_tenant_admin
def property_edit(id):
    """物件編集"""
    try:
        db = SessionLocal()
        tenant_id = session.get('tenant_id')
        
        property_data = db.execute(
            select(TBukken).where(TBukken.id == id, TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
        ).scalar_one_or_none()
        
        if not property_data:
            flash('物件が見つかりません', 'danger')
            return redirect(url_for('property.properties'))
        
        if request.method == 'POST':
            property_data.物件名 = request.form.get('物件名')
            property_data.物件種別 = request.form.get('物件種別')
            property_data.郵便番号 = request.form.get('郵便番号')
            property_data.住所 = request.form.get('住所')
            property_data.建築年月 = datetime.strptime(request.form.get('建築年月'), '%Y-%m-%d').date() if request.form.get('建築年月') else None
            property_data.延床面積 = Decimal(request.form.get('延床面積')) if request.form.get('延床面積') else None
            property_data.構造 = request.form.get('構造')
            property_data.階数 = int(request.form.get('階数')) if request.form.get('階数') else None
            property_data.部屋数 = int(request.form.get('部屋数')) if request.form.get('部屋数') else None
            property_data.取得価額 = Decimal(request.form.get('取得価額')) if request.form.get('取得価額') else None
            property_data.取得年月日 = datetime.strptime(request.form.get('取得年月日'), '%Y-%m-%d').date() if request.form.get('取得年月日') else None
            property_data.耐用年数 = int(request.form.get('耐用年数')) if request.form.get('耐用年数') else None
            property_data.償却方法 = request.form.get('償却方法')
            property_data.残存価額 = Decimal(request.form.get('残存価額')) if request.form.get('残存価額') else None
            property_data.備考 = request.form.get('備考')
            # 建物付属設備
            property_data.付属設備_取得価額 = Decimal(request.form.get('付属設備_取得価額')) if request.form.get('付属設備_取得価額') else None
            property_data.付属設備_取得年月日 = datetime.strptime(request.form.get('付属設備_取得年月日'), '%Y-%m-%d').date() if request.form.get('付属設備_取得年月日') else None
            property_data.付属設備_耐用年数 = int(request.form.get('付属設備_耐用年数')) if request.form.get('付属設備_耐用年数') else None
            property_data.付属設備_償却方法 = request.form.get('付属設備_償却方法')
            property_data.付属設備_残存価額 = Decimal(request.form.get('付属設備_残存価額')) if request.form.get('付属設備_残存価額') else None
            property_data.付属設備_備考 = request.form.get('付属設備_備考')
            # 構築物
            property_data.構築物_取得価額 = Decimal(request.form.get('構築物_取得価額')) if request.form.get('構築物_取得価額') else None
            property_data.構築物_取得年月日 = datetime.strptime(request.form.get('構築物_取得年月日'), '%Y-%m-%d').date() if request.form.get('構築物_取得年月日') else None
            property_data.構築物_耐用年数 = int(request.form.get('構築物_耐用年数')) if request.form.get('構築物_耐用年数') else None
            property_data.構築物_償却方法 = request.form.get('構築物_償却方法')
            property_data.構築物_残存価額 = Decimal(request.form.get('構築物_残存価額')) if request.form.get('構築物_残存価額') else None
            property_data.構築物_備考 = request.form.get('構築物_備考')
            property_data.updated_at = datetime.now()
            
            db.commit()
            
            flash('物件を更新しました', 'success')
            return redirect(url_for('property.property_detail', id=id))
        
        return render_template('property_property_edit.html', property=property_data)
    except Exception as e:
        import traceback
        print(f"⚠️ 物件編集エラー: {e}")
        print(traceback.format_exc())
        flash(f'エラーが発生しました: {str(e)}', 'danger')
        return redirect(url_for('property.properties'))
@property_bp.route('/properties/<int:id>/delete', methods=['POST'])
@require_tenant_admin
def property_delete(id):
    """物件削除（論理削除）"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    property_data = db.execute(
        select(TBukken).where(TBukken.id == id, TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    property_data.有効 = 0
    property_data.updated_at = datetime.now()
    db.commit()
    
    flash('物件を削除しました', 'success')
    return redirect(url_for('property.properties'))


# ==================== 部屋管理 ====================

@property_bp.route('/properties/<int:property_id>/rooms/new', methods=['GET', 'POST'])
@require_tenant_admin
def room_new(property_id):
    """部屋登録"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # 物件の存在確認
    property_data = db.execute(
        select(TBukken).where(TBukken.id == property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    if request.method == 'POST':
        room_data = THeya(
            property_id=property_id,
            部屋番号=request.form.get('部屋番号'),
            間取り=request.form.get('間取り'),
            専有面積=Decimal(request.form.get('専有面積')) if request.form.get('専有面積') else None,
            賃料=Decimal(request.form.get('賃料')) if request.form.get('賃料') else None,
            管理費=Decimal(request.form.get('管理費')) if request.form.get('管理費') else None,
            敷金=Decimal(request.form.get('敷金')) if request.form.get('敷金') else None,
            礼金=Decimal(request.form.get('礼金')) if request.form.get('礼金') else None,
            入居状況=request.form.get('入居状況', '空室'),
            備考=request.form.get('備考')
        )
        
        db.add(room_data)
        db.commit()
        
        flash('部屋を登録しました', 'success')
        return redirect(url_for('property.property_detail', id=property_id))
    
    return render_template('property_room_new.html', property=property_data)


@property_bp.route('/rooms/<int:id>')
@require_tenant_admin
def room_detail(id):
    """部屋詳細"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    room = db.execute(
        select(THeya).where(THeya.id == id, THeya.有効 == 1)
    ).scalar_one_or_none()
    
    if not room:
        flash('部屋が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 物件情報を取得
    property_data = db.execute(
        select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 契約履歴を取得
    contracts = db.execute(
        select(TKeiyaku).where(TKeiyaku.room_id == id)
        .order_by(TKeiyaku.契約開始日.desc())
    ).scalars().all()
    
    return render_template('property_room_detail.html', room=room, property=property_data, contracts=contracts)


@property_bp.route('/rooms/<int:id>/edit', methods=['GET', 'POST'])
@require_tenant_admin
def room_edit(id):
    """部屋編集"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    room = db.execute(
        select(THeya).where(THeya.id == id, THeya.有効 == 1)
    ).scalar_one_or_none()
    
    if not room:
        flash('部屋が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 物件情報を取得
    property_data = db.execute(
        select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    if request.method == 'POST':
        room.部屋番号 = request.form.get('部屋番号')
        room.間取り = request.form.get('間取り')
        room.専有面積 = Decimal(request.form.get('専有面積')) if request.form.get('専有面積') else None
        room.賃料 = Decimal(request.form.get('賃料')) if request.form.get('賃料') else None
        room.管理費 = Decimal(request.form.get('管理費')) if request.form.get('管理費') else None
        room.敷金 = Decimal(request.form.get('敷金')) if request.form.get('敷金') else None
        room.礼金 = Decimal(request.form.get('礼金')) if request.form.get('礼金') else None
        room.入居状況 = request.form.get('入居状況', '空室')
        room.備考 = request.form.get('備考')
        room.updated_at = datetime.now()
        
        db.commit()
        
        flash('部屋を更新しました', 'success')
        return redirect(url_for('property.room_detail', id=id))
    
    return render_template('property_room_edit.html', room=room, property=property_data)


@property_bp.route('/rooms/<int:id>/delete', methods=['POST'])
@require_tenant_admin
def room_delete(id):
    """部屋削除（論理削除）"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    room = db.execute(
        select(THeya).where(THeya.id == id, THeya.有効 == 1)
    ).scalar_one_or_none()
    
    if not room:
        flash('部屋が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 物件情報を取得してテナントIDを確認
    property_data = db.execute(
        select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    room.有効 = 0
    room.updated_at = datetime.now()
    db.commit()
    
    flash('部屋を削除しました', 'success')
    return redirect(url_for('property.property_detail', id=property_data.id))


# ==================== 入居者管理 ====================

@property_bp.route('/tenants')
@require_tenant_admin
def tenants():
    """入居者一覧"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    tenants = db.execute(
        select(TNyukyosha).where(TNyukyosha.tenant_id == tenant_id, TNyukyosha.有効 == 1)
        .order_by(TNyukyosha.created_at.desc())
    ).scalars().all()
    
    return render_template('property_tenants.html', tenants=tenants)


@property_bp.route('/tenants/new', methods=['GET', 'POST'])
@require_tenant_admin
def tenant_new():
    """入居者登録"""
    if request.method == 'POST':
        db = SessionLocal()
        tenant_id = session.get('tenant_id')
        
        tenant_data = TNyukyosha(
            tenant_id=tenant_id,
            氏名=request.form.get('氏名'),
            フリガナ=request.form.get('フリガナ'),
            生年月日=datetime.strptime(request.form.get('生年月日'), '%Y-%m-%d').date() if request.form.get('生年月日') else None,
            電話番号=request.form.get('電話番号'),
            メールアドレス=request.form.get('メールアドレス'),
            緊急連絡先名=request.form.get('緊急連絡先名'),
            緊急連絡先電話番号=request.form.get('緊急連絡先電話番号'),
            備考=request.form.get('備考')
        )
        
        db.add(tenant_data)
        db.commit()
        
        flash('入居者を登録しました', 'success')
        return redirect(url_for('property.tenants'))
    
    return render_template('property_tenant_new.html')


@property_bp.route('/tenants/<int:id>')
@require_tenant_admin
def tenant_detail(id):
    """入居者詳細"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    tenant_data = db.execute(
        select(TNyukyosha).where(TNyukyosha.id == id, TNyukyosha.tenant_id == tenant_id, TNyukyosha.有効 == 1)
    ).scalar_one_or_none()
    
    if not tenant_data:
        flash('入居者が見つかりません', 'danger')
        return redirect(url_for('property.tenants'))
    
    # 契約履歴を取得
    contracts = db.execute(
        select(TKeiyaku).where(TKeiyaku.tenant_person_id == id)
        .order_by(TKeiyaku.契約開始日.desc())
    ).scalars().all()
    
    return render_template('property_tenant_detail.html', tenant=tenant_data, contracts=contracts)


@property_bp.route('/tenants/<int:id>/edit', methods=['GET', 'POST'])
@require_tenant_admin
def tenant_edit(id):
    """入居者編集"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    tenant_data = db.execute(
        select(TNyukyosha).where(TNyukyosha.id == id, TNyukyosha.tenant_id == tenant_id, TNyukyosha.有効 == 1)
    ).scalar_one_or_none()
    
    if not tenant_data:
        flash('入居者が見つかりません', 'danger')
        return redirect(url_for('property.tenants'))
    
    if request.method == 'POST':
        tenant_data.氏名 = request.form.get('氏名')
        tenant_data.フリガナ = request.form.get('フリガナ')
        tenant_data.生年月日 = datetime.strptime(request.form.get('生年月日'), '%Y-%m-%d').date() if request.form.get('生年月日') else None
        tenant_data.電話番号 = request.form.get('電話番号')
        tenant_data.メールアドレス = request.form.get('メールアドレス')
        tenant_data.緊急連絡先名 = request.form.get('緊急連絡先名')
        tenant_data.緊急連絡先電話番号 = request.form.get('緊急連絡先電話番号')
        tenant_data.備考 = request.form.get('備考')
        tenant_data.updated_at = datetime.now()
        
        db.commit()
        
        flash('入居者を更新しました', 'success')
        return redirect(url_for('property.tenant_detail', id=id))
    
    return render_template('property_tenant_edit.html', tenant=tenant_data)


@property_bp.route('/tenants/<int:id>/delete', methods=['POST'])
@require_tenant_admin
def tenant_delete(id):
    """入居者削除（論理削除）"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    tenant_data = db.execute(
        select(TNyukyosha).where(TNyukyosha.id == id, TNyukyosha.tenant_id == tenant_id, TNyukyosha.有効 == 1)
    ).scalar_one_or_none()
    
    if not tenant_data:
        flash('入居者が見つかりません', 'danger')
        return redirect(url_for('property.tenants'))
    
    tenant_data.有効 = 0
    tenant_data.updated_at = datetime.now()
    db.commit()
    
    flash('入居者を削除しました', 'success')
    return redirect(url_for('property.tenants'))


# ==================== 契約管理 ====================

@property_bp.route('/contracts')
@require_tenant_admin
def contracts():
    """契約一覧"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # テナントに紐づく契約を取得
    all_contracts = db.execute(
        select(TKeiyaku).order_by(TKeiyaku.契約開始日.desc())
    ).scalars().all()
    
    # テナントIDでフィルタリング
    contracts_list = []
    for contract in all_contracts:
        room = db.execute(
            select(THeya).where(THeya.id == contract.room_id)
        ).scalar_one_or_none()
        if room:
            property_data = db.execute(
                select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id)
            ).scalar_one_or_none()
            if property_data:
                tenant_person = db.execute(
                    select(TNyukyosha).where(TNyukyosha.id == contract.tenant_person_id)
                ).scalar_one_or_none()
                contracts_list.append({
                    'contract': contract,
                    'room': room,
                    'property': property_data,
                    'tenant_person': tenant_person
                })
    
    return render_template('property_contracts.html', contracts=contracts_list)


@property_bp.route('/contracts/new', methods=['GET', 'POST'])
@require_tenant_admin
def contract_new():
    """契約登録"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    if request.method == 'POST':
        contract_data = TKeiyaku(
            room_id=int(request.form.get('room_id')),
            tenant_person_id=int(request.form.get('tenant_person_id')),
            契約開始日=datetime.strptime(request.form.get('契約開始日'), '%Y-%m-%d').date(),
            契約終了日=datetime.strptime(request.form.get('契約終了日'), '%Y-%m-%d').date() if request.form.get('契約終了日') else None,
            月額賃料=Decimal(request.form.get('月額賃料')),
            月額管理費=Decimal(request.form.get('月額管理費')) if request.form.get('月額管理費') else None,
            敷金=Decimal(request.form.get('敷金')) if request.form.get('敷金') else None,
            礼金=Decimal(request.form.get('礼金')) if request.form.get('礼金') else None,
            契約状況='契約中',
            備考=request.form.get('備考')
        )
        
        db.add(contract_data)
        
        # 部屋の入居状況を更新
        room = db.execute(
            select(THeya).where(THeya.id == int(request.form.get('room_id')))
        ).scalar_one_or_none()
        if room:
            room.入居状況 = '入居中'
            room.updated_at = datetime.now()
        
        db.commit()
        
        flash('契約を登録しました', 'success')
        return redirect(url_for('property.contracts'))
    
    # 空室一覧を取得
    properties = db.execute(
        select(TBukken).where(TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
    ).scalars().all()
    
    vacant_rooms = []
    for prop in properties:
        rooms = db.execute(
            select(THeya).where(THeya.property_id == prop.id, THeya.有効 == 1, THeya.入居状況 == '空室')
        ).scalars().all()
        for room in rooms:
            vacant_rooms.append({
                'room': room,
                'property': prop
            })
    
    # 入居者一覧を取得
    tenants = db.execute(
        select(TNyukyosha).where(TNyukyosha.tenant_id == tenant_id, TNyukyosha.有効 == 1)
    ).scalars().all()
    
    return render_template('property_contract_new.html', vacant_rooms=vacant_rooms, tenants=tenants)


@property_bp.route('/contracts/<int:id>')
@require_tenant_admin
def contract_detail(id):
    """契約詳細"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    contract = db.execute(
        select(TKeiyaku).where(TKeiyaku.id == id)
    ).scalar_one_or_none()
    
    if not contract:
        flash('契約が見つかりません', 'danger')
        return redirect(url_for('property.contracts'))
    
    # 部屋情報を取得
    room = db.execute(
        select(THeya).where(THeya.id == contract.room_id)
    ).scalar_one_or_none()
    
    # 物件情報を取得
    property_data = db.execute(
        select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.contracts'))
    
    # 入居者情報を取得
    tenant_person = db.execute(
        select(TNyukyosha).where(TNyukyosha.id == contract.tenant_person_id)
    ).scalar_one_or_none()
    
    # 家賃収支を取得
    rent_payments = db.execute(
        select(TYachinShushi).where(TYachinShushi.contract_id == id)
        .order_by(TYachinShushi.対象年月.desc())
    ).scalars().all()
    
    return render_template('property_contract_detail.html',
                         contract=contract,
                         room=room,
                         property=property_data,
                         tenant_person=tenant_person,
                         rent_payments=rent_payments)


@property_bp.route('/contracts/<int:id>/edit', methods=['GET', 'POST'])
@require_tenant_admin
def contract_edit(id):
    """契約編集"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    contract = db.execute(
        select(TKeiyaku).where(TKeiyaku.id == id)
    ).scalar_one_or_none()
    
    if not contract:
        flash('契約が見つかりません', 'danger')
        return redirect(url_for('property.contracts'))
    
    # 部屋情報を取得
    room = db.execute(
        select(THeya).where(THeya.id == contract.room_id)
    ).scalar_one_or_none()
    
    # 物件情報を取得
    property_data = db.execute(
        select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.contracts'))
    
    # 入居者情報を取得
    tenant_person = db.execute(
        select(TNyukyosha).where(TNyukyosha.id == contract.tenant_person_id)
    ).scalar_one_or_none()
    
    if request.method == 'POST':
        contract.契約開始日 = datetime.strptime(request.form.get('契約開始日'), '%Y-%m-%d').date()
        contract.契約終了日 = datetime.strptime(request.form.get('契約終了日'), '%Y-%m-%d').date() if request.form.get('契約終了日') else None
        contract.月額賃料 = Decimal(request.form.get('月額賃料'))
        contract.月額管理費 = Decimal(request.form.get('月額管理費')) if request.form.get('月額管理費') else None
        contract.敷金 = Decimal(request.form.get('敷金')) if request.form.get('敷金') else None
        contract.礼金 = Decimal(request.form.get('礼金')) if request.form.get('礼金') else None
        contract.備考 = request.form.get('備考')
        contract.updated_at = datetime.now()
        
        db.commit()
        
        flash('契約を更新しました', 'success')
        return redirect(url_for('property.contract_detail', id=id))
    
    return render_template('property_contract_edit.html',
                         contract=contract,
                         room=room,
                         property=property_data,
                         tenant_person=tenant_person)


@property_bp.route('/contracts/<int:id>/terminate', methods=['POST'])
@require_tenant_admin
def contract_terminate(id):
    """契約終了"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    contract = db.execute(
        select(TKeiyaku).where(TKeiyaku.id == id)
    ).scalar_one_or_none()
    
    if not contract:
        flash('契約が見つかりません', 'danger')
        return redirect(url_for('property.contracts'))
    
    # 部屋情報を取得
    room = db.execute(
        select(THeya).where(THeya.id == contract.room_id)
    ).scalar_one_or_none()
    
    # 物件情報を取得してテナントIDを確認
    property_data = db.execute(
        select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.contracts'))
    
    contract.契約状況 = '契約終了'
    contract.契約終了日 = date.today()
    contract.updated_at = datetime.now()
    
    # 部屋の入居状況を更新
    room.入居状況 = '空室'
    room.updated_at = datetime.now()
    
    db.commit()
    
    flash('契約を終了しました', 'success')
    return redirect(url_for('property.contracts'))


# ==================== 減価償却管理 ====================

@property_bp.route('/depreciation')
@require_tenant_admin
def depreciation():
    """減価償却一覧"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # 物件一覧を取得
    properties = db.execute(
        select(TBukken).where(TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
        .order_by(TBukken.created_at.desc())
    ).scalars().all()
    
    depreciation_list = []
    for prop in properties:
        # 最新の減価償却情報を取得
        latest_dep = db.execute(
            select(TGenkashokaku).where(TGenkashokaku.property_id == prop.id)
            .order_by(TGenkashokaku.年度.desc())
        ).scalars().first()
        
        depreciation_list.append({
            'property': prop,
            'latest_depreciation': latest_dep
        })
    
    return render_template('property_depreciation.html', depreciation_list=depreciation_list)


@property_bp.route('/depreciation/<int:property_id>')
@require_tenant_admin
def depreciation_detail(property_id):
    """物件別減価償却詳細"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    property_data = db.execute(
        select(TBukken).where(TBukken.id == property_id, TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.depreciation'))
    
    # 減価償却履歴を取得
    depreciation_history = db.execute(
        select(TGenkashokaku).where(TGenkashokaku.property_id == property_id)
        .order_by(TGenkashokaku.年度.desc())
    ).scalars().all()
    
    from datetime import date
    return render_template('property_depreciation_detail.html',
                         property=property_data,
                         depreciation_history=depreciation_history,
                         current_year=date.today().year)


@property_bp.route('/depreciation/<int:property_id>/calculate', methods=['POST'])
@require_tenant_admin
def depreciation_calculate(property_id):
    """減価償却計算"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    property_data = db.execute(
        select(TBukken).where(TBukken.id == property_id, TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.depreciation'))
    
    # 減価償却の計算に必要な情報を確認
    if not property_data.取得価額 or not property_data.耐用年数 or not property_data.償却方法:
        flash('減価償却の計算に必要な情報（取得価額、耐用年数、償却方法）が不足しています', 'danger')
        return redirect(url_for('property.depreciation_detail', property_id=property_id))
    
    # 対象年度を取得（フォームから）
    target_year = int(request.form.get('target_year', date.today().year))
    
    # 前年度の減価償却情報を取得
    prev_dep = db.execute(
        select(TGenkashokaku).where(
            TGenkashokaku.property_id == property_id,
            TGenkashokaku.年度 == target_year - 1
        )
    ).scalar_one_or_none()
    
    # 期首帳簿価額を計算
    if prev_dep:
        期首帳簿価額 = prev_dep.期末帳簿価額
    else:
        期首帳簿価額 = property_data.取得価額
    
    # 償却額を計算
    if property_data.償却方法 == '定額法':
        償却額 = (property_data.取得価額 - (property_data.残存価額 or 0)) / property_data.耐用年数
    elif property_data.償却方法 == '定率法':
        償却率 = Decimal('2.0') / property_data.耐用年数
        償却額 = 期首帳簿価額 * 償却率
    else:
        flash('償却方法が不正です', 'danger')
        return redirect(url_for('property.depreciation_detail', property_id=property_id))
    
    # 期末帳簿価額を計算
    期末帳簿価額 = 期首帳簿価額 - 償却額
    
    # 残存価額を下回らないようにする
    if property_data.残存価額 and 期末帳簿価額 < property_data.残存価額:
        償却額 = 期首帳簿価額 - property_data.残存価額
        期末帳簿価額 = property_data.残存価額
    
    # 減価償却情報を登録
    depreciation_data = TGenkashokaku(
        property_id=property_id,
        年度=target_year,
        期首帳簿価額=期首帳簿価額,
        償却額=償却額,
        期末帳簿価額=期末帳簿価額
    )
    
    db.add(depreciation_data)
    db.commit()
    
    flash(f'{target_year}年度の減価償却を計算しました', 'success')
    return redirect(url_for('property.depreciation_detail', property_id=property_id))


# ==================== シミュレーション ====================

def calculate_tax_rate(total_income):
    """所得金額に応じた税率を計算（所得税+住民税）"""
    total_income = Decimal(str(total_income))
    
    if total_income <= 1950000:
        return Decimal('15.0')  # 5% + 10%
    elif total_income <= 3300000:
        return Decimal('20.0')  # 10% + 10%
    elif total_income <= 6950000:
        return Decimal('30.0')  # 20% + 10%
    elif total_income <= 9000000:
        return Decimal('33.0')  # 23% + 10%
    elif total_income <= 18000000:
        return Decimal('43.0')  # 33% + 10%
    elif total_income <= 40000000:
        return Decimal('50.0')  # 40% + 10%
    else:
        return Decimal('55.0')  # 45% + 10%


def calculate_simulation(simulation, db):
    """シミュレーション計算を実行"""
    tenant_id = session.get('tenant_id')
    
    # 既存の結果を削除
    db.execute(
        delete(TSimulationResult).where(TSimulationResult.シミュレーションid == simulation.id)
    )
    db.commit()
    
    # シミュレーション種別による分岐
    property_data = None
    
    if simulation.シミュレーション種別 == '独立':
        # 独立シミュレーション: 手動入力値を使用
        total_rent = simulation.年間家賃収入 or Decimal('0')
    else:
        # 物件ベースシミュレーション: 物件データから取得
        if simulation.物件id:
            property_data = db.execute(
                select(TBukken).where(TBukken.id == simulation.物件id, TBukken.tenant_id == tenant_id)
            ).scalar_one_or_none()
            
            if not property_data:
                return False
            
            # 物件の部屋を取得
            rooms = db.execute(
                select(THeya).where(THeya.property_id == property_data.id, THeya.有効 == 1)
            ).scalars().all()
            
            # 年間家賃収入を計算
            total_rent = sum(room.賃料 or 0 for room in rooms) * 12
        else:
            # 全物件の場合
            properties = db.execute(
                select(TBukken).where(TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
            ).scalars().all()
            
            total_rent = Decimal('0')
            for prop in properties:
                rooms = db.execute(
                    select(THeya).where(THeya.property_id == prop.id, THeya.有効 == 1)
                ).scalars().all()
                total_rent += sum(room.賃料 or 0 for room in rooms) * 12
    
    # 年度ごとにシミュレーション
    current_loan_balance = simulation.ローン残高
    
    for year_offset in range(simulation.期間):
        year = simulation.開始年度 + year_offset
        
        # 収入計算
        家賃収入 = total_rent * (simulation.稼働率 / 100)
        その他収入 = simulation.その他収入
        総収入 = 家賃収入 + その他収入
        
        # 経費計算
        管理費 = 家賃収入 * (simulation.管理費率 / 100)
        修繕費 = 家賃収入 * (simulation.修繕費率 / 100)
        固定資産税 = simulation.固定資産税
        損害保険料 = simulation.損害保険料
        借入金利息 = current_loan_balance * (simulation.ローン金利 / 100)
        その他経費 = simulation.その他経費
        
        # 減価償却費を計算（3分割方式）
        減価償却費 = Decimal('0')
        
        # 建物部分の減価償却費
        if simulation.建物_取得価額 and simulation.建物_取得価額 > 0:
            if simulation.建物_償却方法 == '定額法' and simulation.建物_耐用年数:
                減価償却費 += (simulation.建物_取得価額 - simulation.建物_残存価額) / simulation.建物_耐用年数
            elif simulation.建物_償却方法 == '定率法' and simulation.建物_耐用年数:
                償却率 = Decimal('2.0') / simulation.建物_耐用年数
                # 簡易計算（実際は期首帳簿価額を追跡する必要がある）
                減価償却費 += simulation.建物_取得価額 * 償却率 * (Decimal('0.9') ** year_offset)
        
        # 建物付属設備の減価償却費
        if simulation.付属設備_取得価額 and simulation.付属設備_取得価額 > 0:
            if simulation.付属設備_償却方法 == '定額法' and simulation.付属設備_耐用年数:
                減価償却費 += (simulation.付属設備_取得価額 - simulation.付属設備_残存価額) / simulation.付属設備_耐用年数
            elif simulation.付属設備_償却方法 == '定率法' and simulation.付属設備_耐用年数:
                償却率 = Decimal('2.0') / simulation.付属設備_耐用年数
                減価償却費 += simulation.付属設備_取得価額 * 償却率 * (Decimal('0.9') ** year_offset)
        
        # 構築物の減価償却費
        if simulation.構築物_取得価額 and simulation.構築物_取得価額 > 0:
            if simulation.構築物_償却方法 == '定額法' and simulation.構築物_耐用年数:
                減価償却費 += (simulation.構築物_取得価額 - simulation.構築物_残存価額) / simulation.構築物_耐用年数
            elif simulation.構築物_償却方法 == '定率法' and simulation.構築物_耐用年数:
                償却率 = Decimal('2.0') / simulation.構築物_耐用年数
                減価償却費 += simulation.構築物_取得価額 * 償却率 * (Decimal('0.9') ** year_offset)
        
        # 旧方式の減価償却費が設定されている場合はそれを使用（互換性のため）
        if 減価償却費 == 0 and simulation.減価償却費 and simulation.減価償却費 > 0:
            減価償却費 = simulation.減価償却費
        
        総経費 = 管理費 + 修繕費 + 固定資産税 + 損害保険料 + 借入金利息 + 減価償却費 + その他経費
        
        # 不動産所得
        不動産所得 = 総収入 - 総経費
        
        # 税金計算
        if simulation.税率:
            税率 = simulation.税率
        else:
            税率 = calculate_tax_rate(不動産所得 + simulation.その他所得)
        
        税金 = (不動産所得 + simulation.その他所得) * (税率 / 100)
        if 税金 < 0:
            税金 = Decimal('0')
        
        # キャッシュフロー
        ローン元本返済 = simulation.ローン年間返済額 - 借入金利息
        キャッシュフロー = 総収入 - (総経費 - 減価償却費) - 税金 - ローン元本返済
        
        # ローン残高を更新
        current_loan_balance -= ローン元本返済
        if current_loan_balance < 0:
            current_loan_balance = Decimal('0')
        
        # 結果を保存
        result = TSimulationResult(
            シミュレーションid=simulation.id,
            年度=year,
            家賃収入=家賃収入,
            その他収入=その他収入,
            総収入=総収入,
            管理費=管理費,
            修繕費=修繕費,
            固定資産税=固定資産税,
            損害保険料=損害保険料,
            借入金利息=借入金利息,
            減価償却費=減価償却費,
            その他経費=その他経費,
            総経費=総経費,
            不動産所得=不動産所得,
            税金=税金,
            キャッシュフロー=キャッシュフロー,
            ローン残高=current_loan_balance
        )
        
        db.add(result)
    
    db.commit()
    return True


@property_bp.route('/simulations')
@require_tenant_admin
def simulations():
    """シミュレーション一覧"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    simulations = db.execute(
        select(TSimulation).where(TSimulation.tenant_id == tenant_id)
        .order_by(TSimulation.created_at.desc())
    ).scalars().all()
    
    # 各シミュレーションの物件名を取得
    simulation_list = []
    for sim in simulations:
        if sim.物件id:
            property_data = db.execute(
                select(TBukken).where(TBukken.id == sim.物件id)
            ).scalar_one_or_none()
            property_name = property_data.物件名 if property_data else '不明'
        else:
            property_name = '全物件'
        
        simulation_list.append({
            'simulation': sim,
            'property_name': property_name
        })
    
    db.close()
    return render_template('property_simulations.html', simulations=simulation_list)


@property_bp.route('/simulations/new', methods=['GET', 'POST'])
@require_tenant_admin
def simulation_new():
    """シミュレーション新規作成"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    if request.method == 'POST':
        # フォームデータを取得
        名称 = request.form.get('名称')
        シミュレーション種別 = request.form.get('シミュレーション種別', '物件ベース')
        物件id = request.form.get('物件id')
        年間家賃収入 = request.form.get('年間家賃収入')
        部屋数 = request.form.get('部屋数')
        開始年度 = int(request.form.get('開始年度', date.today().year))
        期間 = int(request.form.get('期間', 10))
        稼働率 = Decimal(request.form.get('稼働率', '95.00'))
        管理費率 = Decimal(request.form.get('管理費率', '5.00'))
        修繕費率 = Decimal(request.form.get('修繕費率', '5.00'))
        固定資産税 = Decimal(request.form.get('固定資産税', '0'))
        損害保険料 = Decimal(request.form.get('損害保険料', '0'))
        ローン残高 = Decimal(request.form.get('ローン残高', '0'))
        ローン金利 = Decimal(request.form.get('ローン金利', '0'))
        ローン年間返済額 = Decimal(request.form.get('ローン年間返済額', '0'))
        その他収入 = Decimal(request.form.get('その他収入', '0'))
        その他経費 = Decimal(request.form.get('その他経費', '0'))
        減価償却費 = Decimal(request.form.get('減価償却費', '0'))
        その他所得 = Decimal(request.form.get('その他所得', '0'))
        
        # 減価償却設定（建物部分）
        建物_取得価額 = Decimal(request.form.get('建物_取得価額', '0'))
        建物_耐用年数 = int(request.form.get('建物_耐用年数', '47'))
        建物_償却方法 = request.form.get('建物_償却方法', '定額法')
        建物_残存価額 = Decimal(request.form.get('建物_残存価額', '0'))
        
        # 減価償却設定（建物付属設備）
        付属設備_取得価額 = Decimal(request.form.get('付属設備_取得価額', '0'))
        付属設備_耐用年数 = int(request.form.get('付属設備_耐用年数', '15'))
        付属設備_償却方法 = request.form.get('付属設備_償却方法', '定額法')
        付属設備_残存価額 = Decimal(request.form.get('付属設備_残存価額', '0'))
        
        # 減価償却設定（構築物）
        構築物_取得価額 = Decimal(request.form.get('構築物_取得価額', '0'))
        構築物_耐用年数 = int(request.form.get('構築物_耐用年数', '20'))
        構築物_償却方法 = request.form.get('構築物_償却方法', '定額法')
        構築物_残存価額 = Decimal(request.form.get('構築物_残存価額', '0'))
        
        # 物件IDの処理
        if 物件id == '' or 物件id == 'all':
            物件id = None
        else:
            物件id = int(物件id)
        
        # 独立シミュレーション用フィールドの変換
        if 年間家賃収入:
            年間家賃収入 = Decimal(年間家賃収入) if 年間家賃収入 else None
        else:
            年間家賃収入 = None
        
        if 部屋数:
            部屋数 = int(部屋数) if 部屋数 else None
        else:
            部屋数 = None
        
        # シミュレーションを作成
        simulation = TSimulation(
            tenant_id=tenant_id,
            名称=名称,
            シミュレーション種別=シミュレーション種別,
            物件id=物件id,
            年間家賃収入=年間家賃収入,
            部屋数=部屋数,
            開始年度=開始年度,
            期間=期間,
            稼働率=稼働率,
            管理費率=管理費率,
            修繕費率=修繕費率,
            固定資産税=固定資産税,
            損害保険料=損害保険料,
            ローン残高=ローン残高,
            ローン金利=ローン金利,
            ローン年間返済額=ローン年間返済額,
            その他収入=その他収入,
            その他経費=その他経費,
            減価償却費=減価償却費,
            その他所得=その他所得,
            # 減価償却設定
            建物_取得価額=建物_取得価額,
            建物_耐用年数=建物_耐用年数,
            建物_償却方法=建物_償却方法,
            建物_残存価額=建物_残存価額,
            付属設備_取得価額=付属設備_取得価額,
            付属設備_耐用年数=付属設備_耐用年数,
            付属設備_償却方法=付属設備_償却方法,
            付属設備_残存価額=付属設備_残存価額,
            構築物_取得価額=構築物_取得価額,
            構築物_耐用年数=構築物_耐用年数,
            構築物_償却方法=構築物_償却方法,
            構築物_残存価額=構築物_残存価額
        )
        
        db.add(simulation)
        db.commit()
        
        # シミュレーション計算を実行
        if calculate_simulation(simulation, db):
            flash('シミュレーションを作成しました', 'success')
            return redirect(url_for('property.simulation_detail', simulation_id=simulation.id))
        else:
            flash('シミュレーションの計算に失敗しました', 'danger')
            return redirect(url_for('property.simulations'))
    
    # GET: フォーム表示
    properties = db.execute(
        select(TBukken).where(TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
    ).scalars().all()
    
    db.close()
    return render_template('property_simulation_new.html', 
                         properties=properties,
                         current_year=date.today().year)


@property_bp.route('/simulations/<int:simulation_id>')
@require_tenant_admin
def simulation_detail(simulation_id):
    """シミュレーション詳細"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    simulation = db.execute(
        select(TSimulation).where(TSimulation.id == simulation_id, TSimulation.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not simulation:
        flash('シミュレーションが見つかりません', 'danger')
        return redirect(url_for('property.simulations'))
    
    # 物件名を取得
    if simulation.物件id:
        property_data = db.execute(
            select(TBukken).where(TBukken.id == simulation.物件id)
        ).scalar_one_or_none()
        property_name = property_data.物件名 if property_data else '不明'
    else:
        property_name = '全物件'
    
    # 結果を取得
    results = db.execute(
        select(TSimulationResult).where(TSimulationResult.シミュレーションid == simulation_id)
        .order_by(TSimulationResult.年度)
    ).scalars().all()
    
    # 累積キャッシュフローを計算
    累積CF = Decimal('0')
    results_with_cumulative = []
    for result in results:
        累積CF += result.キャッシュフロー
        results_with_cumulative.append({
            'result': result,
            '累積キャッシュフロー': 累積CF
        })
    
    db.close()
    return render_template('property_simulation_detail.html',
                         simulation=simulation,
                         property_name=property_name,
                         results=results_with_cumulative)


@property_bp.route('/simulations/<int:simulation_id>/edit', methods=['GET', 'POST'])
@require_tenant_admin
def simulation_edit(simulation_id):
    """シミュレーション編集"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    simulation = db.execute(
        select(TSimulation).where(TSimulation.id == simulation_id, TSimulation.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not simulation:
        flash('シミュレーションが見つかりません', 'danger')
        return redirect(url_for('property.simulations'))
    
    if request.method == 'POST':
        # フォームデータを取得
        simulation.名称 = request.form.get('名称')
        simulation.シミュレーション種別 = request.form.get('シミュレーション種別', '物件ベース')
        物件id = request.form.get('物件id')
        simulation.年間家賃収入 = request.form.get('年間家賃収入')
        simulation.部屋数 = request.form.get('部屋数')
        simulation.開始年度 = int(request.form.get('開始年度', date.today().year))
        simulation.期間 = int(request.form.get('期間', 10))
        simulation.稼働率 = Decimal(request.form.get('稼働率', '95.00'))
        simulation.管理費率 = Decimal(request.form.get('管理費率', '5.00'))
        simulation.修繕費率 = Decimal(request.form.get('修繕費率', '5.00'))
        simulation.固定資産税 = Decimal(request.form.get('固定資産税', '0'))
        simulation.損害保険料 = Decimal(request.form.get('損害保険料', '0'))
        simulation.ローン残高 = Decimal(request.form.get('ローン残高', '0'))
        simulation.ローン金利 = Decimal(request.form.get('ローン金利', '0'))
        simulation.ローン年間返済額 = Decimal(request.form.get('ローン年間返済額', '0'))
        simulation.その他収入 = Decimal(request.form.get('その他収入', '0'))
        simulation.その他経費 = Decimal(request.form.get('その他経費', '0'))
        simulation.減価償却費 = Decimal(request.form.get('減価償却費', '0'))
        simulation.その他所得 = Decimal(request.form.get('その他所得', '0'))
        
        # 減価償却設定（建物部分）
        simulation.建物_取得価額 = Decimal(request.form.get('建物_取得価額', '0'))
        simulation.建物_耐用年数 = int(request.form.get('建物_耐用年数', '47'))
        simulation.建物_償却方法 = request.form.get('建物_償却方法', '定額法')
        simulation.建物_残存価額 = Decimal(request.form.get('建物_残存価額', '0'))
        
        # 減価償却設定（建物付属設備）
        simulation.付属設備_取得価額 = Decimal(request.form.get('付属設備_取得価額', '0'))
        simulation.付属設備_耐用年数 = int(request.form.get('付属設備_耐用年数', '15'))
        simulation.付属設備_償却方法 = request.form.get('付属設備_償却方法', '定額法')
        simulation.付属設備_残存価額 = Decimal(request.form.get('付属設備_残存価額', '0'))
        
        # 減価償却設定（構築物）
        simulation.構築物_取得価額 = Decimal(request.form.get('構築物_取得価額', '0'))
        simulation.構築物_耐用年数 = int(request.form.get('構築物_耐用年数', '20'))
        simulation.構築物_償却方法 = request.form.get('構築物_償却方法', '定額法')
        simulation.構築物_残存価額 = Decimal(request.form.get('構築物_残存価額', '0'))
        
        # 物件IDの処理
        if 物件id == '' or 物件id == 'all':
            simulation.物件id = None
        else:
            simulation.物件id = int(物件id)
        
        # 独立シミュレーション用フィールドの変換
        if simulation.年間家賃収入:
            simulation.年間家賃収入 = Decimal(simulation.年間家賃収入) if simulation.年間家賃収入 else None
        else:
            simulation.年間家賃収入 = None
        
        if simulation.部屋数:
            simulation.部屋数 = int(simulation.部屋数) if simulation.部屋数 else None
        else:
            simulation.部屋数 = None
        
        db.commit()
        
        # シミュレーション計算を再実行
        if calculate_simulation(simulation, db):
            flash('シミュレーションを更新しました', 'success')
            return redirect(url_for('property.simulation_detail', simulation_id=simulation.id))
        else:
            flash('シミュレーションの計算に失敗しました', 'danger')
            return redirect(url_for('property.simulations'))
    
    # GET: フォーム表示
    properties = db.execute(
        select(TBukken).where(TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
    ).scalars().all()
    
    db.close()
    return render_template('property_simulation_edit.html', 
                         simulation=simulation,
                         properties=properties,
                         current_year=date.today().year)

@property_bp.route('/simulations/<int:simulation_id>/delete', methods=['POST'])
@require_tenant_admin
def simulation_delete(simulation_id):
    """シミュレーション削除"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    simulation = db.execute(
        select(TSimulation).where(TSimulation.id == simulation_id, TSimulation.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not simulation:
        flash('シミュレーションが見つかりません', 'danger')
        return redirect(url_for('property.simulations'))
    
    # 結果も削除
    db.execute(
        delete(TSimulationResult).where(TSimulationResult.シミュレーションid == simulation_id)
    )
    
    # シミュレーションを削除
    db.execute(
        delete(TSimulation).where(TSimulation.id == simulation_id)
    )
    
    db.commit()
    db.close()
    
    flash('シミュレーションを削除しました', 'success')
    return redirect(url_for('property.simulations'))


@property_bp.route('/simulations/<int:simulation_id>/recalculate', methods=['POST'])
@require_tenant_admin
def simulation_recalculate(simulation_id):
    """シミュレーション再計算"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    simulation = db.execute(
        select(TSimulation).where(TSimulation.id == simulation_id, TSimulation.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not simulation:
        flash('シミュレーションが見つかりません', 'danger')
        return redirect(url_for('property.simulations'))
    
    # シミュレーション計算を実行
    if calculate_simulation(simulation, db):
        flash('シミュレーションを再計算しました', 'success')
    else:
        flash('シミュレーションの計算に失敗しました', 'danger')
    
    db.close()
    return redirect(url_for('property.simulation_detail', simulation_id=simulation_id))


# ==================== 物件経費管理 ====================

# 経費カテゴリと支払方法の定義
PROPERTY_EXPENSE_CATEGORIES = ['税金', '保険', '管理費', '修繕費', '水道光熱費', 'その他']
ROOM_EXPENSE_CATEGORIES = ['原状回復', 'クリーニング', '仲介手数料', '広告宣伝', '修繕費', '水道光熱費', 'その他']
PAYMENT_METHODS = ['現金', '銀行振込', 'クレジットカード', '口座引落']


@property_bp.route('/properties/<int:property_id>/expenses')
@require_tenant_admin
def expense_list_property(property_id):
    """物件経費一覧"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # 物件の存在確認
    property_data = db.execute(
        select(TBukken).where(TBukken.id == property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 経費一覧を取得
    expenses = db.execute(
        select(TBukkenKeihi).where(TBukkenKeihi.物件id == property_id)
        .order_by(TBukkenKeihi.発生日.desc())
    ).scalars().all()
    
    # 合計金額を計算
    total_amount = sum(expense.金額 for expense in expenses)
    
    db.close()
    return render_template('property_expense_list.html', 
                         property=property_data, 
                         expenses=expenses,
                         total_amount=total_amount)


@property_bp.route('/properties/<int:property_id>/expenses/new', methods=['GET', 'POST'])
@require_tenant_admin
def expense_new_property(property_id):
    """物件経費登録"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # 物件の存在確認
    property_data = db.execute(
        select(TBukken).where(TBukken.id == property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    if request.method == 'POST':
        expense_data = TBukkenKeihi(
            物件id=property_id,
            経費名=request.form.get('経費名'),
            経費カテゴリ=request.form.get('経費カテゴリ'),
            金額=Decimal(request.form.get('金額')),
            発生日=datetime.strptime(request.form.get('発生日'), '%Y-%m-%d').date(),
            支払日=datetime.strptime(request.form.get('支払日'), '%Y-%m-%d').date() if request.form.get('支払日') else None,
            支払方法=request.form.get('支払方法') if request.form.get('支払方法') else None,
            備考=request.form.get('備考')
        )
        
        db.add(expense_data)
        db.commit()
        db.close()
        
        flash('経費を登録しました', 'success')
        return redirect(url_for('property.expense_list_property', property_id=property_id))
    
    db.close()
    return render_template('property_expense_form.html', 
                         property=property_data,
                         categories=PROPERTY_EXPENSE_CATEGORIES,
                         payment_methods=PAYMENT_METHODS,
                         expense=None)


@property_bp.route('/properties/<int:property_id>/expenses/<int:expense_id>/edit', methods=['GET', 'POST'])
@require_tenant_admin
def expense_edit_property(property_id, expense_id):
    """物件経費編集"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # 物件の存在確認
    property_data = db.execute(
        select(TBukken).where(TBukken.id == property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 経費の存在確認
    expense = db.execute(
        select(TBukkenKeihi).where(TBukkenKeihi.物件経費id == expense_id, TBukkenKeihi.物件id == property_id)
    ).scalar_one_or_none()
    
    if not expense:
        flash('経費が見つかりません', 'danger')
        return redirect(url_for('property.expense_list_property', property_id=property_id))
    
    if request.method == 'POST':
        expense.経費名 = request.form.get('経費名')
        expense.経費カテゴリ = request.form.get('経費カテゴリ')
        expense.金額 = Decimal(request.form.get('金額'))
        expense.発生日 = datetime.strptime(request.form.get('発生日'), '%Y-%m-%d').date()
        expense.支払日 = datetime.strptime(request.form.get('支払日'), '%Y-%m-%d').date() if request.form.get('支払日') else None
        expense.支払方法 = request.form.get('支払方法') if request.form.get('支払方法') else None
        expense.備考 = request.form.get('備考')
        expense.updated_at = datetime.now()
        
        db.commit()
        db.close()
        
        flash('経費を更新しました', 'success')
        return redirect(url_for('property.expense_list_property', property_id=property_id))
    
    db.close()
    return render_template('property_expense_form.html', 
                         property=property_data,
                         categories=PROPERTY_EXPENSE_CATEGORIES,
                         payment_methods=PAYMENT_METHODS,
                         expense=expense)


@property_bp.route('/properties/<int:property_id>/expenses/<int:expense_id>/delete', methods=['POST'])
@require_tenant_admin
def expense_delete_property(property_id, expense_id):
    """物件経費削除"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # 物件の存在確認
    property_data = db.execute(
        select(TBukken).where(TBukken.id == property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 経費の存在確認
    expense = db.execute(
        select(TBukkenKeihi).where(TBukkenKeihi.物件経費id == expense_id, TBukkenKeihi.物件id == property_id)
    ).scalar_one_or_none()
    
    if not expense:
        flash('経費が見つかりません', 'danger')
        return redirect(url_for('property.expense_list_property', property_id=property_id))
    
    db.delete(expense)
    db.commit()
    db.close()
    
    flash('経費を削除しました', 'success')
    return redirect(url_for('property.expense_list_property', property_id=property_id))


# ==================== 部屋経費管理 ====================

@property_bp.route('/rooms/<int:room_id>/expenses')
@require_tenant_admin
def expense_list_room(room_id):
    """部屋経費一覧"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # 部屋の存在確認
    room = db.execute(
        select(THeya).where(THeya.id == room_id)
    ).scalar_one_or_none()
    
    if not room:
        flash('部屋が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 物件情報を取得してテナントIDを確認
    property_data = db.execute(
        select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 経費一覧を取得
    expenses = db.execute(
        select(THeyaKeihi).where(THeyaKeihi.部屋id == room_id)
        .order_by(THeyaKeihi.発生日.desc())
    ).scalars().all()
    
    # 合計金額を計算
    total_amount = sum(expense.金額 for expense in expenses)
    
    db.close()
    return render_template('room_expense_list.html', 
                         room=room,
                         property=property_data,
                         expenses=expenses,
                         total_amount=total_amount)


@property_bp.route('/rooms/<int:room_id>/expenses/new', methods=['GET', 'POST'])
@require_tenant_admin
def expense_new_room(room_id):
    """部屋経費登録"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # 部屋の存在確認
    room = db.execute(
        select(THeya).where(THeya.id == room_id)
    ).scalar_one_or_none()
    
    if not room:
        flash('部屋が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 物件情報を取得してテナントIDを確認
    property_data = db.execute(
        select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    if request.method == 'POST':
        expense_data = THeyaKeihi(
            部屋id=room_id,
            経費名=request.form.get('経費名'),
            経費カテゴリ=request.form.get('経費カテゴリ'),
            金額=Decimal(request.form.get('金額')),
            発生日=datetime.strptime(request.form.get('発生日'), '%Y-%m-%d').date(),
            支払日=datetime.strptime(request.form.get('支払日'), '%Y-%m-%d').date() if request.form.get('支払日') else None,
            支払方法=request.form.get('支払方法') if request.form.get('支払方法') else None,
            備考=request.form.get('備考')
        )
        
        db.add(expense_data)
        db.commit()
        db.close()
        
        flash('経費を登録しました', 'success')
        return redirect(url_for('property.expense_list_room', room_id=room_id))
    
    db.close()
    return render_template('room_expense_form.html', 
                         room=room,
                         property=property_data,
                         categories=ROOM_EXPENSE_CATEGORIES,
                         payment_methods=PAYMENT_METHODS,
                         expense=None)


@property_bp.route('/rooms/<int:room_id>/expenses/<int:expense_id>/edit', methods=['GET', 'POST'])
@require_tenant_admin
def expense_edit_room(room_id, expense_id):
    """部屋経費編集"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # 部屋の存在確認
    room = db.execute(
        select(THeya).where(THeya.id == room_id)
    ).scalar_one_or_none()
    
    if not room:
        flash('部屋が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 物件情報を取得してテナントIDを確認
    property_data = db.execute(
        select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 経費の存在確認
    expense = db.execute(
        select(THeyaKeihi).where(THeyaKeihi.部屋経費id == expense_id, THeyaKeihi.部屋id == room_id)
    ).scalar_one_or_none()
    
    if not expense:
        flash('経費が見つかりません', 'danger')
        return redirect(url_for('property.expense_list_room', room_id=room_id))
    
    if request.method == 'POST':
        expense.経費名 = request.form.get('経費名')
        expense.経費カテゴリ = request.form.get('経費カテゴリ')
        expense.金額 = Decimal(request.form.get('金額'))
        expense.発生日 = datetime.strptime(request.form.get('発生日'), '%Y-%m-%d').date()
        expense.支払日 = datetime.strptime(request.form.get('支払日'), '%Y-%m-%d').date() if request.form.get('支払日') else None
        expense.支払方法 = request.form.get('支払方法') if request.form.get('支払方法') else None
        expense.備考 = request.form.get('備考')
        expense.updated_at = datetime.now()
        
        db.commit()
        db.close()
        
        flash('経費を更新しました', 'success')
        return redirect(url_for('property.expense_list_room', room_id=room_id))
    
    db.close()
    return render_template('room_expense_form.html', 
                         room=room,
                         property=property_data,
                         categories=ROOM_EXPENSE_CATEGORIES,
                         payment_methods=PAYMENT_METHODS,
                         expense=expense)


@property_bp.route('/rooms/<int:room_id>/expenses/<int:expense_id>/delete', methods=['POST'])
@require_tenant_admin
def expense_delete_room(room_id, expense_id):
    """部屋経費削除"""
    db = SessionLocal()
    tenant_id = session.get('tenant_id')
    
    # 部屋の存在確認
    room = db.execute(
        select(THeya).where(THeya.id == room_id)
    ).scalar_one_or_none()
    
    if not room:
        flash('部屋が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 物件情報を取得してテナントIDを確認
    property_data = db.execute(
        select(TBukken).where(TBukken.id == room.property_id, TBukken.tenant_id == tenant_id)
    ).scalar_one_or_none()
    
    if not property_data:
        flash('物件が見つかりません', 'danger')
        return redirect(url_for('property.properties'))
    
    # 経費の存在確認
    expense = db.execute(
        select(THeyaKeihi).where(THeyaKeihi.部屋経費id == expense_id, THeyaKeihi.部屋id == room_id)
    ).scalar_one_or_none()
    
    if not expense:
        flash('経費が見つかりません', 'danger')
        return redirect(url_for('property.expense_list_room', room_id=room_id))
    
    db.delete(expense)
    db.commit()
    db.close()
    
    flash('経費を削除しました', 'success')
    return redirect(url_for('property.expense_list_room', room_id=room_id))
