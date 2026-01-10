import streamlit as st
from datetime import date, datetime, timedelta  # 修正：已加入 timedelta
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
st.title("🛡️ 標準保險年齡計算器")
st.write(f"📅 目前系統日期：{today_tw}")

# --- 第一部分：輸入區 ---
st.subheader("1. 出生日期")
col1, col2, col3 = st.columns(3)
with col1:
    in_y = st.number_input("民國/西元年", min_value=1, max_value=2100, value=109)
with col2:
    in_m = st.number_input("月份", min_value=1, max_value=12, value=9)
with col3:
    in_d = st.number_input("日期", min_value=1, max_value=31, value=12)

# 民國轉西元判定
ad_year = in_y + 1911 if in_y < 1900 else in_y
year_display = f"民國 {in_y} 年" if in_y < 1900 else f"西元 {in_y} 年"

try:
    birth_date = date(ad_year, in_m, in_d)
except ValueError:
    st.error("❌ 日期格式錯誤，請檢查該月份是否有此日期。")
    st.stop()

ref_date = st.date_input("2. 計算基準日", value=today_tw)

# --- 第二部分：核心邏輯計算 ---
if st.button("🚀 開始精確計算"):
    if birth_date > ref_date:
        st.error("出生日期不可晚於基準日！")
    else:
        # A. 計算足歲差距
        diff = relativedelta(ref_date, birth_date)
        
        # B. 保險年齡邏輯：生日後過 6 個月又 1 天即進位
        is_rounded = diff.months > 6 or (diff.months == 6 and diff.days >= 1)
        ins_age = diff.years + 1 if is_rounded else diff.years

        # C. 計算下一個跳歲點 [生日+6個月+1天] 或 [明年生日+1天]
        potential_points = []
        for y in [ref_date.year - 1, ref_date.year, ref_date.year + 1]:
            # 點 1：生日當天 + 1天
            try:
                p_bday = birth_date.replace(year=y) + timedelta(days=1)
                potential_points.append(p_bday)
            except ValueError:
                p_bday = birth_date.replace(year=y, month=3, day=1)
                potential_points.append(p_bday)
                
            # 點 2：生日 + 6個月 + 1天
            try:
                p_half = birth_date.replace(year=y) + relativedelta(months=6) + timedelta(days=1)
                potential_points.append(p_half)
            except ValueError:
                p_half = (birth_date.replace(year=y) + relativedelta(months=6)).replace(day=1) + timedelta(days=1)
                potential_points.append(p_half)
        
        # 找出未來最近的一個點
        upcoming_points = [p for p in potential_points if p > ref_date]
        next_jump = min(upcoming_points)
        days_left = (next_jump - ref_date).days

        # --- 第三部分：顯示結果 ---
        st.divider()
        st.write(f"🎂 出生日期：{year_display} {in_m} 月 {in_d} 日")
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("目前保險年齡", f"{ins_age} 歲")
        with c2:
            # 使用 Markdown 呈現紅色粗體字
            st.write("距離下次跳歲")
            st.markdown(f"<h2 style='color: red; font-weight: bold;'>{days_left} 天</h2>", unsafe_allow_html=True)

        st.subheader("📅 下次跳歲預告")
        roc_j_y = next_jump.year - 1911
        st.success(f"下次跳歲日期：**{next_jump} (民國 {roc_j_y} 年)**")

        # --- 三個月(90天)警示標示 ---
        if days_left <= 90:
            st.warning("⚠️ **特別標示：三個月內即將跳歲！**")
            progress_val = max(0.0, min(1.0, (90 - days_left) / 90.0))
            st.progress(progress_val)
            if days_left <= 30:
                st.error(f"‼️ 極緊急：僅剩 **{days_left}** 天，保費即將隨年齡調漲！")
        else:
            st.info("✅ 目前距離跳歲時間尚充裕。")
        
        st.info(f"📊 詳細數據：目前實際足歲為 {diff.years} 歲 {diff.months} 個月 {diff.days} 天")






