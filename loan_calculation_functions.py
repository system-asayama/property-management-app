from decimal import Decimal
import math


def calculate_monthly_payment_equal_installment(principal, annual_rate, years):
    """
    元利均等返済の月額返済額を計算
    
    Args:
        principal: 借入金額（円）
        annual_rate: 年利（%）
        years: 返済期間（年）
    
    Returns:
        月額返済額（円）
    """
    principal = Decimal(str(principal))
    annual_rate = Decimal(str(annual_rate))
    years = int(years)
    
    if principal <= 0 or years <= 0:
        return Decimal('0')
    
    if annual_rate == 0:
        # 金利0%の場合は単純に元金を分割
        months = years * 12
        return principal / months
    
    # 月利を計算
    monthly_rate = annual_rate / Decimal('100') / Decimal('12')
    months = years * 12
    
    # 元利均等返済の計算式
    # 月額返済額 = 借入金額 × 月利 × (1 + 月利)^返済回数 / ((1 + 月利)^返済回数 - 1)
    
    # (1 + 月利)^返済回数 を計算
    rate_plus_one = Decimal('1') + monthly_rate
    power_term = rate_plus_one ** months
    
    monthly_payment = principal * monthly_rate * power_term / (power_term - Decimal('1'))
    
    return monthly_payment


def calculate_annual_payment_equal_installment(principal, annual_rate, years):
    """
    元利均等返済の年間返済額を計算
    
    Args:
        principal: 借入金額（円）
        annual_rate: 年利（%）
        years: 返済期間（年）
    
    Returns:
        年間返済額（円）
    """
    monthly_payment = calculate_monthly_payment_equal_installment(principal, annual_rate, years)
    annual_payment = monthly_payment * Decimal('12')
    
    return annual_payment


def calculate_first_monthly_payment_equal_principal(principal, annual_rate, years):
    """
    元金均等返済の初回月額返済額を計算
    
    Args:
        principal: 借入金額（円）
        annual_rate: 年利（%）
        years: 返済期間（年）
    
    Returns:
        初回月額返済額（円）
    """
    principal = Decimal(str(principal))
    annual_rate = Decimal(str(annual_rate))
    years = int(years)
    
    if principal <= 0 or years <= 0:
        return Decimal('0')
    
    months = years * 12
    
    # 毎月の元金返済額
    monthly_principal = principal / months
    
    # 初回の利息（借入金額全体に対する利息）
    monthly_rate = annual_rate / Decimal('100') / Decimal('12')
    first_interest = principal * monthly_rate
    
    # 初回月額返済額 = 元金返済額 + 初回利息
    first_monthly_payment = monthly_principal + first_interest
    
    return first_monthly_payment


def calculate_annual_payment_equal_principal(principal, annual_rate, years):
    """
    元金均等返済の年間返済額を計算（初年度）
    
    Args:
        principal: 借入金額（円）
        annual_rate: 年利（%）
        years: 返済期間（年）
    
    Returns:
        初年度の年間返済額（円）
    """
    principal = Decimal(str(principal))
    annual_rate = Decimal(str(annual_rate))
    years = int(years)
    
    if principal <= 0 or years <= 0:
        return Decimal('0')
    
    months = years * 12
    monthly_rate = annual_rate / Decimal('100') / Decimal('12')
    
    # 毎月の元金返済額
    monthly_principal = principal / months
    
    # 初年度（1～12ヶ月目）の返済額を計算
    annual_payment = Decimal('0')
    remaining_principal = principal
    
    for month in range(12):
        # 当月の利息
        monthly_interest = remaining_principal * monthly_rate
        # 当月の返済額
        monthly_payment = monthly_principal + monthly_interest
        annual_payment += monthly_payment
        # 残高を更新
        remaining_principal -= monthly_principal
    
    return annual_payment


def calculate_loan_payment(principal, annual_rate, years, method='元利均等'):
    """
    ローン返済額を計算（年間）
    
    Args:
        principal: 借入金額（円）
        annual_rate: 年利（%）
        years: 返済期間（年）
        method: 返済方法（'元利均等' or '元金均等'）
    
    Returns:
        年間返済額（円）
    """
    if method == '元利均等':
        return calculate_annual_payment_equal_installment(principal, annual_rate, years)
    elif method == '元金均等':
        return calculate_annual_payment_equal_principal(principal, annual_rate, years)
    else:
        return Decimal('0')


# テスト
if __name__ == '__main__':
    print("ローン返済額計算テスト")
    print("=" * 60)
    
    # テストケース
    principal = 30000000  # 3000万円
    annual_rate = 2.0  # 年利2%
    years = 35  # 35年
    
    print(f"\n借入金額: {principal:,}円")
    print(f"年利: {annual_rate}%")
    print(f"返済期間: {years}年")
    
    # 元利均等返済
    print("\n【元利均等返済】")
    monthly_equal = calculate_monthly_payment_equal_installment(principal, annual_rate, years)
    annual_equal = calculate_annual_payment_equal_installment(principal, annual_rate, years)
    print(f"月額返済額: {int(monthly_equal):,}円")
    print(f"年間返済額: {int(annual_equal):,}円")
    
    # 元金均等返済
    print("\n【元金均等返済】")
    first_monthly_principal = calculate_first_monthly_payment_equal_principal(principal, annual_rate, years)
    annual_principal = calculate_annual_payment_equal_principal(principal, annual_rate, years)
    print(f"初回月額返済額: {int(first_monthly_principal):,}円")
    print(f"初年度年間返済額: {int(annual_principal):,}円")
