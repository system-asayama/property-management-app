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

