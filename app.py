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
        st.info("💡 密碼提示：請輸入預設的三位數字密碼。")
        
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
st.title("🎯 保險年齡快速計算器")
st.caption(f"📅 系統日期：{today_tw}")

# --- 3. 日期輸入邏輯 (修正重點) ---
tab_roc, tab_ad = st.tabs(["🇹🇼 民國年輸入", "🌐 西元年輸入"])

with tab_roc:
    c1, c2, c3 = st.columns(3)
    r_y = c1.number_input("民國年", min_value=1, max_value=150, value=69)
    r_m = c2.number_input("月份", min_value=1, max_value=12, value=7)
    r_d = c3.number_input("日期", min_value=1, max_value=31, value=2)
    # 這裡直接計算出西元日期
    birth_from_roc = date(r_y + 1911, r_m, r_d)

with tab_ad:
    birth_from_ad = st.date_input("請選擇西元生日", value=date(1980, 7, 2))

# 根據目前選取的 Tab 決定最終生日 (預設先看民國 Tab)
# 如果使用者切換到西元 Tab 並點選日期，這裡會自動處理
final_birth_date = birth_from_roc 

# 讓使用者可以手動切換來源 (加一個選項按鈕)
source = st.radio("確認生日來源：", ["使用民國年轉換", "使用西元年選擇"], horizontal=True)
if source == "使用西元年選擇":
    final_birth_date = birth_from_ad

st.divider()
effective_date = st.date_input("📌 計算基準日 (保單生效日)", value=today_tw)

# --- 4. 核心計算 ---
if st.button("🚀 開始計算結果"):
    if final_birth_date > effective_date:
        st.error("❌ 錯誤：出生日期不能晚於生效日期！")
    else:
        # 計算足歲 (y 歲 m 月 d 天)
        diff = relativedelta(effective_date, final_birth_date)
        y, m, d = diff.years, diff.months, diff.days
        
        # 保險年齡判定 (過半年進位)
        if m > 6 or (m == 6 and d >= 1):
            ins_age = y + 1
            logic_text = "已過半年，進位一歲"
        else:
            ins_age = y
            logic_text = "未過半年，維持足歲"
            
        # 跳歲日計算
        this_year_bday = final_birth_date.replace(year=effective_date.year)
        jump_date = this_year_bday + relativedelta(months=6, days=1)
        if effective_date >= jump_date:
            jump_date = (this_year_bday + relativedelta(years=1)) + relativedelta(months=6, days=1)
        days_to_jump = (jump_date - effective_date).days

        # --- 顯示結果 ---
        st.success(f"### 您的保險年齡：{ins_age} 歲")
        st.write(f"📊 **資料核對：**")
        st.write(f"- 西元生日：{final_birth_date} (民國 {final_birth_date.year-1911} 年)")
        st.write(f"- 實際足歲：{y} 歲 {m} 個月 {d} 天")
        st.write(f"- 計算邏輯：{logic_text}")

        st.divider()
        if days_to_jump <= 30:
            st.error(f"⚠️ **緊急預警：剩餘 {days_to_jump} 天跳歲！**")
            st.write(f"將於 **{jump_date}** 變為 {ins_age + 1} 歲")
        else:
            st.info(f"✅ 距離下次跳歲還有 **{days_to_jump}** 天 (預計於 {jump_date})")

with st.sidebar:
    if st.button("登出系統"):
        st.session_state.clear()
        st.rerun()
