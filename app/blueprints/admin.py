# -*- coding: utf-8 -*-
"""
管理者ダッシュボード（SQLAlchemy版）
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import SessionLocal
from app.models_login import TKanrisha, TJugyoin, TTenant, TTenpo, TKanrishaTenpo, TJugyoinTenpo, TTenpoAppSetting, TTenantAdminTenant
from sqlalchemy import func, and_, or_
from ..utils.decorators import ROLES
from ..utils.decorators import require_roles

bp = Blueprint('admin', __name__, url_prefix='/admin')

# 利用可能なアプリの定義
AVAILABLE_APPS = [
    {'name': 'survey-app', 'display_name': 'アンケートアプリ', 'scope': 'store'}
]


@bp.route('/')
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def dashboard():
    """管理者ダッシュボード"""
    # 店舗で有効なアプリを取得
    store_id = session.get('store_id')
    tenant_id = session.get('tenant_id')
    enabled_apps = []
    
    if store_id:
        db = SessionLocal()
        
        try:
            for app in AVAILABLE_APPS:
                if app['scope'] == 'store':
                    app_setting = db.query(TTenpoAppSetting).filter(
                        and_(
                            TTenpoAppSetting.store_id == store_id,
                            TTenpoAppSetting.app_name == app['name']
                        )
                    ).first()
                    enabled = app_setting.enabled if app_setting else 1
                    
                    if enabled:
                        enabled_apps.append(app)
        finally:
            db.close()
    
    return render_template('admin_dashboard.html', tenant_id=tenant_id, apps=enabled_apps)


@bp.route('/available_apps')
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def available_apps():
    """利用可能アプリ一覧"""
    store_id = session.get('store_id')
    tenant_id = session.get('tenant_id')
    enabled_apps = []
    
    if store_id:
        db = SessionLocal()
        
        try:
            for app in AVAILABLE_APPS:
                if app['scope'] == 'store':
                    app_setting = db.query(TTenpoAppSetting).filter(
                        and_(
                            TTenpoAppSetting.store_id == store_id,
                            TTenpoAppSetting.app_name == app['name']
                        )
                    ).first()
                    enabled = app_setting.enabled if app_setting else 1
                    
                    if enabled:
                        enabled_apps.append(app)
        finally:
            db.close()
    
    # マイページURLを取得
    user_role = session.get('role')
    if user_role == ROLES["SYSTEM_ADMIN"]:
        mypage_url = url_for('system_admin.mypage')
    elif user_role == ROLES["TENANT_ADMIN"]:
        mypage_url = url_for('tenant_admin.mypage')
    else:
        mypage_url = url_for('admin.mypage')
    
    return render_template('admin_available_apps.html', tenant_id=tenant_id, apps=enabled_apps, mypage_url=mypage_url)


@bp.route('/mypage', methods=['GET', 'POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def mypage():
    """管理者マイページ"""
    user_id = session.get('user_id')
    tenant_id = session.get('tenant_id')
    db = SessionLocal()
    
    try:
        # ユーザー情報を取得
        user_obj = db.query(TKanrisha).filter(
            TKanrisha.id == user_id,
            TKanrisha.role == ROLES["ADMIN"]
        ).first()
        
        if not user_obj:
            flash('ユーザー情報が見つかりません', 'error')
            return redirect(url_for('admin.dashboard'))
        
        user = {
            'id': user_obj.id,
            'login_id': user_obj.login_id,
            'name': user_obj.name,
            'email': user_obj.email or '',
            'can_manage_admins': user_obj.can_manage_admins or False,
            'created_at': user_obj.created_at,
            'updated_at': user_obj.updated_at if hasattr(user_obj, 'updated_at') else None
        }
        
        # テナント名を取得
        tenant_name = '未選択'
        if tenant_id:
            tenant_obj = db.query(TTenant).filter(TTenant.id == tenant_id).first()
            tenant_name = tenant_obj.名称 if tenant_obj else '不明'
        
        # 所属店舗リストを取得（管理者が管理する店舗）
        store_objs = db.query(TTenpo).join(
            TKanrishaTenpo, TKanrishaTenpo.store_id == TTenpo.id
        ).filter(
            TKanrishaTenpo.admin_id == user_id
        ).order_by(TTenpo.名称).all()
        stores = [s.名称 for s in store_objs]
        store_list = [{'id': s.id, 'name': s.名称} for s in store_objs]
        
        # POSTリクエスト（プロフィール編集またはパスワード変更）
        if request.method == 'POST':
            action = request.form.get('action', '')
            
            if action == 'update_profile':
                # プロフィール編集
                login_id = request.form.get('login_id', '').strip()
                name = request.form.get('name', '').strip()
                email = request.form.get('email', '').strip()
                
                if not login_id or not name:
                    flash('ログインIDと氏名は必須です', 'error')
                    return render_template('admin_mypage.html', user=user, tenant_name=tenant_name, stores=stores, store_list=store_list)
                
                # ログインID重複チェック（自分以外）
                existing = db.query(TKanrisha).filter(
                    TKanrisha.login_id == login_id,
                    TKanrisha.id != user_id
                ).first()
                if existing:
                    flash('このログインIDは既に使用されています', 'error')
                    return render_template('admin_mypage.html', user=user, tenant_name=tenant_name, stores=stores, store_list=store_list)
                
                # プロフィール更新
                user_obj.login_id = login_id
                user_obj.name = name
                user_obj.email = email
                if hasattr(user_obj, 'updated_at'):
                    user_obj.updated_at = func.now()
                db.commit()
                
                flash('プロフィール情報を更新しました', 'success')
                return redirect(url_for('admin.mypage'))
            
            elif action == 'change_password':
                # パスワード変更
                current_password = request.form.get('current_password', '').strip()
                new_password = request.form.get('new_password', '').strip()
                new_password_confirm = request.form.get('new_password_confirm', '').strip()
            
                # パスワード一致チェック
                if new_password != new_password_confirm:
                    flash('パスワードが一致しません', 'error')
                    return render_template('admin_mypage.html', user=user, tenant_name=tenant_name, stores=stores, store_list=store_list)
                
                # 現在のパスワードを確認
                if not check_password_hash(user_obj.password_hash, current_password):
                    flash('現在のパスワードが正しくありません', 'error')
                    return render_template('admin_mypage.html', user=user, tenant_name=tenant_name, stores=stores, store_list=store_list)
                
                # パスワードを更新
                user_obj.password_hash = generate_password_hash(new_password)
                if hasattr(user_obj, 'updated_at'):
                    user_obj.updated_at = func.now()
                db.commit()
                
                flash('パスワードを変更しました', 'success')
                return redirect(url_for('admin.mypage'))
        
        return render_template('admin_mypage.html', user=user, tenant_name=tenant_name, stores=stores, store_list=store_list)
    finally:
        db.close()


@bp.route('/store_info')
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def store_info():
    """店舗情報表示"""
    tenant_id = session.get('tenant_id')
    store_id = session.get('store_id')
    user_id = session.get('user_id')
    db = SessionLocal()
    
    try:
        # セッションにstore_idがない場合はダッシュボードにリダイレクト
        if not store_id:
            flash('店舗が選択されていません', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # 選択された店舗の情報を取得
        store_obj = db.query(TTenpo).filter(TTenpo.id == store_id).first()
        
        if not store_obj:
            flash('店舗情報が見つかりません', 'error')
            return redirect(url_for('admin.dashboard'))
        
        store = {
            'id': store_obj.id,
            '名称': store_obj.名称,
            'slug': store_obj.slug,
            '郵便番号': store_obj.郵便番号 if hasattr(store_obj, '郵便番号') else None,
            '住所': store_obj.住所 if hasattr(store_obj, '住所') else None,
            '電話番号': store_obj.電話番号 if hasattr(store_obj, '電話番号') else None,
            'email': store_obj.email if hasattr(store_obj, 'email') else None,
            'openai_api_key': store_obj.openai_api_key if hasattr(store_obj, 'openai_api_key') else None,
            'created_at': store_obj.created_at,
            'updated_at': store_obj.updated_at if hasattr(store_obj, 'updated_at') else None
        }
        
        return render_template('admin_store_info.html', store=store)
    finally:
        db.close()


@bp.route('/store/<int:store_id>')
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def store_detail(store_id):
    """店舗詳細"""
    tenant_id = session.get('tenant_id')
    db = SessionLocal()
    
    try:
        store_obj = db.query(TTenpo).filter(
            and_(TTenpo.id == store_id, TTenpo.tenant_id == tenant_id)
        ).first()
        
        if not store_obj:
            flash('店舗が見つかりません', 'error')
            return redirect(url_for('admin.store_info'))
        
        store = {
            'id': store_obj.id,
            '名称': store_obj.名称,
            'slug': store_obj.slug,
            '郵便番号': store_obj.郵便番号 if hasattr(store_obj, '郵便番号') else None,
            '住所': store_obj.住所 if hasattr(store_obj, '住所') else None,
            '電話番号': store_obj.電話番号 if hasattr(store_obj, '電話番号') else None,
            'email': store_obj.email if hasattr(store_obj, 'email') else None,
            'openai_api_key': store_obj.openai_api_key if hasattr(store_obj, 'openai_api_key') else None,
            '有効': store_obj.有効,
            'created_at': store_obj.created_at
        }
        
        return render_template('admin_store_detail.html', store=store)
    finally:
        db.close()


@bp.route('/admins')
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def admins():
    """店舗管理者一覧"""
    store_id = session.get('store_id')
    tenant_id = session.get('tenant_id')
    user_id = session.get('user_id')
    
    if not store_id:
        flash('店舗を選択してください。マイページの「店舗選択」から店舗を選んでダッシュボードへ進んでください。', 'warning')
        return redirect(url_for('admin.mypage'))
    
    db = SessionLocal()
    
    try:
        # 現在のユーザーがオーナーかどうかを中間テーブルから確認
        current_admin_rel = db.query(TKanrishaTenpo).filter(
            and_(TKanrishaTenpo.admin_id == user_id, TKanrishaTenpo.store_id == store_id)
        ).first()
        is_owner = current_admin_rel.is_owner if current_admin_rel else False
        can_manage_admins = current_admin_rel.can_manage_admins if current_admin_rel else False
        
        # 店舗に紐づく管理者を取得
        admin_relations = db.query(TKanrishaTenpo).filter(
            TKanrishaTenpo.store_id == store_id
        ).all()
        
        admins_data = []
        for rel in admin_relations:
            admin = db.query(TKanrisha).filter(TKanrisha.id == rel.admin_id).first()
            if admin:
                admins_data.append({
                    'id': admin.id,
                    'login_id': admin.login_id,
                    'name': admin.name,
                    'email': admin.email,
                    'active': admin.active,
                    'is_owner': rel.is_owner,
                    'can_manage_admins': rel.can_manage_admins,
                    'created_at': admin.created_at.strftime('%Y-%m-%d %H:%M:%S') if admin.created_at else '-'
                })
        
        return render_template('admin_admins.html', 
                             admins=admins_data, 
                             current_user_id=user_id,
                             is_owner=is_owner,
                             can_manage_admins=can_manage_admins)
    finally:
        db.close()


@bp.route('/employees')
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def employees():
    """従業員一覧"""
    store_id = session.get('store_id')
    tenant_id = session.get('tenant_id')
    
    if not store_id:
        flash('店舗を選択してください。マイページの「店舗選択」から店舗を選んでダッシュボードへ進んでください。', 'warning')
        return redirect(url_for('admin.mypage'))
    
    db = SessionLocal()
    
    try:
        # 店舗に紐づく従業員を取得
        employee_relations = db.query(TJugyoinTenpo).filter(
            TJugyoinTenpo.store_id == store_id
        ).all()
        
        employees_data = []
        for rel in employee_relations:
            employee = db.query(TJugyoin).filter(TJugyoin.id == rel.employee_id).first()
            if employee:
                employees_data.append({
                    'id': employee.id,
                    'login_id': employee.login_id,
                    'name': employee.name,
                    'email': employee.email,
                    'active': employee.active
                })
        
        return render_template('admin_employees.html', employees=employees_data)
    finally:
        db.close()


@bp.route('/employees/new', methods=['GET', 'POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def employee_new():
    """従業員新規作成"""
    store_id = session.get('store_id')
    tenant_id = session.get('tenant_id')
    admin_id = session.get('user_id')
    
    if not store_id:
        flash('店舗を選択してください。マイページの「店舗選択」から店舗を選んでダッシュボードへ進んでください。', 'warning')
        return redirect(url_for('admin.mypage'))
    
    db = SessionLocal()
    
    try:
        # ユーザーのロールを確認
        user_role = session.get('role')
        
        # テナント管理者またはシステム管理者の場合は、テナントに属するすべての店舗を取得
        if user_role in ['system_admin', 'tenant_admin']:
            stores_list = db.query(TTenpo).filter(
                TTenpo.tenant_id == tenant_id
            ).order_by(TTenpo.id).all()
        else:
            # 店舗管理者の場合は、管理する店舗一覧を取得
            stores_list = db.query(TTenpo).join(
                TKanrishaTenpo, TTenpo.id == TKanrishaTenpo.store_id
            ).filter(
                TKanrishaTenpo.admin_id == admin_id
            ).order_by(TTenpo.id).all()
        
        if request.method == 'POST':
            login_id = request.form.get('login_id', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')
            store_ids = request.form.getlist('store_ids')
            
            # 作成元の店舗IDを必ず含める
            if str(store_id) not in store_ids:
                store_ids.append(str(store_id))
            
            # バリデーション
            if not login_id or not name or not email:
                flash('ログインID、氏名、メールアドレスは必須です', 'error')
                return render_template('admin_employee_new.html', stores=stores_list, from_store_id=store_id, back_url=url_for('admin.employees'))
            
            if not store_ids:
                flash('少なくとも1つの店舗を選択してください', 'error')
                return render_template('admin_employee_new.html', stores=stores_list, from_store_id=store_id, back_url=url_for('admin.employees'))
            
            if password and password != password_confirm:
                flash('パスワードが一致しません', 'error')
                return render_template('admin_employee_new.html', stores=stores_list, from_store_id=store_id, back_url=url_for('admin.employees'))
            
            if password and len(password) < 8:
                flash('パスワードは8文字以上にしてください', 'error')
                return render_template('admin_employee_new.html', stores=stores_list, from_store_id=store_id, back_url=url_for('admin.employees'))
            
            # ログインID重複チェック
            existing = db.query(TJugyoin).filter(TJugyoin.login_id == login_id).first()
            if existing:
                flash(f'ログインID "{login_id}" は既に使用されています', 'error')
                return render_template('admin_employee_new.html', stores=stores_list, from_store_id=store_id, back_url=url_for('admin.employees'))
            
            # 従業員作成
            hashed_password = generate_password_hash(password) if password else None
            new_employee = TJugyoin(
                login_id=login_id,
                name=name,
                email=email,
                password_hash=hashed_password,
                role=ROLES["EMPLOYEE"],
                tenant_id=tenant_id,
                active=1
            )
            db.add(new_employee)
            db.flush()  # IDを取得するため
            
            # 選択された店舗との関連を作成
            for store_id_str in store_ids:
                store_id_int = int(store_id_str)
                new_relation = TJugyoinTenpo(
                    employee_id=new_employee.id,
                    store_id=store_id_int
                )
                db.add(new_relation)
            db.commit()
            
            flash(f'従業員 "{name}" を作成しました', 'success')
            return redirect(url_for('admin.employees'))
        
        return render_template('admin_employee_new.html', stores=stores_list, from_store_id=store_id, back_url=url_for('admin.employees'))
    finally:
        db.close()


@bp.route('/employees/<int:employee_id>/toggle', methods=['POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def employee_toggle(employee_id):
    """従業員の有効/無効切り替え"""
    db = SessionLocal()
    
    try:
        employee = db.query(TJugyoin).filter(TJugyoin.id == employee_id).first()
        
        if employee:
            employee.active = 0 if employee.active == 1 else 1
            db.commit()
            flash('ステータスを更新しました', 'success')
        
        return redirect(url_for('admin.employees'))
    finally:
        db.close()


@bp.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def employee_edit(employee_id):
    """従業員編集"""
    db = SessionLocal()
    
    try:
        if request.method == 'POST':
            login_id = request.form.get('login_id', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            role = request.form.get('role', 'employee').strip()
            password = request.form.get('password', '').strip()
            active = 1 if request.form.get('active') == '1' else 0
            
            if not login_id or not name or not email:
                flash('ログインID、氏名、メールアドレスは必須です', 'error')
            else:
                # ログインIDの重複チェック
                existing = db.query(TJugyoin).filter(
                    and_(TJugyoin.login_id == login_id, TJugyoin.id != employee_id)
                ).first()
                if existing:
                    flash('このログインIDは既に使用されています', 'error')
                else:
                    employee = db.query(TJugyoin).filter(TJugyoin.id == employee_id).first()
                    
                    if employee:
                        # 役割変更の処理
                        old_role = employee.role
                        new_role = role
                        tenant_id = session.get('tenant_id')
                        store_ids = request.form.getlist('store_ids')
                        
                        if old_role != new_role:
                            # 従業員から店舗管理者に変更
                            if old_role == ROLES["EMPLOYEE"] and new_role == ROLES["ADMIN"]:
                                # 従業員テーブルから削除
                                db.query(TJugyoinTenpo).filter(TJugyoinTenpo.employee_id == employee_id).delete()
                                # 店舗管理者テーブルに移動（TKanrishaに移動）
                                new_admin = TKanrisha(
                                    login_id=employee.login_id,
                                    name=name,
                                    email=email,
                                    password_hash=employee.password_hash if not password else generate_password_hash(password),
                                    role=ROLES["ADMIN"],
                                    tenant_id=tenant_id,
                                    active=active
                                )
                                db.add(new_admin)
                                db.flush()
                                # 店舗管理者として店舗に追加
                                if store_ids:
                                    for store_id in store_ids:
                                        new_relation = TKanrishaTenpo(
                                            admin_id=new_admin.id,
                                            store_id=int(store_id),
                                            is_owner=0,
                                            can_manage_admins=0
                                        )
                                        db.add(new_relation)
                                # 元の従業員レコードを削除
                                db.delete(employee)
                                db.commit()
                                flash(f'"{name}"を店舗管理者に変更しました', 'success')
                                return redirect(url_for('admin.employees'))
                            
                            # 従業員からテナント管理者に変更
                            elif old_role == ROLES["EMPLOYEE"] and new_role == ROLES["TENANT_ADMIN"]:
                                # 従業員テーブルから削除
                                db.query(TJugyoinTenpo).filter(TJugyoinTenpo.employee_id == employee_id).delete()
                                # テナント管理者テーブルに移動（TKanrishaに移動）
                                new_admin = TKanrisha(
                                    login_id=employee.login_id,
                                    name=name,
                                    email=email,
                                    password_hash=employee.password_hash if not password else generate_password_hash(password),
                                    role=ROLES["TENANT_ADMIN"],
                                    tenant_id=tenant_id,
                                    active=active
                                )
                                db.add(new_admin)
                                db.flush()
                                # テナント管理者としてテナントに追加
                                new_relation = TTenantAdminTenant(
                                    admin_id=new_admin.id,
                                    tenant_id=tenant_id,
                                    is_owner=0,
                                    can_manage_admins=0
                                )
                                db.add(new_relation)
                                # 元の従業員レコードを削除
                                db.delete(employee)
                                db.commit()
                                flash(f'"{name}"をテナント管理者に変更しました', 'success')
                                return redirect(url_for('admin.employees'))
                            else:
                                flash('役割変更は従業員からのみ対応しています', 'error')
                        else:
                            # 役割変更がない場合は通常の更新
                            employee.login_id = login_id
                            employee.name = name
                            employee.email = email
                            employee.active = active
                            if password:
                                employee.password_hash = generate_password_hash(password)
                            
                            # 店舗所属の更新
                            if store_ids:
                                # 既存の店舗所属を削除
                                db.query(TJugyoinTenpo).filter(
                                    TJugyoinTenpo.employee_id == employee_id
                                ).delete()
                                
                                # 新しい店舗所属を追加
                                for store_id in store_ids:
                                    rel = TJugyoinTenpo(
                                        employee_id=employee_id,
                                        store_id=int(store_id)
                                    )
                                    db.add(rel)
                            
                            db.commit()
                            flash('従業員を更新しました', 'success')
                            return redirect(url_for('admin.employees'))
        
        # GETリクエスト時は現在の情報を表示
        employee = db.query(TJugyoin).filter(TJugyoin.id == employee_id).first()
        
        if not employee:
            flash('従業員が見つかりません', 'error')
            return redirect(url_for('admin.employees'))
        
        # テナントIDを取得
        tenant_id = session.get('tenant_id')
        
        # テナントの全店舗を取得
        stores = db.query(TTenpo).filter(TTenpo.tenant_id == tenant_id).all()
        store_list = [{'id': s.id, '名称': s.名称} for s in stores]
        
        # 従業員が所属している店舗IDを取得
        assigned_stores = db.query(TJugyoinTenpo).filter(
            TJugyoinTenpo.employee_id == employee_id
        ).all()
        assigned_store_ids = [rel.store_id for rel in assigned_stores]
        
        employee_data = {
            'id': employee.id,
            'login_id': employee.login_id,
            'name': employee.name,
            'email': employee.email,
            'active': employee.active,
            'role': employee.role
        }
        
        return render_template('admin_employee_edit.html', 
                             employee=employee_data,
                             stores=store_list,
                             assigned_store_ids=assigned_store_ids)
    finally:
        db.close()


@bp.route('/employees/<int:employee_id>/delete', methods=['POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def employee_delete(employee_id):
    """従業員削除"""
    db = SessionLocal()
    
    try:
        employee = db.query(TJugyoin).filter(TJugyoin.id == employee_id).first()
        
        if employee:
            # 店舗との紐付けも削除
            db.query(TJugyoinTenpo).filter(TJugyoinTenpo.employee_id == employee_id).delete()
            db.delete(employee)
            db.commit()
            flash('従業員を削除しました', 'success')
        
        return redirect(url_for('admin.employees'))
    finally:
        db.close()

@bp.route('/employees/invite', methods=['GET', 'POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def employee_invite():
    """既存の従業員を招待"""
    tenant_id = session.get('tenant_id')
    
    if not tenant_id:
        flash('テナントIDが取得できません', 'error')
        return redirect(url_for('admin.dashboard'))
    
    db = SessionLocal()
    
    try:
        # テナント名を取得
        tenant = db.query(TTenant).filter(TTenant.id == tenant_id).first()
        tenant_name = tenant.名称 if tenant else 'テストテナント'
        
        if request.method == 'POST':
            login_id = request.form.get('login_id', '').strip()
            name = request.form.get('name', '').strip()
            
            # バリデーション
            if not login_id or not name:
                flash('ログインIDと氏名は必須です', 'error')
                return render_template('admin_employee_invite.html', tenant_name=tenant_name)
            
            # ログインIDと氏名が一致する従業員を検索
            existing_employee = db.query(TJugyoin).filter(
                and_(
                    TJugyoin.login_id == login_id,
                    TJugyoin.name == name,
                    TJugyoin.tenant_id == tenant_id
                )
            ).first()
            
            if not existing_employee:
                flash(f'ログインID「{login_id}」と氏名「{name}」が一致する従業員が見つかりません', 'error')
                return render_template('admin_employee_invite.html', tenant_name=tenant_name)
            
            flash(f'従業員「{name}」は既にこのテナントに所属しています', 'info')
            return redirect(url_for('admin.employees'))
        
        return render_template('admin_employee_invite.html', tenant_name=tenant_name)
    finally:
        db.close()



@bp.route('/store/<int:store_id>/edit', methods=['GET', 'POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def store_edit(store_id):
    """店舗編集"""
    tenant_id = session.get('tenant_id')
    session_store_id = session.get('store_id')
    db = SessionLocal()
    
    try:
        # セッションのstore_idと一致するか確認
        if store_id != session_store_id:
            flash('この店舗を編集する権限がありません', 'error')
            return redirect(url_for('admin.store_info'))
        
        store_obj = db.query(TTenpo).filter(
            and_(TTenpo.id == store_id, TTenpo.tenant_id == tenant_id)
        ).first()
        
        if not store_obj:
            flash('店舗が見つかりません', 'error')
            return redirect(url_for('admin.store_info'))
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            slug = request.form.get('slug', '').strip()
            postal_code = request.form.get('postal_code', '').strip()
            address = request.form.get('address', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            openai_api_key = request.form.get('openai_api_key', '').strip()
            
            if not name or not slug:
                flash('名称とSlugは必須です', 'error')
                return render_template('admin_store_edit.html', store=store_obj)
            
            # Slug重複チェック（自分以外）
            existing = db.query(TTenpo).filter(
                and_(
                    TTenpo.slug == slug,
                    TTenpo.tenant_id == tenant_id,
                    TTenpo.id != store_id
                )
            ).first()
            
            if existing:
                flash(f'Slug "{slug}" は既に使用されています', 'error')
                return render_template('admin_store_edit.html', store=store_obj)
            
            # 更新
            store_obj.名称 = name
            store_obj.slug = slug
            store_obj.郵便番号 = postal_code if postal_code else None
            store_obj.住所 = address if address else None
            store_obj.電話番号 = phone if phone else None
            store_obj.email = email if email else None
            store_obj.openai_api_key = openai_api_key if openai_api_key else None
            db.commit()
            
            flash('店舗情報を更新しました', 'success')
            return redirect(url_for('admin.store_info'))
        
        return render_template('admin_store_edit.html', store=store_obj)
    finally:
        db.close()


@bp.route('/store/<int:store_id>/delete', methods=['POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def store_delete(store_id):
    """店舗削除"""
    tenant_id = session.get('tenant_id')
    session_store_id = session.get('store_id')
    user_id = session.get('user_id')
    db = SessionLocal()
    
    try:
        # パスワード検証
        password = request.form.get('password')
        if not password:
            flash('パスワードを入力してください', 'error')
            return redirect(url_for('admin.store_info'))
        
        # ユーザーを取得してパスワードを検証
        user = db.query(TKanrisha).filter(TKanrisha.id == user_id).first()
        if not user or not check_password_hash(user.password, password):
            flash('パスワードが正しくありません', 'error')
            return redirect(url_for('admin.store_info'))
        
        # セッションのstore_idと一致するか確認
        if store_id != session_store_id:
            flash('この店舗を削除する権限がありません', 'error')
            return redirect(url_for('admin.store_info'))
        
        store_obj = db.query(TTenpo).filter(
            and_(TTenpo.id == store_id, TTenpo.tenant_id == tenant_id)
        ).first()
        
        if not store_obj:
            flash('店舗が見つかりません', 'error')
            return redirect(url_for('admin.store_info'))
        
        # 関連データの削除（必要に応じて）
        # 店舗管理者の関連を削除
        db.query(TKanrishaTenpo).filter(TKanrishaTenpo.store_id == store_id).delete()
        
        # 従業員の関連を削除
        db.query(TJugyoinTenpo).filter(TJugyoinTenpo.store_id == store_id).delete()
        
        # アプリ設定を削除
        db.query(TTenpoAppSetting).filter(TTenpoAppSetting.store_id == store_id).delete()
        
        # 店舗を削除
        db.delete(store_obj)
        db.commit()
        
        # セッションから店舗IDを削除
        session.pop('store_id', None)
        
        flash('店舗を削除しました', 'success')
        
        # ユーザーの役割に応じてリダイレクト
        user_role = session.get('role')
        if user_role == ROLES["SYSTEM_ADMIN"]:
            return redirect(url_for('system_admin.mypage'))
        elif user_role == ROLES["TENANT_ADMIN"]:
            return redirect(url_for('tenant_admin.mypage'))
        else:
            return redirect(url_for('auth.logout'))
    finally:
        db.close()


@bp.route('/mypage/select_store', methods=['POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def select_store_from_mypage():
    """マイページから店舗を選択してダッシュボードへ進む"""
    store_id = request.form.get('store_id')
    
    if not store_id:
        flash('店舗を選択してください', 'error')
        return redirect(url_for('admin.mypage'))
    
    session['store_id'] = int(store_id)
    flash('店舗を選択しました', 'success')
    return redirect(url_for('admin.dashboard'))


@bp.route('/admins/<int:admin_id>/edit', methods=['GET', 'POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def admin_edit(admin_id):
    """店舗管理者編集"""
    user_id = session.get('user_id')
    tenant_id = session.get('tenant_id')
    
    db = SessionLocal()
    
    try:
        # 権限チェック（システム管理者とテナント管理者は無条件で許可）
        role = session.get('role')
        store_id = session.get('store_id')
        if role not in ['system_admin', 'tenant_admin']:
            # 店舗管理者の場合は中間テーブルから権限をチェック
            current_admin_rel = db.query(TKanrishaTenpo).filter(
                and_(TKanrishaTenpo.admin_id == user_id, TKanrishaTenpo.store_id == store_id)
            ).first()
            if not current_admin_rel or (current_admin_rel.is_owner != 1 and current_admin_rel.can_manage_admins != 1):
                flash('管理者を編集する権限がありません', 'error')
                return redirect(url_for('admin.dashboard'))
        
        # 店舗一覧を取得
        stores = db.query(TTenpo).filter(
            and_(TTenpo.tenant_id == tenant_id, TTenpo.有効 == 1)
        ).order_by(TTenpo.名称).all()
        
        stores_data = [{'id': store.id, '名称': store.名称} for store in stores]
        
        if request.method == 'POST':
            login_id = request.form.get('login_id', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            password_confirm = request.form.get('password_confirm', '').strip()
            store_ids = request.form.getlist('store_ids')
            active = int(request.form.get('active', 1))
            
            # 編集対象の管理者を取得
            admin = db.query(TKanrisha).filter(
                and_(
                    TKanrisha.id == admin_id,
                    TKanrisha.tenant_id == tenant_id,
                    TKanrisha.role == ROLES["ADMIN"]
                )
            ).first()
            
            if not admin:
                flash('管理者が見つかりません', 'error')
                return redirect(url_for('admin.admins'))
            
            is_owner = admin.is_owner
            
            if not login_id or not name:
                flash('ログインIDと氏名は必須です', 'error')
            elif password and password != password_confirm:
                flash('パスワードが一致しません', 'error')
            elif not store_ids:
                flash('少なくとも1つの店舗を選択してください', 'error')
            elif is_owner == 1 and active == 0:
                flash('オーナーを無効にすることはできません。先にオーナー権限を移譲してください。', 'error')
            else:
                # 重複チェック（自分以外）
                existing = db.query(TKanrisha).filter(
                    and_(TKanrisha.login_id == login_id, TKanrisha.id != admin_id)
                ).first()
                
                if existing:
                    flash(f'ログインID "{login_id}" は既に使用されています', 'error')
                else:
                    # 管理者情報を更新
                    admin.login_id = login_id
                    admin.name = name
                    admin.email = email
                    admin.active = active
                    
                    if password:
                        admin.password_hash = generate_password_hash(password)
                    
                    # 所属店舗を更新
                    # 既存の所属店舗を削除
                    db.query(TKanrishaTenpo).filter(TKanrishaTenpo.admin_id == admin_id).delete()
                    
                    # 新しい所属店舗を追加
                    for store_id in store_ids:
                        new_relation = TKanrishaTenpo(
                            admin_id=admin_id,
                            store_id=int(store_id)
                        )
                        db.add(new_relation)
                    
                    db.commit()
                    flash('管理者情報を更新しました', 'success')
                    return redirect(url_for('admin.admins'))
        
        # GETリクエスト：管理者情報を取得
        admin = db.query(TKanrisha).filter(
            and_(
                TKanrisha.id == admin_id,
                TKanrisha.tenant_id == tenant_id,
                TKanrisha.role == ROLES["ADMIN"]
            )
        ).first()
        
        if not admin:
            flash('管理者が見つかりません', 'error')
            return redirect(url_for('admin.admins'))
        
        admin_data = {
            'id': admin.id,
            'login_id': admin.login_id,
            'name': admin.name,
            'email': admin.email,
            'is_owner': admin.is_owner,
            'active': admin.active if admin.active is not None else 1
        }
        
        # 現在の所属店舗を取得
        admin_store_relations = db.query(TKanrishaTenpo).filter(
            TKanrishaTenpo.admin_id == admin_id
        ).all()
        admin_store_ids = [rel.store_id for rel in admin_store_relations]
        
        return render_template('admin_admin_edit.html', 
                             admin=admin_data, 
                             stores=stores_data, 
                             admin_store_ids=admin_store_ids, 
                             back_url=url_for('admin.admins'))
    finally:
        db.close()


@bp.route('/admins/<int:admin_id>/delete', methods=['POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def admin_delete(admin_id):
    """店舗管理者削除"""
    user_id = session.get('user_id')
    tenant_id = session.get('tenant_id')
    
    db = SessionLocal()
    
    try:
        # 権限チェック（システム管理者とテナント管理者は無条件で許可）
        role = session.get('role')
        store_id = session.get('store_id')
        if role not in ['system_admin', 'tenant_admin']:
            # 店舗管理者の場合は中間テーブルから権限をチェック
            current_admin_rel = db.query(TKanrishaTenpo).filter(
                and_(TKanrishaTenpo.admin_id == user_id, TKanrishaTenpo.store_id == store_id)
            ).first()
            if not current_admin_rel or (current_admin_rel.is_owner != 1 and current_admin_rel.can_manage_admins != 1):
                flash('管理者を削除する権限がありません', 'error')
                return redirect(url_for('admin.dashboard'))
        
        # 削除対象の管理者を取得
        admin = db.query(TKanrisha).filter(
            and_(
                TKanrisha.id == admin_id,
                TKanrisha.tenant_id == tenant_id,
                TKanrisha.role == ROLES["ADMIN"]
            )
        ).first()
        
        if not admin:
            flash('管理者が見つかりません', 'error')
            return redirect(url_for('admin.admins'))
        
        # オーナーは削除できない
        if admin.is_owner == 1:
            flash('オーナーは削除できません', 'error')
        else:
            # 所属店舗の関連を削除
            db.query(TKanrishaTenpo).filter(TKanrishaTenpo.admin_id == admin_id).delete()
            
            # 管理者を削除
            db.delete(admin)
            db.commit()
            flash('管理者を削除しました', 'success')
        
        return redirect(url_for('admin.admins'))
    finally:
        db.close()


@bp.route('/admins/<int:admin_id>/transfer_owner', methods=['POST'])
@require_roles(ROLES["ADMIN"], ROLES["TENANT_ADMIN"], ROLES["SYSTEM_ADMIN"])
def admin_transfer_owner(admin_id):
    """オーナー権限移譲"""
    user_id = session.get('user_id')
    tenant_id = session.get('tenant_id')
    
    db = SessionLocal()
    
    try:
        # 権限チェック（システム管理者とテナント管理者は無条件で許可）
        role = session.get('role')
        store_id = session.get('store_id')
        if role not in ['system_admin', 'tenant_admin']:
            # 店舗管理者の場合は中間テーブルから権限をチェック
            current_admin_rel = db.query(TKanrishaTenpo).filter(
                and_(TKanrishaTenpo.admin_id == user_id, TKanrishaTenpo.store_id == store_id)
            ).first()
            if not current_admin_rel or current_admin_rel.is_owner != 1:
                flash('オーナー権限を移譲する権限がありません', 'error')
                return redirect(url_for('admin.admins'))
        
        # 自分自身への移譲を防止
        if admin_id == user_id:
            flash('自分自身にオーナー権限を移譲することはできません', 'error')
            return redirect(url_for('admin.admins'))
        
        # 移譲先の管理者が同じテナントか確認
        target_admin = db.query(TKanrisha).filter(
            and_(
                TKanrisha.id == admin_id,
                TKanrisha.tenant_id == tenant_id,
                TKanrisha.role == ROLES["ADMIN"]
            )
        ).first()
        
        if not target_admin:
            flash('管理者が見つかりません', 'error')
        else:
            # 現在の店舗のオーナー権限を解除（中間テーブル）
            current_owner_rel = db.query(TKanrishaTenpo).filter(
                and_(
                    TKanrishaTenpo.store_id == store_id,
                    TKanrishaTenpo.is_owner == 1
                )
            ).first()
            
            if current_owner_rel:
                current_owner_rel.is_owner = 0
            
            # 新しいオーナーに権限を付与（中間テーブル）
            target_admin_rel = db.query(TKanrishaTenpo).filter(
                and_(
                    TKanrishaTenpo.admin_id == admin_id,
                    TKanrishaTenpo.store_id == store_id
                )
            ).first()
            
            if target_admin_rel:
                target_admin_rel.is_owner = 1
                db.commit()
                flash(f'{target_admin.name} にオーナー権限を移譲しました', 'success')
            else:
                flash('管理者がこの店舗に所属していません', 'error')
        
        return redirect(url_for('admin.admins'))
    finally:
        db.close()
