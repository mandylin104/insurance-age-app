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
import streamlit as st
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pytz

# 1. 設定台北時區，確保 2026 年日期正確
tw_tz = pytz.timezone('Asia/Taipei')
today_tw = datetime.now(tw_tz).date()

st.set_page_config(page_title="標準保險年齡計算器", page_icon="🛡️")
st.title("🛡️ 標準保險年齡計算器 (精確進位版)")
st.write(f"📅 系統基準日：{today_tw}")

# --- 第一部分：輸入區 ---
st.subheader("1. 出生日期")
col1, col2, col3 = st.columns(3)
with col1:
    input_year = st.number_input("年份 (民國或西元)", min_value=1, max_value=2100, value=84)
with col2:
    input_month = st.number_input("月份", min_value=1, max_value=12, value=1)
with col3:
    input_day = st.number_input("日期", min_value=1, max_value=31, value=1)

# 民國/西元轉換
ad_year = input_year + 1911 if input_year < 1900 else input_year
year_display = f"民國 {input_year} 年" if input_year < 1900 else f"西元 {input_year} 年"

try:
    birth_date = date(ad_year, input_month, input_day)
except ValueError:
    st.error("❌ 日期格式錯誤，請重新確認！")
    st.stop()

# 讓使用者可以調整計算基準日 (例如試算未來某天的保險年齡)
effective_date = st.date_input("2. 計算基準日", value=today_tw)

# --- 第二部分：核心邏輯計算 ---
if st.button("🚀 執行精確保費計算"):
    if birth_date > effective_date:
        st.error("出生日期不可晚於基準日！")
    else:
        # A. 計算足歲差距 (例如 30歲 6個月 2天)
        diff = relativedelta(effective_date, birth_date)
        
        # B. 保險年齡邏輯：生日過 6 個月又 1 天即進位
        # 如果月數 > 6，或是剛好 6 個月且有剩餘天數，就進位
        is_rounded_up = diff.months > 6 or (diff.months == 6 and diff.days >= 1)
        ins_age = diff.years + 1 if is_rounded_up else diff.years

        # C. 【徹底修正】計算距離「下一個跳歲點」還有幾天
        # 跳歲點 1: 生日當天 (從進位狀態回到新的足歲)
        # 跳歲點 2: 生日+6個月 (從足歲變進位)
        
        # 建立一個包含 今年/明年 所有可能的變動點清單
        points = []
        for y in [effective_date.year, effective_date.year + 1]:
            # 點 A: 該年的生日
            b_day = birth_date.replace(year=y)
            points.append(b_day)
            # 點 B: 該年的生日 + 6個月 (進位轉折點)
            round_up_day = b_day + relativedelta(months=6)
            points.append(round_up_day)
        
        # 找出第一個比今天晚的變動日期
        next_jump_date = min([p for p in points if p > effective_date])
        days_to_jump = (next_jump_date - effective_date).days

        # --- 第三部分：顯示結果 ---
        st.divider()
        st.write(f"🎂 出生日期確認：{year_display} {input_month} 月 {input_day} 日")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("目前保險年齡", f"{ins_age} 歲")
        with col_res2:
            st.metric("距離下次跳歲", f"{days_to_jump} 天")

        # 顯示具體日期與民國年
        roc_jump_year = next_jump_date.year - 1911
        st.subheader("📅 下次保費變動預警")
        st.write(f"下次跳歲日期：**{next_jump_date} (民國 {roc_jump_year} 年)**")

        # --- 三個月(90天)警示標示 ---
        if days_to_jump <= 90:
            st.warning("⚠️ **【重要標示】三個月內即將跳歲！**")
            st.progress(max(0, (90 - days_to_jump) / 90))
            if days_to_jump <= 30:
                st.error(f"‼️ 極緊急：僅剩 {days_to_jump} 天，保費即將隨年齡調漲！")
        else:
            st.success("✅ 目前距離跳歲時間尚充裕，建議按計畫規劃投保。")

        st.info(f"📊 詳細數據：目前實際足歲為 {diff.years} 歲 {diff.months} 個月 {diff.days} 天")



