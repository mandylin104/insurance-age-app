import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta

# 設定網頁標題
st.set_page_config(page_title="保險年齡計算器", page_icon="📋")

st.title("🎯 保險年齡快速計算器")
st.write("採用「半年進位法」：超過六個月又一天即進位一歲。")

# 介面輸入
birth_date = st.date_input("請選擇出生日期", value=date(1995, 1, 1), min_value=date(1900, 1, 1))
effective_date = st.date_input("請選擇保單生效日/計算基準日", value=date.today())

if st.button("開始計算"):
    if birth_date > effective_date:
        st.error("錯誤：出生日期不能晚於生效日期！")
    else:
        # 計算足歲與差距
        diff = relativedelta(effective_date, birth_date)
        years = diff.years
        months = diff.months
        days = diff.days

        # 保險年齡邏輯
        if months > 6 or (months == 6 and days >= 1):
            ins_age = years + 1
            reason = "（因超過 6 個月，進位 +1 歲）"
        else:
            ins_age = years
            reason = "（未滿 6 個月，不進位）"

        # 顯示結果
        st.success(f"### 您的保險年齡為：{ins_age} 歲")
        st.info(f"實際足歲：{years} 歲 {months} 個月 {days} 天 \n\n 計算邏輯：{reason}")

st.caption("註：本工具僅供參考，實際投保年齡請以各保險公司核定為準。")