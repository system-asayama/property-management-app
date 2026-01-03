# 不動産管理アプリケーション 問題分析レポート

**作成日時**: 2026年1月3日  
**対象アプリ**: property-management-app-d46351d49159  
**問題発生箇所**: `/property/simulations` エンドポイント

---

## 1. 問題の概要

Heroku本番環境において、シミュレーション機能（`/property/simulations`）にアクセスすると**Internal Server Error**が発生している。この問題は、データベーススキーマとアプリケーションコードの不整合に起因している。

### 1.1 問題発生の経緯

1. **シミュレーション機能の拡張実装**（2パターン対応）
   - 物件ベースシミュレーション（既存物件データから自動計算）
   - 独立シミュレーション（手動入力、物件データに依存しない）

2. **新フィールドの追加**（`app/models_property.py`）
   - `シミュレーション種別` (VARCHAR(20), DEFAULT '物件ベース')
   - `年間家賃収入` (NUMERIC(15, 2))
   - `部屋数` (INTEGER)

3. **自動マイグレーション機能の実装試行**
   - アプリ起動時に不足カラムを自動追加する仕組みを実装
   - 実装後、エラーが発生し一時的に無効化

4. **現在の状態**
   - コードには新フィールドが定義済み
   - データベースには新フィールドが未追加
   - アプリケーションが新フィールドを参照しようとしてエラー発生

---

## 2. 根本原因の分析

### 2.1 データベーススキーマとコードの不整合

**問題**: `T_シミュレーション`テーブルのスキーマが、`app/models_property.py`の`TSimulation`クラス定義と一致していない。

#### コード側の定義（`app/models_property.py` 124-158行目）

```python
class TSimulation(Base):
    """T_シミュレーションテーブル"""
    __tablename__ = 'T_シミュレーション'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey('T_テナント.id'), nullable=False)
    名称 = Column(String(255), nullable=False)
    
    # シミュレーション種別 ← 新規追加
    シミュレーション種別 = Column(String(20), nullable=False, server_default='物件ベース')
    
    # 物件ベースシミュレーション用
    物件id = Column(Integer, ForeignKey('T_物件.id'), nullable=True)
    
    # 独立シミュレーション用 ← 新規追加
    年間家賃収入 = Column(Numeric(15, 2), nullable=True)
    部屋数 = Column(Integer, nullable=True)
    
    # ... その他のフィールド
```

#### データベース側の状態（推定）

本番環境のPostgreSQLデータベースには、以下の3つのカラムが**存在しない**と推定される：

1. `シミュレーション種別`
2. `年間家賃収入`
3. `部屋数`

**根拠**: 
- マイグレーションスクリプト（`migrate_add_simulation_type_fields.py`）が作成されているが未実行
- 自動マイグレーション機能が無効化されている
- Internal Server Errorが発生している

### 2.2 自動マイグレーション機能のエラー

**問題**: `app/__init__.py`の151-180行目でコメントアウトされている自動マイグレーション機能に、モデル名の不一致エラーがあった。

#### エラー内容

```
module 'app.models_login' has no attribute 'TSystemAdmin'
```

#### 原因分析

`app/__init__.py`の167-174行目で、存在しないクラス名を参照していた：

```python
# 誤った記述（コメントアウト済み）
migration_targets = [
    # models_login
    (models_login.TKanrisha, 'T_管理者'),      # ✓ 正しい
    (models_login.TJugyoin, 'T_従業員'),       # ✓ 正しい
    (models_login.TTenant, 'T_テナント'),      # ✓ 正しい
    (models_login.TTenpo, 'T_店舗'),           # ✓ 正しい
    (models_login.TKanrishaTenpo, 'T_管理者_店舗'),  # ✓ 正しい
    (models_login.TJugyoinTenpo, 'T_従業員_店舗'),   # ✓ 正しい
    # models_property
    (models_property.TProperty, 'T_物件'),     # ✗ 誤り（正: TBukken）
    (models_property.TRoom, 'T_部屋'),         # ✗ 誤り（正: THeya）
    (models_property.TTenant_Property, 'T_入居者'),  # ✗ 誤り（正: TNyukyosha）
    (models_property.TContract, 'T_契約'),     # ✗ 誤り（正: TKeiyaku）
    (models_property.TRentIncome, 'T_家賃収支'),    # ✗ 誤り（正: TYachinShushi）
    (models_property.TDepreciation, 'T_減価償却'),  # ✗ 誤り（正: TGenkashokaku）
    (models_property.TSimulation, 'T_シミュレーション'),  # ✓ 正しい
    (models_property.TSimulationResult, 'T_シミュレーション結果'),  # ✓ 正しい
]
```

#### 正しいクラス名（`app/models_property.py`）

```python
class TBukken(Base):           # T_物件
class THeya(Base):             # T_部屋
class TNyukyosha(Base):        # T_入居者
class TKeiyaku(Base):          # T_契約
class TYachinShushi(Base):     # T_家賃収支
class TGenkashokaku(Base):     # T_減価償却
class TSimulation(Base):       # T_シミュレーション
class TSimulationResult(Base): # T_シミュレーション結果
```

### 2.3 マイグレーションスクリプトの未実行

**問題**: `migrate_add_simulation_type_fields.py`が作成されているが、本番環境で実行されていない。

**スクリプトの内容**:
- `T_シミュレーション`テーブルに3つのカラムを追加
- PostgreSQLとSQLiteの両方に対応
- カラムの存在チェック機能あり
- トランザクション管理あり

**未実行の理由**:
- 自動マイグレーション機能の実装を優先したため、手動スクリプトの実行を保留
- 自動マイグレーション機能のエラーにより、マイグレーション自体が実行されず

---

## 3. 影響範囲

### 3.1 機能への影響

| 機能 | 影響 | 理由 |
|------|------|------|
| シミュレーション一覧表示 | ❌ エラー | `シミュレーション種別`カラムが存在しない |
| シミュレーション作成 | ❌ エラー | 新規フィールドをINSERTしようとしてエラー |
| シミュレーション編集 | ❌ エラー | 新規フィールドをUPDATEしようとしてエラー |
| シミュレーション詳細表示 | ❌ エラー | 新規フィールドをSELECTしようとしてエラー |
| その他の不動産管理機能 | ✓ 正常 | シミュレーション以外は影響なし |

### 3.2 ユーザーへの影響

- **シミュレーション機能が完全に使用不可**
- Internal Server Errorが表示され、ユーザー体験が著しく低下
- その他の不動産管理機能（物件管理、契約管理など）は正常に動作

---

## 4. 解決策の提案

### 4.1 即時対応（短期的解決策）

#### オプションA: 手動マイグレーションスクリプトの実行（推奨）

**メリット**:
- 最も確実で安全
- トランザクション管理により、失敗時のロールバックが可能
- カラム存在チェック機能により、冪等性が保証される

**手順**:
1. `migrate_add_simulation_type_fields.py`を本番環境で実行
2. 実行結果を確認
3. アプリケーションを再起動（Heroku dynoの再起動）
4. `/property/simulations`にアクセスして動作確認

**実行コマンド例**:
```bash
# Heroku環境で実行
heroku run python migrate_add_simulation_type_fields.py -a property-management-app-d46351d49159
```

#### オプションB: 自動マイグレーション機能の修正と有効化

**メリット**:
- 今後の開発で同様の問題を防げる
- 手動マイグレーションの手間が不要

**デメリット**:
- 修正とテストに時間がかかる
- 本番環境での動作確認が必要

**手順**:
1. `app/__init__.py`のモデル名を修正
2. エラーハンドリングを強化
3. ローカル環境でテスト
4. GitHubにプッシュ
5. Herokuで自動デプロイ
6. アプリ起動時に自動マイグレーションが実行される

### 4.2 中長期的対応

#### 1. 自動マイグレーション機能の完全実装

**目的**: ユーザー要求「今後のすべてのコードは自動マイグレーション対応必須」を実現

**実装内容**:
- `app/__init__.py`のモデル名を正しいクラス名に修正
- エラーハンドリングを強化（個別カラムの失敗でも続行）
- ログ出力を充実させる
- テストケースを作成

**修正後のコード例**:
```python
migration_targets = [
    # models_login
    (models_login.TKanrisha, 'T_管理者'),
    (models_login.TJugyoin, 'T_従業員'),
    (models_login.TTenant, 'T_テナント'),
    (models_login.TTenpo, 'T_店舗'),
    (models_login.TKanrishaTenpo, 'T_管理者_店舗'),
    (models_login.TJugyoinTenpo, 'T_従業員_店舗'),
    # models_property
    (models_property.TBukken, 'T_物件'),
    (models_property.THeya, 'T_部屋'),
    (models_property.TNyukyosha, 'T_入居者'),
    (models_property.TKeiyaku, 'T_契約'),
    (models_property.TYachinShushi, 'T_家賃収支'),
    (models_property.TGenkashokaku, 'T_減価償却'),
    (models_property.TSimulation, 'T_シミュレーション'),
    (models_property.TSimulationResult, 'T_シミュレーション結果'),
]
```

#### 2. マイグレーション管理の標準化

**提案**:
- すべての新機能実装時に、モデル定義と同時にマイグレーションスクリプトを作成
- 自動マイグレーション機能をデフォルトで有効化
- 手動マイグレーションスクリプトはバックアップとして保持

#### 3. テスト環境の整備

**提案**:
- ローカル開発環境でPostgreSQLを使用（SQLiteとの差異を最小化）
- CI/CDパイプラインでマイグレーションテストを自動実行
- ステージング環境で本番環境と同じ構成でテスト

---

## 5. 推奨アクション

### 5.1 即時実行（今すぐ）

**優先度: 最高**

1. **手動マイグレーションスクリプトの実行**
   ```bash
   heroku run python migrate_add_simulation_type_fields.py -a property-management-app-d46351d49159
   ```

2. **アプリケーションの再起動**
   ```bash
   heroku restart -a property-management-app-d46351d49159
   ```

3. **動作確認**
   - `/property/simulations`にアクセス
   - シミュレーション作成機能のテスト
   - 2パターン（物件ベース/独立）の動作確認

### 5.2 短期対応（今日中）

**優先度: 高**

1. **自動マイグレーション機能の修正**
   - `app/__init__.py`のモデル名を修正
   - エラーハンドリングを強化

2. **ローカル環境でテスト**
   - SQLiteで動作確認
   - PostgreSQLで動作確認（可能であれば）

3. **GitHubにプッシュ**
   - 修正内容をコミット
   - Herokuで自動デプロイ

### 5.3 中期対応（今週中）

**優先度: 中**

1. **自動マイグレーション機能の完全実装**
   - すべてのモデルに対応
   - テストケースの作成
   - ドキュメント整備

2. **マイグレーション管理の標準化**
   - 開発フローの確立
   - チェックリストの作成

---

## 6. リスク評価

### 6.1 手動マイグレーション実行のリスク

| リスク | 発生確率 | 影響度 | 対策 |
|--------|----------|--------|------|
| マイグレーション失敗 | 低 | 高 | トランザクション管理により自動ロールバック |
| データ損失 | 極低 | 極高 | ALTER TABLE ADD COLUMNは既存データに影響なし |
| ダウンタイム | 低 | 中 | マイグレーション中もアプリは稼働可能 |
| カラム重複エラー | 低 | 低 | スクリプトにカラム存在チェック機能あり |

### 6.2 自動マイグレーション有効化のリスク

| リスク | 発生確率 | 影響度 | 対策 |
|--------|----------|--------|------|
| 起動時エラー | 中 | 高 | エラーハンドリングを強化、ログ出力を充実 |
| 予期しないスキーマ変更 | 低 | 高 | ローカル環境で十分にテスト |
| パフォーマンス低下 | 低 | 低 | 起動時のみ実行、カラム追加は高速 |

---

## 7. 結論

### 7.1 問題の本質

データベーススキーマとアプリケーションコードの不整合により、シミュレーション機能が完全に使用不可となっている。この問題は、マイグレーション管理の不備に起因している。

### 7.2 推奨される解決策

**即時対応**: 手動マイグレーションスクリプト（`migrate_add_simulation_type_fields.py`）を実行し、不足カラムを追加する。

**中長期対応**: 自動マイグレーション機能を修正・有効化し、今後の開発で同様の問題を防ぐ。

### 7.3 期待される効果

- シミュレーション機能の完全復旧
- 2パターンシミュレーション機能の正常動作
- 今後の開発効率の向上
- マイグレーション管理の標準化

---

## 8. 次のステップ

1. **このレポートをユーザーに提示**
2. **ユーザーの承認を得る**
3. **手動マイグレーションスクリプトを実行**
4. **動作確認**
5. **自動マイグレーション機能の修正に着手**

---

**レポート作成者**: Manus AI  
**最終更新**: 2026年1月3日
