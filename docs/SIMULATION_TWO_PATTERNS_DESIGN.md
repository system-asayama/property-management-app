# シミュレーション機能 2パターン設計

**作成日**: 2026年1月3日  
**目的**: 物件ベースシミュレーションと独立シミュレーションの2パターンを実装

---

## 📋 概要

シミュレーション機能を以下の2パターンに分けて実装します。

### パターン1: 物件ベースシミュレーション
- **目的**: 既存の物件データに基づいた実績ベースのシミュレーション
- **特徴**: 物件の実データを自動取得し、現実的な予測を行う
- **用途**: 既存物件の収支予測、投資判断

### パターン2: 独立シミュレーション
- **目的**: 物件データに依存しない仮想的なシミュレーション
- **特徴**: すべての項目を手動入力し、自由なシナリオ分析が可能
- **用途**: 購入検討中の物件の試算、複数シナリオの比較

---

## 🎯 実装方針

### データベース設計

#### TSimulationモデルに追加するフィールド

```python
シミュレーション種別 = Column(String(20), nullable=False, default='物件ベース')
# '物件ベース' または '独立'

# 独立シミュレーション用の追加フィールド
年間家賃収入 = Column(Numeric(15, 2), nullable=True)  # 独立シミュレーション用
部屋数 = Column(Integer, nullable=True)  # 独立シミュレーション用
```

### 計算ロジックの分岐

#### 物件ベースシミュレーション
1. **家賃収入**: 物件の部屋データから自動計算
2. **減価償却費**: 物件の取得価額・耐用年数から自動計算
3. **その他**: 稼働率、管理費率などは手動入力

#### 独立シミュレーション
1. **家賃収入**: 手動入力（年間家賃収入）
2. **減価償却費**: 手動入力
3. **その他**: すべて手動入力

---

## 🔧 実装詳細

### 1. データベースモデルの修正

**ファイル**: `app/models_property.py`

```python
class TSimulation(Base):
    __tablename__ = 'T_シミュレーション'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, nullable=False)
    名称 = Column(String(200), nullable=False)
    
    # シミュレーション種別
    シミュレーション種別 = Column(String(20), nullable=False, default='物件ベース')
    
    # 物件ベースシミュレーション用
    物件id = Column(Integer, nullable=True)
    
    # 独立シミュレーション用
    年間家賃収入 = Column(Numeric(15, 2), nullable=True)
    部屋数 = Column(Integer, nullable=True)
    
    # 共通フィールド
    開始年度 = Column(Integer, nullable=False)
    期間 = Column(Integer, nullable=False)
    稼働率 = Column(Numeric(5, 2), default=95.00)
    管理費率 = Column(Numeric(5, 2), default=5.00)
    修繕費率 = Column(Numeric(5, 2), default=5.00)
    固定資産税 = Column(Numeric(15, 2), default=0)
    損害保険料 = Column(Numeric(15, 2), default=0)
    ローン残高 = Column(Numeric(15, 2), default=0)
    ローン金利 = Column(Numeric(5, 2), default=0)
    ローン年間返済額 = Column(Numeric(15, 2), default=0)
    その他収入 = Column(Numeric(15, 2), default=0)
    その他経費 = Column(Numeric(15, 2), default=0)
    減価償却費 = Column(Numeric(15, 2), default=0)
    その他所得 = Column(Numeric(15, 2), default=0)
    作成日時 = Column(DateTime, default=datetime.now)
```

### 2. シミュレーション作成フォームの修正

**ファイル**: `app/templates/property_simulation_new.html`

#### シミュレーション種別の選択

```html
<div class="mb-3">
    <label for="シミュレーション種別" class="form-label">シミュレーション種別 <span class="text-danger">*</span></label>
    <select class="form-select" id="シミュレーション種別" name="シミュレーション種別" required onchange="toggleSimulationType()">
        <option value="物件ベース">物件ベースシミュレーション</option>
        <option value="独立">独立シミュレーション</option>
    </select>
    <div class="form-text">
        物件ベース: 既存物件のデータを使用<br>
        独立: すべての項目を手動入力
    </div>
</div>
```

#### 物件ベースシミュレーション用フィールド

```html
<div id="property-based-fields" style="display: block;">
    <div class="mb-3">
        <label for="物件id" class="form-label">対象物件 <span class="text-danger">*</span></label>
        <select class="form-select" id="物件id" name="物件id">
            <option value="">物件を選択してください</option>
            {% for property in properties %}
                <option value="{{ property.id }}">{{ property.物件名 }}</option>
            {% endfor %}
        </select>
    </div>
</div>
```

#### 独立シミュレーション用フィールド

```html
<div id="independent-fields" style="display: none;">
    <div class="mb-3">
        <label for="年間家賃収入" class="form-label">年間家賃収入（円） <span class="text-danger">*</span></label>
        <input type="number" class="form-control" id="年間家賃収入" name="年間家賃収入" 
               value="0" step="10000">
        <div class="form-text">満室時の年間家賃収入を入力してください</div>
    </div>
    
    <div class="mb-3">
        <label for="部屋数" class="form-label">部屋数</label>
        <input type="number" class="form-control" id="部屋数" name="部屋数" 
               value="0" min="0">
        <div class="form-text">参考情報として入力（計算には使用されません）</div>
    </div>
</div>
```

#### JavaScript for 切り替え

```javascript
<script>
function toggleSimulationType() {
    const type = document.getElementById('シミュレーション種別').value;
    const propertyFields = document.getElementById('property-based-fields');
    const independentFields = document.getElementById('independent-fields');
    
    if (type === '物件ベース') {
        propertyFields.style.display = 'block';
        independentFields.style.display = 'none';
        document.getElementById('物件id').required = true;
        document.getElementById('年間家賃収入').required = false;
    } else {
        propertyFields.style.display = 'none';
        independentFields.style.display = 'block';
        document.getElementById('物件id').required = false;
        document.getElementById('年間家賃収入').required = true;
    }
}
</script>
```

### 3. 計算ロジックの修正

**ファイル**: `app/blueprints/property.py` - `calculate_simulation`関数

```python
def calculate_simulation(simulation, db):
    """シミュレーション計算"""
    
    # シミュレーション種別によって計算方法を分岐
    if simulation.シミュレーション種別 == '物件ベース':
        return calculate_property_based_simulation(simulation, db)
    else:
        return calculate_independent_simulation(simulation, db)

def calculate_property_based_simulation(simulation, db):
    """物件ベースシミュレーション計算"""
    
    # 物件データを取得
    property_data = db.execute(
        select(TBukken).where(TBukken.id == simulation.物件id)
    ).scalar_one_or_none()
    
    if not property_data:
        return False
    
    # 部屋データから家賃収入を計算
    rooms = db.execute(
        select(THeya).where(THeya.property_id == simulation.物件id, THeya.有効 == 1)
    ).scalars().all()
    
    満室時家賃収入 = sum(room.家賃 or 0 for room in rooms) * 12
    
    # 年度ごとの計算
    for year_offset in range(simulation.期間):
        年度 = simulation.開始年度 + year_offset
        
        # 家賃収入
        家賃収入 = 満室時家賃収入 * (simulation.稼働率 / 100)
        
        # 減価償却費（物件データから自動計算 or 手動入力）
        if simulation.減価償却費 and simulation.減価償却費 > 0:
            減価償却費 = simulation.減価償却費
        else:
            # 物件データから自動計算
            if property_data.償却方法 == '定額法' and property_data.耐用年数:
                減価償却費 = (property_data.取得価額 - (property_data.残存価額 or 0)) / property_data.耐用年数
            else:
                減価償却費 = Decimal('0')
        
        # ... 残りの計算
        
def calculate_independent_simulation(simulation, db):
    """独立シミュレーション計算"""
    
    # 年度ごとの計算
    for year_offset in range(simulation.期間):
        年度 = simulation.開始年度 + year_offset
        
        # 家賃収入（手動入力値を使用）
        家賃収入 = simulation.年間家賃収入 * (simulation.稼働率 / 100)
        
        # 減価償却費（手動入力値を使用）
        減価償却費 = simulation.減価償却費
        
        # ... 残りの計算
```

---

## 📊 UI/UX設計

### シミュレーション一覧画面

- シミュレーション種別をバッジで表示
  - 物件ベース: 青色バッジ「物件ベース」
  - 独立: 緑色バッジ「独立」

### シミュレーション詳細画面

- シミュレーション種別を明示
- 物件ベースの場合: 物件名とリンクを表示
- 独立の場合: 「独立シミュレーション」と表示

---

## ✅ 実装チェックリスト

### データベース
- [ ] TSimulationモデルに`シミュレーション種別`フィールドを追加
- [ ] TSimulationモデルに`年間家賃収入`フィールドを追加
- [ ] TSimulationモデルに`部屋数`フィールドを追加
- [ ] マイグレーションスクリプトを作成

### バックエンド
- [ ] `calculate_simulation`関数を分岐処理に変更
- [ ] `calculate_property_based_simulation`関数を実装
- [ ] `calculate_independent_simulation`関数を実装
- [ ] シミュレーション作成ルートを修正

### フロントエンド
- [ ] シミュレーション種別選択UIを追加
- [ ] 物件ベース用フィールドを実装
- [ ] 独立シミュレーション用フィールドを実装
- [ ] JavaScript切り替え機能を実装
- [ ] シミュレーション一覧にバッジを追加
- [ ] シミュレーション詳細に種別表示を追加

### テスト
- [ ] 物件ベースシミュレーションの作成テスト
- [ ] 独立シミュレーションの作成テスト
- [ ] 計算結果の検証
- [ ] UI切り替えの動作確認

---

## 🎯 期待される効果

### 物件ベースシミュレーション
- 既存物件の実データに基づいた正確な予測
- データ入力の手間を削減
- 実績との比較が容易

### 独立シミュレーション
- 購入検討中の物件の試算が可能
- 複数のシナリオを自由に比較
- What-if分析が容易

---

## 📝 注意事項

1. **バリデーション**: シミュレーション種別に応じて必須フィールドを動的に変更
2. **データ整合性**: 物件ベースの場合は物件IDが必須、独立の場合は年間家賃収入が必須
3. **後方互換性**: 既存のシミュレーションは「物件ベース」として扱う
