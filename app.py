import streamlit as st
from datetime import date, datetime  # 加上 datetime
from dateutil.relativedelta import relativedelta
import pytz  # 加上這行處理時區

# --- 新增時區設定 ---
tw_timezone = pytz.timezone('Asia/Taipei')
# 取得台灣當前的日期
today_tw = datetime.now(tw_timezone).date()

# 設定網頁標題
st.set_page_config(page_title="保險年齡計算器 (含跳歲預警)", page_icon="🔔")

st.title("🎯 保險年齡快速計算器")
st.write(f"目前系統日期 (台北時區)：{today_tw}") # 顯示日期方便確認
st.write("採用「半年進位法」：超過 6 個月又 1 天即進位一歲。")

# 介面輸入
birth_date = st.date_input("請選擇出生日期", value=date(1995, 1, 1), min_value=date(1900, 1, 1))

# --- 修改這裡：將 value 改為 today_tw ---
effective_date = st.date_input("請選擇計算基準日 (預設今天)", value=today_tw)

if st.button("開始計算"):
    # ... 以下計算邏輯保持不變 ...
    if birth_date > effective_date:
        st.error("錯誤：出生日期不能晚於生效日期！")
    else:
        # 計算目前的足歲與差距
        diff = relativedelta(effective_date, birth_date)
        years = diff.years
        months = diff.months
        days = diff.days

        # 保險年齡邏輯
        if months > 6 or (months == 6 and days >= 1):
            ins_age = years + 1
        else:
            ins_age = years
        
        # 計算下一次跳歲日
        this_year_birthday = birth_date.replace(year=effective_date.year)
        critical_date = this_year_birthday + relativedelta(months=6)
        if effective_date >= critical_date:
            critical_date = (this_year_birthday + relativedelta(years=1)) + relativedelta(months=6)
        
        days_to_jump = (critical_date - effective_date).days

        st.divider()
        st.success(f"### 您的保險年齡為：{ins_age} 歲")
        st.info(f"實際足歲：{years} 歲 {months} 個月 {days} 天")

        if days_to_jump <= 30:
            st.warning(f"⚠️ **注意：保費即將變貴！**\n\n距離跳到 **{ins_age + 1} 歲** 只剩 **{days_to_jump}** 天！")
        else:
            st.write(f"✅ 距離下次保險跳歲還有 **{days_to_jump}** 天。")
