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

# --- 3. 民國年/西元年雙介面 ---
tab_roc, tab_ad = st.tabs(["🇹🇼 民國年輸入", "🌐 西元年輸入"])

with tab_roc:
    c1, c2, c3 = st.columns(3)
    with c1:
        # 民國 68 年測試：68 + 1911 = 1979
        r_y = st.number_input("民國年", min_value=1, max_value=150, value=68)
    with c2:
        r_m = st.number_input("月份 ", min_value=1, max_value=12, value=1)
    with c3:
        r_d = st.number_input("日期 ", min_value=1, max_value=31, value=1)
    # 修正：確保民國 68 年轉換為 1979
    calc_birth_date = date(r_y + 1911, r_m, r_d)

with tab_ad:
    ad_date = st.date_input("請選擇西元生日", value=date(1979, 1, 1))
    # 判斷使用者最後操作的是哪個分頁
    birth_date = ad_date if st.session_state.get('ad_date') else calc_birth_date

# 最終確認 birth_date (以使用者目前所在 tab 為準)
final_birth_date = calc_birth_date if st.session_state.get('roc_y') else birth_date

st.divider()
effective_date = st.date_input("📌 計算基準日 (保單生效日)", value=today_tw)

# --- 4. 核心計算與邏輯顯示 ---
if st.button("🚀 開始計算結果"):
    # 使用正確的 birth_date (修正民國年轉換後的日期)
    target_birth = calc_birth_date 
    
    if target_birth > effective_date:
        st.error("❌ 錯誤：出生日期不能晚於生效日期！")
    else:
        diff = relativedelta(effective_date, target_birth)
        y, m, d = diff.years, diff.months, diff.days
        
        # 保險年齡判定
        if m > 6 or (m == 6 and d >= 1):
            ins_age = y + 1
            logic_text = "（已過半年，進位一歲）"
        else:
            ins_age = y
            logic_text = "（未過半年，維持足歲）"
            
        this_year_bday = target_birth.replace(year=effective_date.year)
        next_jump_date = this_year_bday + relativedelta(months=6, days=1)
        if effective_date >= next_jump_date:
            next_jump_date = (this_year_bday + relativedelta(years=1)) + relativedelta(months=6, days=1)
            
        days_remaining = (next_jump_date - effective_date).days

        st.success(f"## 您的保險年齡：{ins_age} 歲")
        st.write(f"📊 **日期換算確認：**")
        st.write(f"- 出生日期：西元 **{target_birth.year}** 年 {target_birth.month} 月 {target_birth.day} 日")
        st.write(f"- 實際足歲：{y} 歲 {m} 個月 {d} 天")
        
        st.divider()
        if days_remaining <= 30:
            st.error(f"⚠️ **倒數 {days_remaining} 天跳歲！** (預計 {next_jump_date})")
        else:
            st.info(f"✅ 距離下次跳歲還有 **{days_remaining}** 天 (預計 {next_jump_date})。")
