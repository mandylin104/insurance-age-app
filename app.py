import streamlit as st
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# 設定網頁標題
st.set_page_config(page_title="保險年齡計算器 (含跳歲預警)", page_icon="🔔")

st.title("🎯 保險年齡快速計算器")
st.write("採用「半年進位法」：超過 6 個月又 1 天即進位一歲。")

# 介面輸入
birth_date = st.date_input("請選擇出生日期", value=date(1995, 1, 1), min_value=date(1900, 1, 1))
effective_date = st.date_input("請選擇計算基準日 (預設今天)", value=date.today())

if st.button("開始計算"):
    if birth_date > effective_date:
        st.error("錯誤：出生日期不能晚於生效日期！")
    else:
        # 1. 計算目前的足歲與差距
        diff = relativedelta(effective_date, birth_date)
        years = diff.years
        months = diff.months
        days = diff.days

        # 2. 計算保險年齡
        if months > 6 or (months == 6 and days >= 1):
            ins_age = years + 1
            status = "已進位"
        else:
            ins_age = years
            status = "足歲"

        # 3. 計算【跳歲日】（生日 + 6個月）
        # 如果目前還沒過半，跳歲日就是「今年的生日 + 6個月」
        # 如果目前已經過半，下一次跳歲日就是「明年的生日 + 6個月」
        this_year_birthday = birth_date.replace(year=effective_date.year)
        critical_date = this_year_birthday + relativedelta(months=6)
        
        # 如果基準日已經超過今年的跳歲日，就找明年的
        if effective_date >= critical_date:
            critical_date = (this_year_birthday + relativedelta(years=1)) + relativedelta(months=6)
        
        # 計算距離跳歲還有幾天
        days_to_jump = (critical_date - effective_date).days

        # --- 顯示結果 ---
        st.divider()
        st.success(f"### 您的保險年齡為：{ins_age} 歲")
        st.info(f"實際足歲：{years} 歲 {months} 個月 {days} 天")

        # --- 跳歲警示邏輯 ---
        if days_to_jump <= 30:
            st.warning(f"⚠️ **注意：保費即將變貴！**\n\n距離保險年齡跳到 **{ins_age + 1} 歲** 只剩 **{days_to_jump}** 天！建議儘速完成投保。")
        elif days_to_jump <= 90:
            st.warning(f"💡 **溫馨提示：** 距離保險年齡跳歲還有 **{days_to_jump}** 天 (預計於 {critical_date} 跳歲)。")
        else:
            st.write(f"✅ 距離下次保險跳歲還有 **{days_to_jump}** 天。")

st.caption("註：保險年齡跳歲通常發生在生日後的第 6 個月又 1 天。實際請以保險公司合約為準。")
