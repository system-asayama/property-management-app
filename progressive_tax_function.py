def calculate_progressive_tax(total_income):
    """
    超過累進税率による税金計算（所得税+住民税）
    
    Args:
        total_income: 課税所得（円）
    
    Returns:
        税金額（円）
    """
    from decimal import Decimal
    
    total_income = Decimal(str(total_income))
    
    # 所得税の計算（超過累進）
    income_tax = Decimal('0')
    
    if total_income <= 0:
        income_tax = Decimal('0')
    elif total_income <= 1950000:
        # 195万円以下: 5%
        income_tax = total_income * Decimal('0.05')
    elif total_income <= 3300000:
        # 195万円超～330万円以下: 195万円まで5%、超過分10%
        income_tax = Decimal('1950000') * Decimal('0.05') + \
                     (total_income - Decimal('1950000')) * Decimal('0.10')
    elif total_income <= 6950000:
        # 330万円超～695万円以下
        income_tax = Decimal('1950000') * Decimal('0.05') + \
                     Decimal('1350000') * Decimal('0.10') + \
                     (total_income - Decimal('3300000')) * Decimal('0.20')
    elif total_income <= 9000000:
        # 695万円超～900万円以下
        income_tax = Decimal('1950000') * Decimal('0.05') + \
                     Decimal('1350000') * Decimal('0.10') + \
                     Decimal('3650000') * Decimal('0.20') + \
                     (total_income - Decimal('6950000')) * Decimal('0.23')
    elif total_income <= 18000000:
        # 900万円超～1,800万円以下
        income_tax = Decimal('1950000') * Decimal('0.05') + \
                     Decimal('1350000') * Decimal('0.10') + \
                     Decimal('3650000') * Decimal('0.20') + \
                     Decimal('2050000') * Decimal('0.23') + \
                     (total_income - Decimal('9000000')) * Decimal('0.33')
    elif total_income <= 40000000:
        # 1,800万円超～4,000万円以下
        income_tax = Decimal('1950000') * Decimal('0.05') + \
                     Decimal('1350000') * Decimal('0.10') + \
                     Decimal('3650000') * Decimal('0.20') + \
                     Decimal('2050000') * Decimal('0.23') + \
                     Decimal('9000000') * Decimal('0.33') + \
                     (total_income - Decimal('18000000')) * Decimal('0.40')
    else:
        # 4,000万円超
        income_tax = Decimal('1950000') * Decimal('0.05') + \
                     Decimal('1350000') * Decimal('0.10') + \
                     Decimal('3650000') * Decimal('0.20') + \
                     Decimal('2050000') * Decimal('0.23') + \
                     Decimal('9000000') * Decimal('0.33') + \
                     Decimal('22000000') * Decimal('0.40') + \
                     (total_income - Decimal('40000000')) * Decimal('0.45')
    
    # 住民税の計算（一律10%）
    if total_income > 0:
        resident_tax = total_income * Decimal('0.10')
    else:
        resident_tax = Decimal('0')
    
    # 合計税金
    total_tax = income_tax + resident_tax
    
    return total_tax


def calculate_tax_rate_for_display(total_income):
    """
    表示用の実効税率を計算
    
    Args:
        total_income: 課税所得（円）
    
    Returns:
        実効税率（%）
    """
    from decimal import Decimal
    
    total_income = Decimal(str(total_income))
    
    if total_income <= 0:
        return Decimal('0')
    
    total_tax = calculate_progressive_tax(total_income)
    effective_rate = (total_tax / total_income) * Decimal('100')
    
    return effective_rate
