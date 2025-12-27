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
            st.warning("🆘 終極提示：密碼是欣台光復地址號碼+樓層共3位數 (即 357)。")
        else:
            st.error("❌ 密碼錯誤，請重新輸入。")
            st.info("💡 提示：密碼與「欣台地址+樓層」的數字。")
            
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

# --- 2. 時區設定 (確保今天日期與台灣同步) ---
tw_tz = pytz.timezone('Asia/Taipei')
today_tw = datetime.now(tw_tz).date()

# --- 3. 網頁介面佈局 ---
st.set_page_config(page_title="專業保險年齡計算器", page_icon="🛡️")

st.title("🎯 保險年齡快速計算器")
st.caption(f"📅 系統當前日期 (台北時區)：{today_tw}")

# 使用分頁區隔民國與西元輸入
tab_roc, tab_ad = st.tabs(["🇹🇼 民國年輸入", "🌐 西元年輸入"])

with tab_roc:
    c1, c2, c3 = st.columns(3)
    with c1:
        r_y = st.number_input("民國年", min_value=1, max_value=150, value=80)
    with c2:
        r_m = st.number_input("月 ", min_value=1, max_value=12, value=1)
    with c3:
        r_d = st.number_input("日 ", min_value=1, max_value=31, value=1)
    # 民國轉西元
    birth_date = date(r_y + 1911, r_m, r_d)

with tab_ad:
    ad_date = st.date_input("請選擇西元生日", value=date(1991, 1, 1))
    # 若在西元分頁有異動，則以此為準
    if ad_date:
        birth_date = ad_date

st.divider()
effective_date = st.date_input("📌 計算基準日 (保單生效日)", value=today_tw)

# --- 4. 核心計算邏輯 ---
if st.button("🚀 開始計算結果"):
    if birth_date > effective_date:
        st.error("❌ 錯誤：出生日期不能晚於生效日期！")
    else:
        # 計算實際差距
        diff = relativedelta(effective_date, birth_date)
        y, m, d = diff.years, diff.months, diff.days
        
        # 保險年齡判定 (半年進位法)
        # 規則：超過 6 個月又 1 天即進位
        if m > 6 or (m == 6 and d >= 1):
            ins_age = y + 1
            logic_text = "（已過半年，進位一歲）"
        else:
            ins_age = y
            logic_text = "（未過半年，維持足歲）"
            
        # 計算下一次跳歲日 (生日月 + 6個月 + 1天)
        # 例如 1月1日生，跳歲日為 7月2日
        this_year_bday = birth_date.replace(year=effective_date.year)
        potential_jump_date = this_year_bday + relativedelta(months=6, days=1)
        
        if effective_date >= potential_jump_date:
            next_jump_date = (this_year_bday + relativedelta(years=1)) + relativedelta(months=6, days=1)
        else:
            next_jump_date = potential_jump_date
            
        days_remaining = (next_jump_date - effective_date).days

        # --- 5. 結果呈現 ---
        st.success(f"## 您的保險年齡：{ins_age} 歲")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("實際足歲", f"{y} 歲")
            st.write(f"出生日期: {birth_date}")
        with col_res2:
            st.metric("距生日餘數", f"{m}月{d}天")
            st.write(f"計算邏輯: {logic_text}")

        st.divider()
        
        # 跳歲預警警示
        if days_remaining <= 30:
            st.error(f"⚠️ **緊急警告：倒數 {days_remaining} 天跳歲！**")
            st.write(f"您的保險年齡即將在 **{next_jump_date}** 增加為 **{ins_age + 1} 歲**，屆時保費將會調整，請把握時間投保！")
        elif days_remaining <= 90:
            st.warning(f"🔔 **跳歲提醒：** 距離下次保險跳歲還有 **{days_remaining}** 天。")
        else:
            st.info(f"✅ **時程穩定：** 距離下次跳歲還有 **{days_remaining}** 天 (預計 {next_jump_date})。")

# 側邊欄：登出功能
with st.sidebar:
    st.title("系統控制")
    if st.button("登出並鎖定"):
        st.session_state.clear()
        st.rerun()
