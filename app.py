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

st.title("🛡️ 保險年齡計算器 (2026 修正版)")
st.write(f"目前系統日期：{today_tw}")

# --- 第一部分：輸入區 ---
st.subheader("1. 出生日期")
col1, col2, col3 = st.columns(3)

with col1:
    input_year = st.number_input("年份 (民國或西元)", min_value=1, max_value=2100, value=84)
with col2:
    input_month = st.number_input("月份", min_value=1, max_value=12, value=1)
with col3:
    input_day = st.number_input("日期", min_value=1, max_value=31, value=1)

# 自動判定民國/西元
if input_year < 1900:
    ad_year = input_year + 1911
    year_type = f"民國 {input_year} 年"
else:
    ad_year = input_year
    year_type = f"西元 {input_year} 年"

try:
    birth_date = date(ad_year, input_month, input_day)
except ValueError:
    st.error("❌ 日期格式錯誤，請重新確認！")
    st.stop()

effective_date = st.date_input("2. 計算基準日", value=today_tw)

# --- 第二部分：核心邏輯計算 ---
if st.button("🚀 開始精確計算"):
    if birth_date > effective_date:
        st.error("出生日期不可晚於基準日！")
    else:
        # A. 計算足歲
        diff = relativedelta(effective_date, birth_date)
        
        # B. 保險年齡：超過 6 個月又 1 天進位
        if diff.months > 6 or (diff.months == 6 and diff.days >= 1):
            ins_age = diff.years + 1
            age_status = "已進位 (+1)"
        else:
            ins_age = diff.years
            age_status = "足歲計算"

        # C. 修正跨年跳歲日邏輯
        # 取得基準日當年的生日，再加 6 個月
        this_year_critical = birth_date.replace(year=effective_date.year) + relativedelta(months=6)
        
        # 如果基準日已經 >= 今年跳歲點，則下一個跳歲點在明年
        if effective_date >= this_year_critical:
            next_critical_date = birth_date.replace(year=effective_date.year + 1) + relativedelta(months=6)
        else:
            next_critical_date = this_year_critical
        
        days_to_jump = (next_critical_date - effective_date).days
        
        # 轉換下一個跳歲日為民國年顯示
        roc_critical_year = next_critical_date.year - 1911
        roc_critical_str = f"民國 {roc_critical_year} 年 {next_critical_date.month} 月 {next_critical_date.day} 日"

        # --- 第三部分：結果顯示 ---
        st.divider()
        st.write(f"🎂 出生日期：{year_type} {input_month} 月 {input_day} 日")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("目前保險年齡", f"{ins_age} 歲")
        with col_res2:
            st.metric("距離下次跳歲", f"{days_to_jump} 天")

        # 核心亮點：直接顯示日期
        st.subheader("📅 跳歲倒計時")
        st.markdown(f"您的下一個保險跳歲日期為：")
        st.markdown(f"#### `{next_critical_date.strftime('%Y-%m-%d')} ({roc_critical_str})`")

        st.info(f"📊 詳細進度：目前足歲為 **{diff.years} 歲 {diff.months} 個月 {diff.days} 天** ({age_status})")

        # 警示邏輯
        if days_to_jump <= 30:
            st.error(f"⚠️ **急迫警示：** 距離跳歲僅剩 **{days_to_jump}** 天！\n\n請注意，在 **{next_critical_date}** 之後投保，保險年齡將變為 **{ins_age + 1}** 歲，保費級距將會調升。")
        elif days_to_jump <= 90:
            st.warning(f"🔔 **溫馨提醒：** 距離下次跳歲還有 {days_to_jump} 天。建議提早規劃。")
