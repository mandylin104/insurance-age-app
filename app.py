import streamlit as st
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pytz

# --- 1. 安全檢查與密碼提示邏輯 ---
def check_password():
    """驗證密碼，若正確則回傳 True"""
    
    # 初始化錯誤計數器
    if "retry_count" not in st.session_state:
        st.session_state["retry_count"] = 0

    if "password_correct" not in st.session_state:
        st.subheader("🔒 本系統受保護")
        # 預設提示
        st.info("💡 密碼提示：請輸入預設的三位數字密碼-欣台地址號碼+樓層。")
        
        st.text_input("請輸入存取密碼", type="password", on_change=password_entered, key="password")
        return False
    
    elif not st.session_state["password_correct"]:
        st.subheader("🔒 本系統受保護")
        
        # 根據錯誤次數給予動態提示
        if st.session_state["retry_count"] >= 3:
            st.error("❌ 密碼錯誤多次！")
            st.warning("🆘 終極提示：密碼是欣台地址的號碼+樓層 (即 357)。")
        else:
            st.error("❌ 密碼錯誤，請重新輸入。")
            st.info("💡 提示：密碼與「欣台地址的號碼+樓層」數字。")
            
        st.text_input("請輸入存取密碼", type="password", on_change=password_entered, key="password")
        return False
        
    return True

def password_entered():
    # 在此設定你的密碼
    if st.session_state["password"] == "357": 
        st.session_state["password_correct"] = True
        st.session_state["retry_count"] = 0 
        del st.session_state["password"]
    else:
        st.session_state["password_correct"] = False
        st.session_state["retry_count"] += 1

# 如果密碼驗證未通過，則停止執行後續程式
if not check_password():
    st.stop()


# --- 2. 時區設定 ---
tw_tz = pytz.timezone('Asia/Taipei')
today_tw = datetime.now(tw_tz).date()

st.set_page_config(page_title="專業保險年齡計算器", page_icon="🛡️")
st.title("🛡️ 保險年齡計算器 (2026 精確修正版)")
st.write(f"目前系統日期：{today_tw}")

# --- 第一部分：輸入區 ---
st.subheader("1. 出生日期")
col1, col2, col3 = st.columns(3)
with col1:
    input_year = st.number_input("年份 (民國或西元)", min_value=1, max_value=2100, value=109)
with col2:
    input_month = st.number_input("月份", min_value=1, max_value=12, value=9)
with col3:
    input_day = st.number_input("日期", min_value=1, max_value=31, value=12)

# 自動判定民國/西元
ad_year = input_year + 1911 if input_year < 1900 else input_year
year_display = f"民國 {input_year} 年" if input_year < 1900 else f"西元 {input_year} 年"

try:
    birth_date = date(ad_year, input_month, input_day)
except ValueError:
    st.error("❌ 日期格式錯誤！")
    st.stop()

effective_date = st.date_input("2. 計算基準日", value=today_tw)

# --- 第二部分：核心邏輯計算 ---
if st.button("🚀 開始精確計算"):
    if birth_date > effective_date:
        st.error("出生日期不可晚於基準日！")
    else:
        # A. 計算足歲差距
        diff = relativedelta(effective_date, birth_date)
        
        # B. 保險年齡邏輯
        if diff.months > 6 or (diff.months == 6 and diff.days >= 1):
            ins_age = diff.years + 1
        else:
            ins_age = diff.years

        # C. 【重要修正】計算下一個跳歲點 (Next Critical Date)
        # 邏輯：跳歲點發生在「生日後的 6 個月又 1 天」或「生日當天（滿整歲）」
        # 我們找出所有可能的臨界點，取「大於今天」的最小那一個
        
        # 臨界點 1：今年的生日
        bday_this_year = birth_date.replace(year=effective_date.year)
        # 臨界點 2：今年的生日 + 6 個月
        half_year_this_year = bday_this_year + relativedelta(months=6)
        # 臨界點 3：明年的生日
        bday_next_year = birth_date.replace(year=effective_date.year + 1)
        # 臨界點 4：明年的生日 + 6 個月
        half_year_next_year = bday_next_year + relativedelta(months=6)
        
        potential_dates = [bday_this_year, half_year_this_year, bday_next_year, half_year_next_year]
        # 過濾掉已經過去的日期，並排序
        upcoming_dates = sorted([d for d in potential_dates if d > effective_date])
        
        # 下一個跳歲日期
        next_critical_date = upcoming_dates[0]
        days_to_jump = (next_critical_date - effective_date).days
        
        # 民國格式轉換
        roc_critical_year = next_critical_date.year - 1911
        roc_critical_str = f"民國 {roc_critical_year} 年 {next_critical_date.month} 月 {next_critical_date.day} 日"

        # --- 第三部分：結果顯示 ---
        st.divider()
        st.write(f"🎂 出生日期：{year_display} {input_month} 月 {input_day} 日")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("目前保險年齡", f"{ins_age} 歲")
        with col_res2:
            st.metric("距離下次跳歲", f"{days_to_jump} 天")

        st.subheader("📅 下次跳歲預告")
        st.markdown(f"您的下一個保險跳歲日期為：")
        st.markdown(f"#### `{next_critical_date.strftime('%Y-%m-%d')} ({roc_critical_str})`")

        st.info(f"📊 詳細進度：目前實際足歲為 **{diff.years} 歲 {diff.months} 個月 {diff.days} 天**")

        if days_to_jump <= 30:
            st.error(f"⚠️ **急迫警示：** 僅剩 **{days_to_jump}** 天就要跳歲（變為 {ins_age + 1} 歲）！")

