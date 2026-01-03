# 物件編集ページのタブ機能設計仕様

## 📋 概要

物件編集ページに**建物本体**、**建物付属設備**、**構築物**の3つのタブを追加し、各資産区分を別々に登録・管理できるようにします。

---

## 🎯 目的

- 各資産区分を明確に分けて管理
- 減価償却計算の精度向上
- ユーザビリティの向上

---

## 📊 データベーススキーマ

### T_物件テーブルに追加するフィールド

#### 建物付属設備（6フィールド）

| フィールド名 | データ型 | NULL | デフォルト値 | 説明 |
|-------------|---------|------|-------------|------|
| 付属設備_取得価額 | NUMERIC(15, 2) | NULL | - | 建物付属設備の取得価額 |
| 付属設備_取得年月日 | DATE | NULL | - | 建物付属設備の取得年月日 |
| 付属設備_耐用年数 | INTEGER | NULL | 15 | 建物付属設備の耐用年数 |
| 付属設備_償却方法 | VARCHAR(20) | NULL | '定額法' | 建物付属設備の償却方法 |
| 付属設備_残存価額 | NUMERIC(15, 2) | NULL | 0 | 建物付属設備の残存価額 |
| 付属設備_備考 | TEXT | NULL | - | 建物付属設備の備考 |

#### 構築物（6フィールド）

| フィールド名 | データ型 | NULL | デフォルト値 | 説明 |
|-------------|---------|------|-------------|------|
| 構築物_取得価額 | NUMERIC(15, 2) | NULL | - | 構築物の取得価額 |
| 構築物_取得年月日 | DATE | NULL | - | 構築物の取得年月日 |
| 構築物_耐用年数 | INTEGER | NULL | 15 | 構築物の耐用年数 |
| 構築物_償却方法 | VARCHAR(20) | NULL | '定額法' | 構築物の償却方法 |
| 構築物_残存価額 | NUMERIC(15, 2) | NULL | 0 | 構築物の残存価額 |
| 構築物_備考 | TEXT | NULL | - | 構築物の備考 |

**合計**: 12フィールド

---

## 🎨 UI設計

### タブ構成

```
┌─────────────────────────────────────────────┐
│ [建物本体] [建物付属設備] [構築物]           │
├─────────────────────────────────────────────┤
│                                             │
│  （各タブの内容）                            │
│                                             │
└─────────────────────────────────────────────┘
```

### 1. 建物本体タブ

**表示内容**:
- 基本情報（物件名、物件種別、住所など）
- 建物情報（建築年月、構造、階数、延床面積など）
- 減価償却情報（取得価額、取得年月日、耐用年数、償却方法、残存価額）

### 2. 建物付属設備タブ

**表示内容**:
- 取得価額
- 取得年月日
- 耐用年数（デフォルト: 15年）
- 償却方法（定額法/定率法）
- 残存価額
- 備考

**説明テキスト**:
「電気設備、給排水設備、冷暖房設備、昇降機設備などの建物付属設備を登録します。法定耐用年数は15年です。」

### 3. 構築物タブ

**表示内容**:
- 取得価額
- 取得年月日
- 耐用年数（デフォルト: 15年）
- 償却方法（定額法/定率法）
- 残存価額
- 備考

**説明テキスト**:
「アスファルト舗装、コンクリート舗装、門・塀、フェンスなどの構築物を登録します。法定耐用年数は種類により10〜20年です。」

---

## 🔧 実装方法

### Bootstrap 5のタブ機能を使用

```html
<ul class="nav nav-tabs" id="propertyTabs" role="tablist">
  <li class="nav-item" role="presentation">
    <button class="nav-link active" id="building-tab" data-bs-toggle="tab" data-bs-target="#building" type="button" role="tab">
      建物本体
    </button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="equipment-tab" data-bs-toggle="tab" data-bs-target="#equipment" type="button" role="tab">
      建物付属設備
    </button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="structure-tab" data-bs-toggle="tab" data-bs-target="#structure" type="button" role="tab">
      構築物
    </button>
  </li>
</ul>

<div class="tab-content" id="propertyTabsContent">
  <div class="tab-pane fade show active" id="building" role="tabpanel">
    <!-- 建物本体の内容 -->
  </div>
  <div class="tab-pane fade" id="equipment" role="tabpanel">
    <!-- 建物付属設備の内容 -->
  </div>
  <div class="tab-pane fade" id="structure" role="tabpanel">
    <!-- 構築物の内容 -->
  </div>
</div>
```

---

## 📝 適用範囲

### 修正対象ページ

1. **物件登録ページ**: `/property/properties/new`
2. **物件編集ページ**: `/property/properties/{id}/edit`

### 修正対象ファイル

1. `app/models_property.py`: TBukkenモデルに12フィールド追加
2. `app/templates/property_property_new.html`: タブUIを実装
3. `app/templates/property_property_edit.html`: タブUIを実装
4. `app/blueprints/property.py`: ビュー関数を修正

---

## ✅ 期待される効果

### ユーザーメリット

- ✅ **明確な資産区分**: 建物本体、付属設備、構築物を明確に分けて管理
- ✅ **減価償却の精度向上**: 各資産区分ごとに正確な減価償却費を計算
- ✅ **使いやすいUI**: タブで情報を整理し、見やすく入力しやすい

### システムメリット

- ✅ **データの正確性**: 各資産区分のデータを正確に保存
- ✅ **拡張性**: 今後、新しい資産区分を追加しやすい
- ✅ **自動マイグレーション**: 新しいフィールドは起動時に自動作成

---

## 🎯 実装スケジュール

1. **データベーススキーマの設計**: 完了
2. **モデルにフィールドを追加**: 10分
3. **タブUIを実装**: 30分
4. **テストとデプロイ**: 10分

**合計**: 約50分
