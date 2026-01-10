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

st.title("🛡️ 專業保險年齡計算器 (2026 修正版)")

# 輸入區 (預設為 109/09/12)
col1, col2, col3 = st.columns(3)
with col1:
    in_y = st.number_input("民國/西元年", value=109)
with col2:
    in_m = st.number_input("月", value=9)
with col3:
    in_d = st.number_input("日", value=12)

# 日期轉換
ad_year = in_y + 1911 if in_y < 1900 else in_y
birth_date = date(ad_year, in_m, in_d)
ref_date = st.date_input("基準日", value=today_tw)

# 核心邏輯
diff = relativedelta(ref_date, birth_date)
# 判定保險年齡：過 6 個月又 1 天進位
is_rounded = diff.months > 6 or (diff.months == 6 and diff.days >= 1)
ins_age = diff.years + 1 if is_rounded else diff.years

# 計算下一個跳歲點 [生日+6個月+1天] 或 [明年生日+1天]
# 找出所有可能的跳歲點
p1 = birth_date.replace(year=ref_date.year) + relativedelta(months=6) + timedelta(days=1)
p2 = birth_date.replace(year=ref_date.year) + timedelta(days=1)
p3 = birth_date.replace(year=ref_date.year + 1) + timedelta(days=1)
p4 = birth_date.replace(year=ref_date.year - 1) + relativedelta(months=6) + timedelta(days=1)

# 只抓未來且最近的一個
next_jump = min([p for p in [p1, p2, p3, p4] if p > ref_date])
days_left = (next_jump - ref_date).days

# 顯示結果
st.divider()
st.metric("目前保險年齡", f"{ins_age} 歲")
st.success(f"📅 下一個跳歲日期：{next_jump} (民國 {next_jump.year-1911} 年)")

if days_left <= 90:
    st.warning(f"⚠️ 警示：距離跳歲僅剩 {days_left} 天！")




