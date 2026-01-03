#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小限のテンプレートを作成するスクリプト
"""

templates = {
    'property_room_new.html': '''{% extends "base.html" %}
{% block title %}部屋登録 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>部屋登録: {{ property.物件名 }}</h2>
    <form method="POST">
        <div class="mb-3">
            <label class="form-label">部屋番号</label>
            <input type="text" class="form-control" name="部屋番号" required>
        </div>
        <div class="mb-3">
            <label class="form-label">間取り</label>
            <input type="text" class="form-control" name="間取り">
        </div>
        <div class="mb-3">
            <label class="form-label">専有面積（㎡）</label>
            <input type="number" class="form-control" name="専有面積" step="0.01">
        </div>
        <div class="mb-3">
            <label class="form-label">賃料（円）</label>
            <input type="number" class="form-control" name="賃料">
        </div>
        <div class="mb-3">
            <label class="form-label">管理費（円）</label>
            <input type="number" class="form-control" name="管理費">
        </div>
        <button type="submit" class="btn btn-primary">登録</button>
        <a href="{{ url_for('property.property_detail', id=property.id) }}" class="btn btn-secondary">キャンセル</a>
    </form>
</div>
{% endblock %}''',

    'property_room_detail.html': '''{% extends "base.html" %}
{% block title %}部屋詳細 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>部屋詳細: {{ property.物件名 }} - {{ room.部屋番号 }}</h2>
    <div class="card">
        <div class="card-body">
            <p><strong>間取り:</strong> {{ room.間取り or '-' }}</p>
            <p><strong>専有面積:</strong> {{ room.専有面積 or '-' }}㎡</p>
            <p><strong>賃料:</strong> ¥{{ "{:,.0f}".format(room.賃料) if room.賃料 else '-' }}</p>
            <p><strong>入居状況:</strong> {{ room.入居状況 }}</p>
        </div>
    </div>
    <a href="{{ url_for('property.room_edit', id=room.id) }}" class="btn btn-warning mt-3">編集</a>
    <a href="{{ url_for('property.property_detail', id=property.id) }}" class="btn btn-secondary mt-3">戻る</a>
</div>
{% endblock %}''',

    'property_room_edit.html': '''{% extends "base.html" %}
{% block title %}部屋編集 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>部屋編集: {{ property.物件名 }} - {{ room.部屋番号 }}</h2>
    <form method="POST">
        <div class="mb-3">
            <label class="form-label">部屋番号</label>
            <input type="text" class="form-control" name="部屋番号" value="{{ room.部屋番号 }}" required>
        </div>
        <div class="mb-3">
            <label class="form-label">間取り</label>
            <input type="text" class="form-control" name="間取り" value="{{ room.間取り or '' }}">
        </div>
        <div class="mb-3">
            <label class="form-label">専有面積（㎡）</label>
            <input type="number" class="form-control" name="専有面積" value="{{ room.専有面積 or '' }}" step="0.01">
        </div>
        <div class="mb-3">
            <label class="form-label">賃料（円）</label>
            <input type="number" class="form-control" name="賃料" value="{{ room.賃料 or '' }}">
        </div>
        <div class="mb-3">
            <label class="form-label">入居状況</label>
            <select class="form-select" name="入居状況">
                <option value="空室" {% if room.入居状況 == '空室' %}selected{% endif %}>空室</option>
                <option value="入居中" {% if room.入居状況 == '入居中' %}selected{% endif %}>入居中</option>
            </select>
        </div>
        <button type="submit" class="btn btn-primary">更新</button>
        <a href="{{ url_for('property.room_detail', id=room.id) }}" class="btn btn-secondary">キャンセル</a>
    </form>
</div>
{% endblock %}''',

    'property_tenants.html': '''{% extends "base.html" %}
{% block title %}入居者一覧 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>入居者一覧</h2>
    <a href="{{ url_for('property.tenant_new') }}" class="btn btn-primary mb-3">新規登録</a>
    <table class="table table-striped">
        <thead>
            <tr><th>氏名</th><th>電話番号</th><th>操作</th></tr>
        </thead>
        <tbody>
            {% for tenant in tenants %}
            <tr>
                <td>{{ tenant.氏名 }}</td>
                <td>{{ tenant.電話番号 or '-' }}</td>
                <td><a href="{{ url_for('property.tenant_detail', id=tenant.id) }}" class="btn btn-sm btn-info">詳細</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'property_tenant_new.html': '''{% extends "base.html" %}
{% block title %}入居者登録 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>入居者登録</h2>
    <form method="POST">
        <div class="mb-3">
            <label class="form-label">氏名</label>
            <input type="text" class="form-control" name="氏名" required>
        </div>
        <div class="mb-3">
            <label class="form-label">電話番号</label>
            <input type="text" class="form-control" name="電話番号">
        </div>
        <div class="mb-3">
            <label class="form-label">メールアドレス</label>
            <input type="email" class="form-control" name="メールアドレス">
        </div>
        <button type="submit" class="btn btn-primary">登録</button>
        <a href="{{ url_for('property.tenants') }}" class="btn btn-secondary">キャンセル</a>
    </form>
</div>
{% endblock %}''',

    'property_tenant_detail.html': '''{% extends "base.html" %}
{% block title %}入居者詳細 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>入居者詳細: {{ tenant.氏名 }}</h2>
    <div class="card">
        <div class="card-body">
            <p><strong>電話番号:</strong> {{ tenant.電話番号 or '-' }}</p>
            <p><strong>メールアドレス:</strong> {{ tenant.メールアドレス or '-' }}</p>
        </div>
    </div>
    <a href="{{ url_for('property.tenant_edit', id=tenant.id) }}" class="btn btn-warning mt-3">編集</a>
    <a href="{{ url_for('property.tenants') }}" class="btn btn-secondary mt-3">戻る</a>
</div>
{% endblock %}''',

    'property_tenant_edit.html': '''{% extends "base.html" %}
{% block title %}入居者編集 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>入居者編集: {{ tenant.氏名 }}</h2>
    <form method="POST">
        <div class="mb-3">
            <label class="form-label">氏名</label>
            <input type="text" class="form-control" name="氏名" value="{{ tenant.氏名 }}" required>
        </div>
        <div class="mb-3">
            <label class="form-label">電話番号</label>
            <input type="text" class="form-control" name="電話番号" value="{{ tenant.電話番号 or '' }}">
        </div>
        <button type="submit" class="btn btn-primary">更新</button>
        <a href="{{ url_for('property.tenant_detail', id=tenant.id) }}" class="btn btn-secondary">キャンセル</a>
    </form>
</div>
{% endblock %}''',

    'property_contracts.html': '''{% extends "base.html" %}
{% block title %}契約一覧 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>契約一覧</h2>
    <a href="{{ url_for('property.contract_new') }}" class="btn btn-primary mb-3">新規契約</a>
    <table class="table table-striped">
        <thead>
            <tr><th>物件</th><th>部屋</th><th>入居者</th><th>契約状況</th><th>操作</th></tr>
        </thead>
        <tbody>
            {% for item in contracts %}
            <tr>
                <td>{{ item.property.物件名 }}</td>
                <td>{{ item.room.部屋番号 }}</td>
                <td>{{ item.tenant_person.氏名 if item.tenant_person else '-' }}</td>
                <td>{{ item.contract.契約状況 }}</td>
                <td><a href="{{ url_for('property.contract_detail', id=item.contract.id) }}" class="btn btn-sm btn-info">詳細</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'property_contract_new.html': '''{% extends "base.html" %}
{% block title %}契約登録 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>契約登録</h2>
    <form method="POST">
        <div class="mb-3">
            <label class="form-label">部屋</label>
            <select class="form-select" name="room_id" required>
                {% for item in vacant_rooms %}
                <option value="{{ item.room.id }}">{{ item.property.物件名 }} - {{ item.room.部屋番号 }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="mb-3">
            <label class="form-label">入居者</label>
            <select class="form-select" name="tenant_person_id" required>
                {% for tenant in tenants %}
                <option value="{{ tenant.id }}">{{ tenant.氏名 }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="mb-3">
            <label class="form-label">契約開始日</label>
            <input type="date" class="form-control" name="契約開始日" required>
        </div>
        <div class="mb-3">
            <label class="form-label">月額賃料</label>
            <input type="number" class="form-control" name="月額賃料" required>
        </div>
        <button type="submit" class="btn btn-primary">登録</button>
        <a href="{{ url_for('property.contracts') }}" class="btn btn-secondary">キャンセル</a>
    </form>
</div>
{% endblock %}''',

    'property_contract_detail.html': '''{% extends "base.html" %}
{% block title %}契約詳細 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>契約詳細</h2>
    <div class="card">
        <div class="card-body">
            <p><strong>物件:</strong> {{ property.物件名 }}</p>
            <p><strong>部屋:</strong> {{ room.部屋番号 }}</p>
            <p><strong>入居者:</strong> {{ tenant_person.氏名 if tenant_person else '-' }}</p>
            <p><strong>契約開始日:</strong> {{ contract.契約開始日.strftime('%Y年%m月%d日') if contract.契約開始日 else '-' }}</p>
            <p><strong>月額賃料:</strong> ¥{{ "{:,.0f}".format(contract.月額賃料) if contract.月額賃料 else '-' }}</p>
            <p><strong>契約状況:</strong> {{ contract.契約状況 }}</p>
        </div>
    </div>
    <a href="{{ url_for('property.contract_edit', id=contract.id) }}" class="btn btn-warning mt-3">編集</a>
    {% if contract.契約状況 == '契約中' %}
    <form method="POST" action="{{ url_for('property.contract_terminate', id=contract.id) }}" style="display:inline;">
        <button type="submit" class="btn btn-danger mt-3" onclick="return confirm('契約を終了しますか？');">契約終了</button>
    </form>
    {% endif %}
    <a href="{{ url_for('property.contracts') }}" class="btn btn-secondary mt-3">戻る</a>
</div>
{% endblock %}''',

    'property_contract_edit.html': '''{% extends "base.html" %}
{% block title %}契約編集 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>契約編集</h2>
    <form method="POST">
        <div class="mb-3">
            <label class="form-label">契約開始日</label>
            <input type="date" class="form-control" name="契約開始日" value="{{ contract.契約開始日.strftime('%Y-%m-%d') if contract.契約開始日 else '' }}" required>
        </div>
        <div class="mb-3">
            <label class="form-label">月額賃料</label>
            <input type="number" class="form-control" name="月額賃料" value="{{ contract.月額賃料 or '' }}" required>
        </div>
        <button type="submit" class="btn btn-primary">更新</button>
        <a href="{{ url_for('property.contract_detail', id=contract.id) }}" class="btn btn-secondary">キャンセル</a>
    </form>
</div>
{% endblock %}''',

    'property_depreciation.html': '''{% extends "base.html" %}
{% block title %}減価償却一覧 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>減価償却一覧</h2>
    <table class="table table-striped">
        <thead>
            <tr><th>物件名</th><th>取得価額</th><th>耐用年数</th><th>償却方法</th><th>操作</th></tr>
        </thead>
        <tbody>
            {% for item in depreciation_list %}
            <tr>
                <td>{{ item.property.物件名 }}</td>
                <td>¥{{ "{:,.0f}".format(item.property.取得価額) if item.property.取得価額 else '-' }}</td>
                <td>{{ item.property.耐用年数 or '-' }}年</td>
                <td>{{ item.property.償却方法 or '-' }}</td>
                <td><a href="{{ url_for('property.depreciation_detail', property_id=item.property.id) }}" class="btn btn-sm btn-info">詳細</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'property_depreciation_detail.html': '''{% extends "base.html" %}
{% block title %}減価償却詳細 - 不動産管理{% endblock %}
{% block content %}
<div class="container mt-4">
    <h2>減価償却詳細: {{ property.物件名 }}</h2>
    <div class="card mb-4">
        <div class="card-body">
            <p><strong>取得価額:</strong> ¥{{ "{:,.0f}".format(property.取得価額) if property.取得価額 else '-' }}</p>
            <p><strong>耐用年数:</strong> {{ property.耐用年数 or '-' }}年</p>
            <p><strong>償却方法:</strong> {{ property.償却方法 or '-' }}</p>
        </div>
    </div>
    <form method="POST" action="{{ url_for('property.depreciation_calculate', property_id=property.id) }}">
        <div class="mb-3">
            <label class="form-label">対象年度</label>
            <input type="number" class="form-control" name="target_year" value="{{ current_year }}" required>
        </div>
        <button type="submit" class="btn btn-primary">減価償却を計算</button>
    </form>
    <h4 class="mt-4">償却履歴</h4>
    <table class="table table-striped">
        <thead>
            <tr><th>年度</th><th>期首帳簿価額</th><th>償却額</th><th>期末帳簿価額</th></tr>
        </thead>
        <tbody>
            {% for dep in depreciation_history %}
            <tr>
                <td>{{ dep.年度 }}</td>
                <td>¥{{ "{:,.0f}".format(dep.期首帳簿価額) if dep.期首帳簿価額 else '-' }}</td>
                <td>¥{{ "{:,.0f}".format(dep.償却額) if dep.償却額 else '-' }}</td>
                <td>¥{{ "{:,.0f}".format(dep.期末帳簿価額) if dep.期末帳簿価額 else '-' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}'''
}

import os

template_dir = 'app/templates'
for filename, content in templates.items():
    filepath = os.path.join(template_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ {filename} 作成完了")

print(f"\n✅ 全{len(templates)}個のテンプレート作成完了")
