#!/usr/bin/env python3
"""
シミュレーション編集テンプレートのselectフィールドにselected属性を追加する
"""

with open('app/templates/property_simulation_edit.html', 'r', encoding='utf-8') as f:
    content = f.read()

# シミュレーション種別のselected属性を追加
content = content.replace(
    '<option value="物件ベース">物件ベース（既存物件データを使用）</option>',
    '<option value="物件ベース" {% if simulation.シミュレーション種別 == "物件ベース" %}selected{% endif %}>物件ベース（既存物件データを使用）</option>'
)
content = content.replace(
    '<option value="独立">独立シミュレーション（手動入力）</option>',
    '<option value="独立" {% if simulation.シミュレーション種別 == "独立" %}selected{% endif %}>独立シミュレーション（手動入力）</option>'
)

# 物件IDのselected属性を追加
content = content.replace(
    '<option value="">全物件</option>',
    '<option value="" {% if not simulation.物件id %}selected{% endif %}>全物件</option>'
)
content = content.replace(
    '<option value="{{ property.id }}">{{ property.物件名 }}</option>',
    '<option value="{{ property.id }}" {% if simulation.物件id == property.id %}selected{% endif %}>{{ property.物件名 }}</option>'
)

# 償却方法のselected属性を追加（建物）
content = content.replace(
    'id="建物_償却方法" name="建物_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" selected>定額法</option>',
    'id="建物_償却方法" name="建物_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" {% if simulation.建物_償却方法 == "定額法" or not simulation.建物_償却方法 %}selected{% endif %}>定額法</option>'
)
content = content.replace(
    'id="建物_償却方法" name="建物_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" {% if simulation.建物_償却方法 == "定額法" or not simulation.建物_償却方法 %}selected{% endif %}>定額法</option>\n                                        <option value="定率法">定率法</option>',
    'id="建物_償却方法" name="建物_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" {% if simulation.建物_償却方法 == "定額法" or not simulation.建物_償却方法 %}selected{% endif %}>定額法</option>\n                                        <option value="定率法" {% if simulation.建物_償却方法 == "定率法" %}selected{% endif %}>定率法</option>'
)

# 償却方法のselected属性を追加（付属設備）
content = content.replace(
    'id="付属設備_償却方法" name="付属設備_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" selected>定額法</option>',
    'id="付属設備_償却方法" name="付属設備_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" {% if simulation.付属設備_償却方法 == "定額法" or not simulation.付属設備_償却方法 %}selected{% endif %}>定額法</option>'
)
content = content.replace(
    'id="付属設備_償却方法" name="付属設備_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" {% if simulation.付属設備_償却方法 == "定額法" or not simulation.付属設備_償却方法 %}selected{% endif %}>定額法</option>\n                                        <option value="定率法">定率法</option>',
    'id="付属設備_償却方法" name="付属設備_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" {% if simulation.付属設備_償却方法 == "定額法" or not simulation.付属設備_償却方法 %}selected{% endif %}>定額法</option>\n                                        <option value="定率法" {% if simulation.付属設備_償却方法 == "定率法" %}selected{% endif %}>定率法</option>'
)

# 償却方法のselected属性を追加（構築物）
content = content.replace(
    'id="構築物_償却方法" name="構築物_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" selected>定額法</option>',
    'id="構築物_償却方法" name="構築物_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" {% if simulation.構築物_償却方法 == "定額法" or not simulation.構築物_償却方法 %}selected{% endif %}>定額法</option>'
)
content = content.replace(
    'id="構築物_償却方法" name="構築物_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" {% if simulation.構築物_償却方法 == "定額法" or not simulation.構築物_償却方法 %}selected{% endif %}>定額法</option>\n                                        <option value="定率法">定率法</option>',
    'id="構築物_償却方法" name="構築物_償却方法" onchange="calculateDepreciation()">\n                                        <option value="定額法" {% if simulation.構築物_償却方法 == "定額法" or not simulation.構築物_償却方法 %}selected{% endif %}>定額法</option>\n                                        <option value="定率法" {% if simulation.構築物_償却方法 == "定率法" %}selected{% endif %}>定率法</option>'
)

with open('app/templates/property_simulation_edit.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ selectフィールドのselected属性を追加しました")
