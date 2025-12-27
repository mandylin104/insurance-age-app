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
st.set_page_config(page_title="保險年齡快速計算器", page_icon="🛡️")

# --- 3. 輸入介面 ---
st.title("🎯 保險年齡快速計算器")
st.caption(f"📅 台北時間：{today_tw}")

# 民國/西元輸入
tab_roc, tab_ad = st.tabs(["🇹🇼 民國年輸入", "🌐 西元年輸入"])
with tab_roc:
    c1, c2, c3 = st.columns(3)
    r_y = c1.number_input("民國", 1, 150, 69)
    r_m = c2.number_input("月", 1, 12, 7)
    r_d = c3.number_input("日", 1, 31, 2)
    birth_roc = date(r_y + 1911, r_m, r_d)
with tab_ad:
    birth_ad = st.date_input("選擇西元生日", value=date(1980, 7, 2))

source = st.radio("請確認生日來源：", ["民國年", "西元年"], horizontal=True)
final_birth = birth_ad if source == "西元年" else birth_roc

st.divider()
effective_date = st.date_input("📌 計算基準日 (生效日)", value=today_tw)

# --- 4. 計算與顯示 (強制排序結構) ---
if st.button("🚀 開始計算"):
    if final_birth > effective_date:
        st.error("❌ 出生日期不得晚於基準日")
    else:
        # 計算
        diff = relativedelta(effective_date, final_birth)
        y, m, d = diff.years, diff.months, diff.days
        ins_age = y + 1 if (m > 6 or (m == 6 and d >= 1)) else y
        
        # 跳歲日
        this_year_bday = final_birth.replace(year=effective_date.year)
        jump_date = this_year_bday + relativedelta(months=6, days=1)
        if effective_date >= jump_date:
            jump_date = (this_year_bday + relativedelta(years=1)) + relativedelta(months=6, days=1)
        days_to_jump = (jump_date - effective_date).days

        # === 重點：強制順序顯示區 ===
        # 使用一個大的綠色框包住所有最重要的資訊
        st.success(f"## 您的保險年齡：{ins_age} 歲")
        
        # 立即顯示警示 (絕對在年齡下方)
        if days_to_jump <= 30:
            st.error(f"🚨 **緊急預警：剩餘 {days_to_jump} 天跳歲！**")
            st.subheader(f"將於 {jump_date} 變為 {ins_age + 1} 歲")
        elif days_to_jump <= 90:
            st.warning(f"⚠️ **跳歲提醒：剩餘 {days_to_jump} 天 (預計於 {jump_date} 加歲)**")
        else:
            st.info(f"✅ 距離下次跳歲還有 {days_to_jump} 天 (預計於 {jump_date})")
        
        # 最後顯示輔助資料
        st.divider()
        st.markdown(f"**詳細核對：**")
        st.write(f"🔹 生日：{final_birth} (民國 {final_birth.year-1911} 年)")
        st.write(f"🔹 足歲：{y} 歲 {m} 個月 {d} 天")

# 側邊欄
with st.sidebar:
    if st.button("登出"):
        st.session_state.clear()
        st.rerun()


