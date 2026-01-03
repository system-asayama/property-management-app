# 経費管理機能 設計仕様書

**作成日**: 2026年1月3日  
**バージョン**: 1.0

---

## 1. 概要

不動産管理アプリケーションに経費入力・管理機能を追加します。物件単位の経費と部屋単位の経費を分けて登録・管理できるようにします。

---

## 2. 要件定義

### 2.1 機能要件

#### 物件単位の経費
物件全体に関わる経費を登録・管理します。

**経費の種類**:
- 固定資産税
- 損害保険料
- 管理費（管理会社への委託費）
- 修繕費（共用部分）
- 水道光熱費（共用部分）
- その他経費

**登録項目**:
- 経費名（例: 固定資産税）
- 経費カテゴリ（税金、保険、管理費、修繕費、水道光熱費、その他）
- 金額（円）
- 発生日
- 支払日
- 支払方法（現金、銀行振込、クレジットカード、口座引落）
- 備考

#### 部屋単位の経費
個別の部屋に関わる経費を登録・管理します。

**経費の種類**:
- 原状回復費
- クリーニング費
- 仲介手数料
- 広告宣伝費
- 修繕費（専有部分）
- 水道光熱費（専有部分）
- その他経費

**登録項目**:
- 経費名（例: 原状回復費）
- 経費カテゴリ（原状回復、クリーニング、仲介手数料、広告宣伝、修繕費、水道光熱費、その他）
- 金額（円）
- 発生日
- 支払日
- 支払方法（現金、銀行振込、クレジットカード、口座引落）
- 備考

### 2.2 非機能要件

- 経費データは物件・部屋に紐づけて管理
- 経費の登録・編集・削除が可能
- 経費の一覧表示（物件別、部屋別、期間別）
- 経費の合計金額を自動計算
- 経費データをCSVエクスポート可能

---

## 3. データベース設計

### 3.1 テーブル構成

#### T_物件経費（T_BukkenKeihi）

物件単位の経費を管理するテーブル。

| カラム名 | データ型 | NULL制約 | デフォルト値 | 説明 |
|----------|----------|----------|--------------|------|
| 物件経費id | INTEGER | NOT NULL | AUTO_INCREMENT | 主キー |
| 物件id | INTEGER | NOT NULL | - | 外部キー（T_物件） |
| 経費名 | VARCHAR(100) | NOT NULL | - | 経費の名称 |
| 経費カテゴリ | VARCHAR(50) | NOT NULL | - | 税金、保険、管理費、修繕費、水道光熱費、その他 |
| 金額 | NUMERIC(15, 2) | NOT NULL | - | 経費金額（円） |
| 発生日 | DATE | NOT NULL | - | 経費が発生した日 |
| 支払日 | DATE | NULL | - | 実際に支払った日 |
| 支払方法 | VARCHAR(50) | NULL | - | 現金、銀行振込、クレジットカード、口座引落 |
| 備考 | TEXT | NULL | - | 自由記述 |
| 作成日時 | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | レコード作成日時 |
| 更新日時 | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | レコード更新日時 |

**インデックス**:
- PRIMARY KEY (物件経費id)
- FOREIGN KEY (物件id) REFERENCES T_物件(物件id)
- INDEX (発生日)
- INDEX (経費カテゴリ)

#### T_部屋経費（T_HeyaKeihi）

部屋単位の経費を管理するテーブル。

| カラム名 | データ型 | NULL制約 | デフォルト値 | 説明 |
|----------|----------|----------|--------------|------|
| 部屋経費id | INTEGER | NOT NULL | AUTO_INCREMENT | 主キー |
| 部屋id | INTEGER | NOT NULL | - | 外部キー（T_部屋） |
| 経費名 | VARCHAR(100) | NOT NULL | - | 経費の名称 |
| 経費カテゴリ | VARCHAR(50) | NOT NULL | - | 原状回復、クリーニング、仲介手数料、広告宣伝、修繕費、水道光熱費、その他 |
| 金額 | NUMERIC(15, 2) | NOT NULL | - | 経費金額（円） |
| 発生日 | DATE | NOT NULL | - | 経費が発生した日 |
| 支払日 | DATE | NULL | - | 実際に支払った日 |
| 支払方法 | VARCHAR(50) | NULL | - | 現金、銀行振込、クレジットカード、口座引落 |
| 備考 | TEXT | NULL | - | 自由記述 |
| 作成日時 | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | レコード作成日時 |
| 更新日時 | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | レコード更新日時 |

**インデックス**:
- PRIMARY KEY (部屋経費id)
- FOREIGN KEY (部屋id) REFERENCES T_部屋(部屋id)
- INDEX (発生日)
- INDEX (経費カテゴリ)

---

## 4. 画面設計

### 4.1 物件経費一覧画面

**URL**: `/property/<物件id>/expenses`

**表示内容**:
- 物件情報（物件名、住所）
- 経費一覧テーブル（経費名、カテゴリ、金額、発生日、支払日、支払方法）
- 合計金額
- 「新規経費登録」ボタン
- 各行に「編集」「削除」ボタン

**フィルタ機能**:
- 期間指定（開始日〜終了日）
- カテゴリ絞り込み
- 支払状況（未払い、支払済み）

### 4.2 物件経費登録・編集画面

**URL**: 
- 新規登録: `/property/<物件id>/expenses/new`
- 編集: `/property/<物件id>/expenses/<経費id>/edit`

**入力項目**:
- 経費名（テキスト、必須）
- 経費カテゴリ（セレクトボックス、必須）
- 金額（数値、必須）
- 発生日（日付、必須）
- 支払日（日付、任意）
- 支払方法（セレクトボックス、任意）
- 備考（テキストエリア、任意）

**ボタン**:
- 「登録」または「更新」
- 「キャンセル」

### 4.3 部屋経費一覧画面

**URL**: `/room/<部屋id>/expenses`

**表示内容**:
- 部屋情報（物件名、部屋番号）
- 経費一覧テーブル（経費名、カテゴリ、金額、発生日、支払日、支払方法）
- 合計金額
- 「新規経費登録」ボタン
- 各行に「編集」「削除」ボタン

**フィルタ機能**:
- 期間指定（開始日〜終了日）
- カテゴリ絞り込み
- 支払状況（未払い、支払済み）

### 4.4 部屋経費登録・編集画面

**URL**: 
- 新規登録: `/room/<部屋id>/expenses/new`
- 編集: `/room/<部屋id>/expenses/<経費id>/edit`

**入力項目**:
- 経費名（テキスト、必須）
- 経費カテゴリ（セレクトボックス、必須）
- 金額（数値、必須）
- 発生日（日付、必須）
- 支払日（日付、任意）
- 支払方法（セレクトボックス、任意）
- 備考（テキストエリア、任意）

**ボタン**:
- 「登録」または「更新」
- 「キャンセル」

---

## 5. ルーティング設計

### 5.1 物件経費

| メソッド | URL | アクション | 説明 |
|---------|-----|-----------|------|
| GET | /property/<物件id>/expenses | expense_list_property | 物件経費一覧 |
| GET | /property/<物件id>/expenses/new | expense_new_property | 物件経費登録フォーム |
| POST | /property/<物件id>/expenses/new | expense_create_property | 物件経費登録処理 |
| GET | /property/<物件id>/expenses/<経費id>/edit | expense_edit_property | 物件経費編集フォーム |
| POST | /property/<物件id>/expenses/<経費id>/edit | expense_update_property | 物件経費更新処理 |
| POST | /property/<物件id>/expenses/<経費id>/delete | expense_delete_property | 物件経費削除処理 |

### 5.2 部屋経費

| メソッド | URL | アクション | 説明 |
|---------|-----|-----------|------|
| GET | /room/<部屋id>/expenses | expense_list_room | 部屋経費一覧 |
| GET | /room/<部屋id>/expenses/new | expense_new_room | 部屋経費登録フォーム |
| POST | /room/<部屋id>/expenses/new | expense_create_room | 部屋経費登録処理 |
| GET | /room/<部屋id>/expenses/<経費id>/edit | expense_edit_room | 部屋経費編集フォーム |
| POST | /room/<部屋id>/expenses/<経費id>/edit | expense_update_room | 部屋経費更新処理 |
| POST | /room/<部屋id>/expenses/<経費id>/delete | expense_delete_room | 部屋経費削除処理 |

---

## 6. 実装ファイル

### 6.1 モデル定義

**ファイル**: `app/models_property.py`

- `TBukkenKeihi`クラスを追加
- `THeyaKeihi`クラスを追加

### 6.2 ビュー関数

**ファイル**: `app/blueprints/property.py`

物件経費関連のビュー関数を追加:
- `expense_list_property()`
- `expense_new_property()`
- `expense_create_property()`
- `expense_edit_property()`
- `expense_update_property()`
- `expense_delete_property()`

**ファイル**: `app/blueprints/room.py`（新規作成）

部屋経費関連のビュー関数を追加:
- `expense_list_room()`
- `expense_new_room()`
- `expense_create_room()`
- `expense_edit_room()`
- `expense_update_room()`
- `expense_delete_room()`

### 6.3 HTMLテンプレート

**物件経費**:
- `app/templates/property_expense_list.html`
- `app/templates/property_expense_form.html`

**部屋経費**:
- `app/templates/room_expense_list.html`
- `app/templates/room_expense_form.html`

---

## 7. 経費カテゴリの定義

### 7.1 物件経費カテゴリ

```python
PROPERTY_EXPENSE_CATEGORIES = [
    '税金',
    '保険',
    '管理費',
    '修繕費',
    '水道光熱費',
    'その他'
]
```

### 7.2 部屋経費カテゴリ

```python
ROOM_EXPENSE_CATEGORIES = [
    '原状回復',
    'クリーニング',
    '仲介手数料',
    '広告宣伝',
    '修繕費',
    '水道光熱費',
    'その他'
]
```

### 7.3 支払方法

```python
PAYMENT_METHODS = [
    '現金',
    '銀行振込',
    'クレジットカード',
    '口座引落'
]
```

---

## 8. 自動マイグレーション

新しい2つのテーブル（T_物件経費、T_部屋経費）は、**自動マイグレーション機能**により、アプリケーション起動時に自動的にデータベースに作成されます。

手動でのマイグレーションスクリプト実行は不要です。

---

## 9. セキュリティ

### 9.1 認証・認可

- 経費データへのアクセスは、ログインユーザーが所有する物件・部屋に限定
- 他のユーザーの経費データは閲覧・編集不可

### 9.2 入力検証

- 金額は正の数値のみ許可
- 発生日、支払日は有効な日付形式のみ許可
- 経費カテゴリ、支払方法は定義済みの値のみ許可

---

## 10. 今後の拡張

### 10.1 経費分析機能

- 月別・年別の経費推移グラフ
- カテゴリ別の経費割合（円グラフ）
- 予算vs実績の比較

### 10.2 経費予測機能

- 過去の経費データから将来の経費を予測
- 季節性を考慮した予測

### 10.3 経費アラート機能

- 予算超過時にアラート通知
- 支払期限が近い経費を通知

---

**設計者**: Manus AI  
**最終更新**: 2026年1月3日 17:30 JST
