# 不動産管理アプリ設計書

**作成日**: 2026年1月3日  
**バージョン**: 1.0

---

## 1. 概要

不動産管理アプリは、テナント単位で不動産物件の管理、賃貸契約、入居者管理、家賃収支、減価償却を一元管理するアプリケーションです。

### 1.1. スコープ

- **アプリケーション名**: `property`
- **表示名**: 不動産管理
- **スコープ**: `tenant`（テナント単位で管理）
- **アイコン**: `fas fa-building`
- **カラー**: `bg-primary`

---

## 2. データベース設計

### 2.1. T_物件（Property）

| カラム名           | 型          | 説明                                   |
| ------------------ | ----------- | -------------------------------------- |
| id                 | Integer     | プライマリキー                         |
| tenant_id          | Integer     | テナントID（外部キー）                 |
| 物件名             | String(255) | 物件の名称                             |
| 物件種別           | String(50)  | マンション、アパート、戸建て等         |
| 郵便番号           | String(10)  | 物件の郵便番号                         |
| 住所               | String(500) | 物件の住所                             |
| 建築年月           | Date        | 建築年月                               |
| 延床面積           | Decimal     | 延床面積（㎡）                         |
| 構造               | String(50)  | 木造、鉄骨造、RC造等                   |
| 階数               | Integer     | 建物の階数                             |
| 部屋数             | Integer     | 総部屋数                               |
| 取得価額           | Decimal     | 物件の取得価額（円）                   |
| 取得年月日         | Date        | 物件の取得年月日                       |
| 耐用年数           | Integer     | 減価償却の耐用年数（年）               |
| 償却方法           | String(20)  | 定額法、定率法                         |
| 残存価額           | Decimal     | 残存価額（円）                         |
| 備考               | Text        | その他メモ                             |
| 有効               | Integer     | 有効フラグ（1=有効、0=無効）           |
| created_at         | DateTime    | 作成日時                               |
| updated_at         | DateTime    | 更新日時                               |

### 2.2. T_部屋（Room）

| カラム名           | 型          | 説明                                   |
| ------------------ | ----------- | -------------------------------------- |
| id                 | Integer     | プライマリキー                         |
| property_id        | Integer     | 物件ID（外部キー）                     |
| 部屋番号           | String(50)  | 部屋番号（例: 101、202）               |
| 間取り             | String(50)  | 1K、2LDK等                             |
| 専有面積           | Decimal     | 専有面積（㎡）                         |
| 賃料               | Decimal     | 月額賃料（円）                         |
| 管理費             | Decimal     | 月額管理費（円）                       |
| 敷金               | Decimal     | 敷金（円）                             |
| 礼金               | Decimal     | 礼金（円）                             |
| 入居状況           | String(20)  | 空室、入居中、退去予定                 |
| 備考               | Text        | その他メモ                             |
| 有効               | Integer     | 有効フラグ（1=有効、0=無効）           |
| created_at         | DateTime    | 作成日時                               |
| updated_at         | DateTime    | 更新日時                               |

### 2.3. T_入居者（Tenant）

| カラム名           | 型          | 説明                                   |
| ------------------ | ----------- | -------------------------------------- |
| id                 | Integer     | プライマリキー                         |
| tenant_id          | Integer     | テナントID（外部キー）                 |
| 氏名               | String(255) | 入居者の氏名                           |
| フリガナ           | String(255) | 入居者のフリガナ                       |
| 生年月日           | Date        | 生年月日                               |
| 電話番号           | String(20)  | 電話番号                               |
| メールアドレス     | String(255) | メールアドレス                         |
| 緊急連絡先名       | String(255) | 緊急連絡先の氏名                       |
| 緊急連絡先電話番号 | String(20)  | 緊急連絡先の電話番号                   |
| 備考               | Text        | その他メモ                             |
| 有効               | Integer     | 有効フラグ（1=有効、0=無効）           |
| created_at         | DateTime    | 作成日時                               |
| updated_at         | DateTime    | 更新日時                               |

### 2.4. T_契約（Contract）

| カラム名           | 型          | 説明                                   |
| ------------------ | ----------- | -------------------------------------- |
| id                 | Integer     | プライマリキー                         |
| room_id            | Integer     | 部屋ID（外部キー）                     |
| tenant_person_id   | Integer     | 入居者ID（外部キー）                   |
| 契約開始日         | Date        | 契約開始日                             |
| 契約終了日         | Date        | 契約終了日                             |
| 月額賃料           | Decimal     | 月額賃料（円）                         |
| 月額管理費         | Decimal     | 月額管理費（円）                       |
| 敷金               | Decimal     | 敷金（円）                             |
| 礼金               | Decimal     | 礼金（円）                             |
| 契約状況           | String(20)  | 契約中、契約終了、解約予定             |
| 備考               | Text        | その他メモ                             |
| created_at         | DateTime    | 作成日時                               |
| updated_at         | DateTime    | 更新日時                               |

### 2.5. T_家賃収支（RentPayment）

| カラム名           | 型          | 説明                                   |
| ------------------ | ----------- | -------------------------------------- |
| id                 | Integer     | プライマリキー                         |
| contract_id        | Integer     | 契約ID（外部キー）                     |
| 対象年月           | String(7)   | 対象年月（YYYY-MM形式）                |
| 賃料               | Decimal     | 賃料（円）                             |
| 管理費             | Decimal     | 管理費（円）                           |
| 入金日             | Date        | 入金日                                 |
| 入金状況           | String(20)  | 未入金、入金済み、延滞                 |
| 備考               | Text        | その他メモ                             |
| created_at         | DateTime    | 作成日時                               |
| updated_at         | DateTime    | 更新日時                               |

### 2.6. T_減価償却（Depreciation）

| カラム名           | 型          | 説明                                   |
| ------------------ | ----------- | -------------------------------------- |
| id                 | Integer     | プライマリキー                         |
| property_id        | Integer     | 物件ID（外部キー）                     |
| 年度               | Integer     | 対象年度（YYYY形式）                   |
| 期首帳簿価額       | Decimal     | 期首帳簿価額（円）                     |
| 償却額             | Decimal     | 当期償却額（円）                       |
| 期末帳簿価額       | Decimal     | 期末帳簿価額（円）                     |
| 備考               | Text        | その他メモ                             |
| created_at         | DateTime    | 作成日時                               |
| updated_at         | DateTime    | 更新日時                               |

---

## 3. 機能設計

### 3.1. 物件管理

- **物件一覧**: テナントに紐づく全物件を表示
- **物件詳細**: 物件の詳細情報と部屋一覧を表示
- **物件登録**: 新規物件を登録
- **物件編集**: 既存物件の情報を編集
- **物件削除**: 物件を削除（論理削除）

### 3.2. 部屋管理

- **部屋一覧**: 物件に紐づく全部屋を表示
- **部屋詳細**: 部屋の詳細情報と契約履歴を表示
- **部屋登録**: 新規部屋を登録
- **部屋編集**: 既存部屋の情報を編集
- **部屋削除**: 部屋を削除（論理削除）

### 3.3. 入居者管理

- **入居者一覧**: テナントに紐づく全入居者を表示
- **入居者詳細**: 入居者の詳細情報と契約履歴を表示
- **入居者登録**: 新規入居者を登録
- **入居者編集**: 既存入居者の情報を編集
- **入居者削除**: 入居者を削除（論理削除）

### 3.4. 契約管理

- **契約一覧**: 全契約を表示（契約中、契約終了）
- **契約詳細**: 契約の詳細情報を表示
- **契約登録**: 新規契約を登録
- **契約編集**: 既存契約の情報を編集
- **契約終了**: 契約を終了

### 3.5. 家賃収支管理

- **家賃収支一覧**: 月別の家賃収支を表示
- **家賃収支登録**: 家賃の入金情報を登録
- **家賃収支編集**: 入金情報を編集
- **延滞管理**: 延滞している家賃を一覧表示

### 3.6. 減価償却管理

- **減価償却一覧**: 物件別の減価償却状況を表示
- **減価償却計算**: 年度ごとの減価償却額を自動計算
- **減価償却詳細**: 物件の減価償却履歴を表示

---

## 4. ルーティング設計

### 4.1. 基本ルート

- `/property/` - 不動産管理トップページ（ダッシュボード）

### 4.2. 物件管理

- `/property/properties` - 物件一覧
- `/property/properties/new` - 物件登録
- `/property/properties/<id>` - 物件詳細
- `/property/properties/<id>/edit` - 物件編集
- `/property/properties/<id>/delete` - 物件削除

### 4.3. 部屋管理

- `/property/properties/<property_id>/rooms` - 部屋一覧
- `/property/properties/<property_id>/rooms/new` - 部屋登録
- `/property/rooms/<id>` - 部屋詳細
- `/property/rooms/<id>/edit` - 部屋編集
- `/property/rooms/<id>/delete` - 部屋削除

### 4.4. 入居者管理

- `/property/tenants` - 入居者一覧
- `/property/tenants/new` - 入居者登録
- `/property/tenants/<id>` - 入居者詳細
- `/property/tenants/<id>/edit` - 入居者編集
- `/property/tenants/<id>/delete` - 入居者削除

### 4.5. 契約管理

- `/property/contracts` - 契約一覧
- `/property/contracts/new` - 契約登録
- `/property/contracts/<id>` - 契約詳細
- `/property/contracts/<id>/edit` - 契約編集
- `/property/contracts/<id>/terminate` - 契約終了

### 4.6. 家賃収支管理

- `/property/rent-payments` - 家賃収支一覧
- `/property/rent-payments/new` - 家賃収支登録
- `/property/rent-payments/<id>/edit` - 家賃収支編集

### 4.7. 減価償却管理

- `/property/depreciation` - 減価償却一覧
- `/property/depreciation/<property_id>` - 物件別減価償却詳細
- `/property/depreciation/<property_id>/calculate` - 減価償却計算

---

## 5. アクセス制御

- **デコレータ**: `@require_app_enabled('property')`
- **ロール制限**: テナント管理者のみアクセス可能
- **テナント分離**: ログインユーザーのテナントIDに紐づくデータのみ表示

---

## 6. AVAILABLE_APPSへの登録

```python
{
    'name': 'property',
    'display_name': '不動産管理',
    'description': '不動産物件、契約、入居者、家賃収支、減価償却を管理します。',
    'scope': 'tenant',
    'url': 'property.index',
    'icon': 'fas fa-building',
    'color': 'bg-primary'
}
```

---

## 7. 環境変数

`.env` ファイルに以下を追加:

```env
LICENSED_APPS=property
```

---

## 8. まとめ

本設計書に基づき、不動産管理アプリを実装します。テナント単位で物件、部屋、入居者、契約、家賃収支、減価償却を一元管理できるシステムを構築します。
