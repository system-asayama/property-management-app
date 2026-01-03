# 経費管理機能エラー修正レポート

**発生日時**: 2026年1月3日 22:51  
**エラー**: Internal Server Error  
**URL**: https://property-management-app-d46351d49159.herokuapp.com/property/properties/1/expenses

---

## 🔍 エラー原因の調査

### 発生したエラー

経費一覧ページにアクセスすると「Internal Server Error」が発生しました。

### 原因1: 有効カラムのチェック

**問題**: `TBukken.有効 == 1`というクエリ条件が含まれていましたが、データベースに`有効`カラムが存在しませんでした。

**影響範囲**:
- 物件経費管理の全関数（一覧、登録、編集、削除）
- 部屋経費管理の全関数（一覧、登録、編集、削除）

**修正内容**:
- すべての経費管理関数から`TBukken.有効 == 1`と`THeya.有効 == 1`のチェックを削除
- コミットID: a54486e

### 原因2: 経費テーブルが存在しない

**問題**: `T_物件経費`と`T_部屋経費`テーブルが自動マイグレーション対象に含まれていなかったため、データベースに作成されていませんでした。

**影響範囲**:
- 経費一覧ページ: SELECT文が失敗
- 経費登録ページ: INSERT文が失敗

**修正内容**:
- `app/__init__.py`の`migration_targets`リストに`TBukkenKeihi`と`THeyaKeihi`を追加
- コミットID: 6a316c8

### 原因3: 手動マイグレーションスクリプトの必要性

**問題**: 自動マイグレーション機能は既存のテーブルにカラムを追加することはできますが、**新しいテーブルを作成することはできません**。

**解決策**:
- 手動マイグレーションスクリプト`create_expense_tables.py`を作成
- コミットID: 9e8c4f7

---

## 🔧 実施した修正

### 1. 有効カラムチェックの削除（コミット a54486e）

**修正ファイル**: `app/blueprints/property.py`

**修正内容**:
```python
# 修正前
property_data = db.execute(
    select(TBukken).where(TBukken.id == property_id, TBukken.tenant_id == tenant_id, TBukken.有効 == 1)
).scalar_one_or_none()

# 修正後
property_data = db.execute(
    select(TBukken).where(TBukken.id == property_id, TBukken.tenant_id == tenant_id)
).scalar_one_or_none()
```

**修正箇所**: 14箇所（物件経費5箇所、部屋経費9箇所）

### 2. 自動マイグレーション対象への追加（コミット 6a316c8）

**修正ファイル**: `app/__init__.py`

**修正内容**:
```python
migration_targets = [
    # ... 既存のテーブル ...
    (models_property.TSimulation, 'T_シミュレーション'),
    (models_property.TSimulationResult, 'T_シミュレーション結果'),
    (models_property.TBukkenKeihi, 'T_物件経費'),  # ← 追加
    (models_property.THeyaKeihi, 'T_部屋経費'),    # ← 追加
]
```

### 3. 手動マイグレーションスクリプトの作成（コミット 9e8c4f7）

**作成ファイル**: `create_expense_tables.py`

**機能**:
- `T_物件経費`テーブルを作成
- `T_部屋経費`テーブルを作成
- 既存テーブルがある場合はスキップ（`checkfirst=True`）

**使用方法**:
```bash
# Herokuで実行
heroku run python create_expense_tables.py -a property-management-app-d46351d49159

# ローカルで実行
python create_expense_tables.py
```

---

## 📊 自動マイグレーション機能の制限

### できること

✅ 既存テーブルに新しいカラムを追加  
✅ カラムの型を自動判定  
✅ NULL制約を自動判定  
✅ デフォルト値を自動判定  
✅ PostgreSQLとSQLiteの両方に対応

### できないこと

❌ 新しいテーブルを作成  
❌ カラムを削除  
❌ カラムの型を変更  
❌ カラム名を変更  
❌ 複雑なデータ変換

### 理由

自動マイグレーション機能は、`Base.metadata.create_all()`を使用してテーブルを作成した後に実行されます。そのため、**既存のテーブルにカラムを追加することしかできません**。

新しいテーブルを作成する場合は、以下のいずれかの方法が必要です：

1. **手動マイグレーションスクリプトを実行**（推奨）
2. `Base.metadata.create_all()`を再実行（すべてのテーブルを再作成）
3. SQLを直接実行してテーブルを作成

---

## 🎯 次のステップ

### 1. 手動マイグレーションスクリプトの実行

Herokuで以下のコマンドを実行して、経費テーブルを作成してください：

```bash
heroku run python create_expense_tables.py -a property-management-app-d46351d49159
```

### 2. 動作確認

経費テーブルが作成されたら、以下のURLで動作確認を行ってください：

- 物件経費一覧: https://property-management-app-d46351d49159.herokuapp.com/property/properties/1/expenses
- 部屋経費一覧: https://property-management-app-d46351d49159.herokuapp.com/property/rooms/1/expenses

### 3. 今後の開発

今後、新しいテーブルを追加する場合は、以下の手順を実施してください：

1. `models_property.py`にモデルクラスを追加
2. `app/__init__.py`の`migration_targets`リストにモデルを追加
3. 手動マイグレーションスクリプトを作成して実行
4. 自動マイグレーション機能は、新しいカラムの追加のみに使用

---

## 📝 まとめ

### 修正内容

1. ✅ 有効カラムチェックの削除（14箇所）
2. ✅ 自動マイグレーション対象への追加（2テーブル）
3. ✅ 手動マイグレーションスクリプトの作成

### 残作業

1. ⏳ Herokuで手動マイグレーションスクリプトを実行
2. ⏳ 本番環境での動作確認

### コミット履歴

- **a54486e**: 有効カラムチェックの削除
- **6a316c8**: 自動マイグレーション対象への追加
- **9e8c4f7**: 手動マイグレーションスクリプトの作成

---

**作成者**: Manus AI  
**最終更新**: 2026年1月3日 23:00 JST  
**ステータス**: 🔧 修正完了、手動マイグレーション実行待ち
