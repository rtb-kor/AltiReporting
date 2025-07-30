import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
import os
from modules.data_manager import DataManager
from modules.report_generator import ReportGenerator
from modules.visualization import VisualizationManager
from modules.export_utils import ExportManager

# 페이지 설정
st.set_page_config(
    page_title="RTB 회계 통합 보고서 시스템",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# RTB 브랜드 스타일링
st.markdown("""
<style>
    /* RTB 브랜드 색상 */
    :root {
        --rtb-burgundy: #9C2A4A;
        --rtb-burgundy-light: #B73B5A;
        --rtb-gray: #6B7280;
        --rtb-light-gray: #F3F4F6;
        --rtb-dark-gray: #374151;
    }
    
    /* 전체 앱 스타일 */
    .main .block-container {
        padding-top: 2rem;
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* 제목 스타일 */
    h1 {
        color: var(--rtb-burgundy) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.8rem !important;
        border-bottom: 2px solid var(--rtb-burgundy);
        padding-bottom: 0.5rem;
    }
    
    /* 서브헤더 스타일 */
    h2, h3 {
        color: var(--rtb-dark-gray) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.3rem !important;
    }
    
    /* 보고서 헤더 박스 */
    .report-header {
        background: linear-gradient(135deg, var(--rtb-burgundy), var(--rtb-burgundy-light));
        color: white !important;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .report-header h2,
    .report-header div,
    .report-header strong {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* 메트릭 카드 스타일 */
    .metric-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    /* burgundy 배경 메트릭 카드에서 흰색 텍스트 우선 적용 */
    div[style*="background: linear-gradient(135deg, #9C2A4A"] h2,
    div[style*="background: linear-gradient(135deg, #9C2A4A"] h3,
    div[style*="background: linear-gradient(135deg, #9C2A4A"] h4 {
        color: white !important;
    }
    
    /* 모바일 반응형 - 보고일정 세로 배열 */
    .schedule-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid var(--rtb-burgundy);
    }
    
    .schedule-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #e9ecef;
    }
    
    .schedule-item:last-child {
        border-bottom: none;
    }
    
    @media (max-width: 768px) {
        .schedule-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.25rem;
        }
        
        .schedule-card {
            margin-bottom: 1rem;
        }
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background-color: var(--rtb-burgundy) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: var(--rtb-burgundy-light) !important;
        box-shadow: 0 4px 8px rgba(156, 42, 74, 0.3) !important;
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background-color: var(--rtb-light-gray) !important;
    }
    
    /* 성공/정보 메시지 스타일 */
    .stSuccess {
        background-color: #ECFDF5 !important;
        border-left: 4px solid #10B981 !important;
        color: #065F46 !important;
    }
    
    .stInfo {
        background-color: #EFF6FF !important;
        border-left: 4px solid var(--rtb-burgundy) !important;
        color: var(--rtb-dark-gray) !important;
    }
    
    /* 테이블 스타일 */
    .dataframe {
        font-family: 'Inter', sans-serif !important;
        border-collapse: collapse !important;
    }
    
    .dataframe th {
        background-color: var(--rtb-burgundy) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    
    .dataframe td {
        padding: 0.75rem !important;
        border-bottom: 1px solid #E5E7EB !important;
    }
    
    /* 숫자 강조 스타일 */
    .highlight-number {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--rtb-burgundy);
    }
    
    /* 구분선 스타일 */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, var(--rtb-burgundy), var(--rtb-gray)) !important;
        margin: 2rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'report_generator' not in st.session_state:
    st.session_state.report_generator = ReportGenerator()
if 'viz_manager' not in st.session_state:
    st.session_state.viz_manager = VisualizationManager()
if 'export_manager' not in st.session_state:
    st.session_state.export_manager = ExportManager()

def check_admin_access():
    """관리자 인증 확인"""
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    
    if not st.session_state.is_admin:
        st.sidebar.markdown("### 🔐 관리자 로그인")
        username = st.sidebar.text_input("사용자명")
        password = st.sidebar.text_input("비밀번호", type="password")
        
        if st.sidebar.button("로그인"):
            if username == "김현지" and password == "rtb2025":
                st.session_state.is_admin = True
                st.sidebar.success("관리자 로그인 성공!")
                st.rerun()
            else:
                st.sidebar.error("잘못된 로그인 정보입니다.")
    else:
        st.sidebar.markdown("### 👤 로그인 정보")
        st.sidebar.success("관리자: 김현지")
        if st.sidebar.button("로그아웃"):
            st.session_state.is_admin = False
            st.rerun()
    
    return st.session_state.is_admin

def main():
    # 관리자 인증 확인
    is_admin = check_admin_access()
    
    # 헤더에 로고와 제목 표시
    col1, col2 = st.columns([1, 4])
    
    with col1:
        try:
            st.image("assets/rtb_logo.png", width=100)
        except:
            st.write("🏢")
    
    with col2:
        st.title("RTB 회계 통합 보고서 시스템")
        st.caption("Real-Time Business Accounting Management System")
    
    st.markdown("---")
    
    # 사이드바 메뉴 (관리자 권한에 따라 다르게 표시)
    with st.sidebar:
        st.header("📋 메뉴")
        
        if is_admin:
            menu_options = ["📝 데이터 입력", "📈 월말 보고서", "📊 반기 보고서", "📋 연말 보고서", "⚙️ 설정"]
        else:
            menu_options = ["📈 월말 보고서", "📊 반기 보고서", "📋 연말 보고서"]
        
        menu = st.selectbox(
            "보고서 유형 선택",
            menu_options
        )
        
        st.markdown("---")
        st.subheader("🗓️ 보고 일정")
        
        # 모바일 친화적인 보고일정 카드
        st.markdown('''
        <div class="schedule-card">
            <div class="schedule-item">
                <strong style="color: var(--rtb-burgundy);">월말 보고</strong>
                <span>매월 15일</span>
            </div>
            <div class="schedule-item">
                <strong style="color: var(--rtb-burgundy);">반기 보고</strong>
                <span>7월/1월 15일</span>
            </div>
            <div class="schedule-item">
                <strong style="color: var(--rtb-burgundy);">연말 보고</strong>
                <span>1월 15일</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 현재 날짜 표시
        today = date.today()
        st.markdown(f"**오늘 날짜:** {today.strftime('%Y년 %m월 %d일')}")
    
    # 메뉴별 페이지 라우팅
    if menu == "📝 데이터 입력":
        if is_admin:
            show_data_input()
        else:
            st.error("🔒 관리자만 접근 가능한 메뉴입니다.")
    elif menu == "📈 월말 보고서":
        show_monthly_report()
    elif menu == "📊 반기 보고서":
        show_semi_annual_report()
    elif menu == "📋 연말 보고서":
        show_annual_report()
    elif menu == "⚙️ 설정":
        if is_admin:
            show_settings()
        else:
            st.error("🔒 관리자만 접근 가능한 메뉴입니다.")
    



def show_data_input():
    st.header("📝 데이터 입력")
    
    # 년월 선택
    col_year, col_month = st.columns(2)
    with col_year:
        year = st.selectbox("📅 년도", list(range(2020, 2030)), index=5)
    with col_month:
        month = st.selectbox("📅 월", list(range(1, 13)), index=6)
    
    month_key = f"{year}-{month:02d}"
    st.info(f"**입력 대상: {year}년 {month}월**")
    
    # 기존 데이터 로드
    existing_data = st.session_state.data_manager.get_month_data(month_key)
    
    # 초기화
    if 'revenue_sources' not in st.session_state:
        st.session_state.revenue_sources = {
            'electronic_tax': ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR"],
            'zero_rated': ["Everllence LEO", "Mitsui"],
            'other': ["기타"]
        }
    
    if 'expense_items' not in st.session_state:
        st.session_state.expense_items = ["급여", "수당", "법인카드 사용액", "전자세금계산서", "세금", "이자", "퇴직금", "기타"]
    
    # 안내 메시지
    st.info("**매출처/매입처 수정**: '설정' 메뉴에서 매출처와 매입처를 추가/삭제할 수 있습니다.")
    
    # 매출/매입 입력
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("매출")
        revenue_data = {}
        
        # 전자세금계산서매출
        st.markdown("**전자세금계산서매출**")
        electronic_total = 0
        for source in st.session_state.revenue_sources['electronic_tax']:
            current_value = existing_data.get('매출', {}).get(source, 0)
            value = st.number_input(f"{source}", value=current_value, min_value=0, step=1000000, key=f"electronic_{source}")
            revenue_data[source] = value
            electronic_total += value
        st.info(f"소계: {electronic_total:,}원")
        
        # 영세매출
        st.markdown("**영세매출**")
        zero_total = 0
        for source in st.session_state.revenue_sources['zero_rated']:
            current_value = existing_data.get('매출', {}).get(source, 0)
            value = st.number_input(f"{source}", value=current_value, min_value=0, step=1000000, key=f"zero_{source}")
            if source == "Mitsui" and source in revenue_data:
                revenue_data[source] += value
            else:
                revenue_data[source] = value
            zero_total += value
        st.info(f"소계: {zero_total:,}원")
        
        # 기타 매출
        st.markdown("**기타 매출**")
        current_other = existing_data.get('매출', {}).get("기타", 0)
        other_revenue = st.number_input("기타", value=current_other, min_value=0, step=1000000, key="other_revenue")
        revenue_data["기타"] = other_revenue
        
        total_revenue = sum(revenue_data.values())
        st.markdown(f'<div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid red;"><h4 style="margin: 0;">총 매출: <span style="color: red !important;">{total_revenue:,}원</span></h4></div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("매입")
        expense_data = {}
        
        for item in st.session_state.expense_items:
            current_value = existing_data.get('매입', {}).get(item, 0)
            value = st.number_input(f"{item}", value=current_value, min_value=0, step=100000, key=f"expense_{item}")
            expense_data[item] = value
        
        total_expense = sum(expense_data.values())
        net_profit = total_revenue - total_expense
        st.markdown(f'<div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid blue;"><h4 style="margin: 0;">총 매입: <span style="color: blue !important;">{total_expense:,}원</span></h4></div>', unsafe_allow_html=True)
        profit_color = "red" if net_profit >= 0 else "blue"
        border_color = "red" if net_profit >= 0 else "blue"
        st.markdown(f'<div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid {border_color};"><h4 style="margin: 0;">순이익: <span style="color: {profit_color} !important;">{net_profit:,}원</span></h4></div>', unsafe_allow_html=True)
    
    # 저장 버튼
    st.markdown("---")
    if st.button("데이터 저장", type="primary", use_container_width=True):
        month_data = {
            "매출": revenue_data,
            "매입": expense_data,
            "입력일시": datetime.now().isoformat()
        }
        
        st.session_state.data_manager.save_month_data(month_key, month_data)
        
        # 성공 메시지와 자동 반영 안내
        st.success(f"{year}년 {month}월 데이터가 저장되었습니다!")
        st.info("""
        **자동 집계 시스템 안내**
        - 반기 보고서: 저장한 월별 데이터가 자동으로 상/하반기 집계에 반영됩니다
        - 연말 보고서: 저장한 월별 데이터가 자동으로 연간 집계에 반영됩니다
        - 새로 추가한 매출처/매입처도 자동으로 보고서에 포함됩니다
        """)
        st.rerun()

def show_monthly_report():
    st.header("월말 보고서")
    
    # 년월 선택
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("년도", list(range(2020, 2030)), index=5, key="monthly_year")
    with col2:
        month = st.selectbox("월", list(range(1, 13)), index=6, key="monthly_month")
    
    month_key = f"{year}-{month:02d}"
    data = st.session_state.data_manager.get_month_data(month_key)
    
    if not data:
        st.warning(f"{year}년 {month}월 데이터가 없습니다. 먼저 데이터를 입력해주세요.")
        return
    
    # 보고서 생성
    report = st.session_state.report_generator.generate_monthly_report(year, month, data)
    
    st.markdown("---")
    
    # 보고서 헤더
    # 보고일 계산 (다음 달 15일)
    if month == 12:
        report_year = year + 1
        report_month = 1
    else:
        report_year = year
        report_month = month + 1
    
    st.markdown(f"""
    <div class="report-header">
        <h2 style="color: white !important; margin: 0; font-size: 1.6rem; font-family: 'Inter', sans-serif; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">RTB {year}년 월말보고</h2>
        <div style="margin-top: 1rem; font-size: 1rem; color: white !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.7);">
            <strong>보고일:</strong> {report_year}년 {report_month:02d}월 15일 &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>작성자:</strong> RTB 회계팀
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 요약 테이블
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("매출 현황")
        
        # 전자세금계산서매출 카드
        electronic_tax_sources = ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR"]
        electronic_total = 0
        electronic_items = []
        
        for source in electronic_tax_sources:
            amount = data['매출'].get(source, 0)
            if amount > 0:  # 0원이 아닌 경우만 표시
                electronic_items.append(f'<div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid #e9ecef;"><span>{source}</span><span style="font-weight: 600;">{amount:,}원</span></div>')
                electronic_total += amount
        
        electronic_content = ''.join(electronic_items) if electronic_items else '<div style="text-align: center; color: #6c757d;">데이터 없음</div>'
        
        st.markdown(f'''
        <div style="background: #f8f9fa; padding: 1.2rem; border-radius: 8px; border-left: 4px solid #6c757d; margin-bottom: 1rem;">
            <h4 style="margin: 0 0 1rem 0; color: #2c3e50; font-weight: 600;">전자세금계산서매출</h4>
            <div style="background: white; padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
                {electronic_content}
            </div>
            <div style="text-align: right; font-size: 1.3rem; font-weight: 700; padding: 0.5rem; background: #fff; border-radius: 6px; border: 2px solid #6c757d;">
                <span>소계: {electronic_total:,}원</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 영세매출 카드
        zero_rated_sources = ["Everllence LEO", "Mitsui"]
        zero_total = 0
        zero_items = []
        
        for source in zero_rated_sources:
            amount = data['매출'].get(source, 0)
            if amount > 0:  # 0원이 아닌 경우만 표시
                zero_items.append(f'<div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid #e9ecef;"><span>{source}</span><span style="font-weight: 600;">{amount:,}원</span></div>')
                zero_total += amount
        
        zero_content = ''.join(zero_items) if zero_items else '<div style="text-align: center; color: #6c757d;">데이터 없음</div>'
        
        st.markdown(f'''
        <div style="background: #f8f9fa; padding: 1.2rem; border-radius: 8px; border-left: 4px solid #6c757d; margin-bottom: 1rem;">
            <h4 style="margin: 0 0 1rem 0; color: #2c3e50; font-weight: 600;">영세매출</h4>
            <div style="background: white; padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
                {zero_content}
            </div>
            <div style="text-align: right; font-size: 1.3rem; font-weight: 700; padding: 0.5rem; background: #fff; border-radius: 6px; border: 2px solid #6c757d;">
                <span>소계: {zero_total:,}원</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 기타매출 카드
        other_amount = data['매출'].get("기타", 0)
        other_content = f'<div style="display: flex; justify-content: space-between; padding: 0.3rem 0;"><span>기타</span><span style="font-weight: 600;">{other_amount:,}원</span></div>' if other_amount > 0 else '<div style="text-align: center; color: #6c757d;">데이터 없음</div>'
        
        st.markdown(f'''
        <div style="background: #f8f9fa; padding: 1.2rem; border-radius: 8px; border-left: 4px solid #6c757d; margin-bottom: 1rem;">
            <h4 style="margin: 0 0 1rem 0; color: #2c3e50; font-weight: 600;">기타매출</h4>
            <div style="background: white; padding: 1rem; border-radius: 6px;">
                {other_content}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 매출 총계
        total_revenue = sum(data['매출'].values())
        st.markdown(f'''
        <div style="background: white; border: 2px solid #e9ecef; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
            <h3 style="margin: 0; text-align: center; font-size: 1.4rem; font-weight: 700;">
                매출 총계: <span style="color: red;">{total_revenue:,}원</span>
            </h3>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.subheader("매입 현황")
        
        # 매입 항목별 카드
        expense_items = []
        for item, amount in data['매입'].items():
            if amount > 0:  # 0원이 아닌 경우만 표시
                expense_items.append(f'<div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid #e9ecef;"><span>{item}</span><span style="font-weight: 600;">{amount:,}원</span></div>')
        
        expense_content = ''.join(expense_items) if expense_items else '<div style="text-align: center; color: #6c757d;">데이터 없음</div>'
        
        st.markdown(f'''
        <div style="background: #f8f9fa; padding: 1.2rem; border-radius: 8px; border-left: 4px solid #6c757d; margin-bottom: 1rem;">
            <h4 style="margin: 0 0 1rem 0; color: #2c3e50; font-weight: 600;">매입 항목</h4>
            <div style="background: white; padding: 1rem; border-radius: 6px;">
                {expense_content}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 매입 총계
        total_expense = sum(data['매입'].values())
        st.markdown(f'''
        <div style="background: white; border: 2px solid #e9ecef; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
            <h3 style="margin: 0; text-align: center; font-size: 1.4rem; font-weight: 700;">
                매입 총계: <span style="color: blue;">{total_expense:,}원</span>
            </h3>
        </div>
        ''', unsafe_allow_html=True)
    
    # 순이익 계산
    net_profit = total_revenue - total_expense
    st.markdown("---")
    profit_color = "red" if net_profit >= 0 else "blue"
    st.markdown(f'<div class="metric-card"><h3 style="margin: 0;">순이익: <span style="color: {profit_color} !important;">{net_profit:,}원</span></h3></div>', unsafe_allow_html=True)
    
    # 시각화
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("매출처별 분포")
        pie_chart = st.session_state.viz_manager.create_revenue_pie_chart(data['매출'])
        st.plotly_chart(pie_chart, use_container_width=True)
    
    with col2:
        st.subheader("매입 항목별 분포")
        expense_pie = st.session_state.viz_manager.create_expense_pie_chart(data['매입'])
        st.plotly_chart(expense_pie, use_container_width=True)
    
    # 내보내기 버튼
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("PDF 다운로드"):
            pdf_file = st.session_state.export_manager.generate_pdf_report(report, f"RTB_{year}년_{month}월_월말보고서")
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="PDF 파일 다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_{month}월_월말보고서.pdf",
                    mime="application/pdf"
                )
    
    with col2:
        if st.button("Excel 다운로드"):
            excel_file = st.session_state.export_manager.generate_excel_report(data, f"RTB_{year}년_{month}월_월말보고서")
            with open(excel_file, "rb") as file:
                st.download_button(
                    label="Excel 파일 다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_{month}월_월말보고서.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

def show_semi_annual_report():
    st.header("반기 보고서")
    
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("년도", list(range(2020, 2030)), index=5, key="semi_year")
    with col2:
        period = st.selectbox("기간", ["상반기 (1-6월)", "하반기 (7-12월)"], key="semi_period")
    
    # 기간 설정
    if "상반기" in period:
        months = list(range(1, 7))
        period_name = "상반기"
    else:
        months = list(range(7, 13))
        period_name = "하반기"
    
    # 데이터 수집 및 집계
    all_data = st.session_state.data_manager.get_all_data()
    period_data = {}
    
    for month in months:
        month_key = f"{year}-{month:02d}"
        if month_key in all_data:
            period_data[month_key] = all_data[month_key]
    
    if not period_data:
        st.warning(f"{year}년 {period_name} 데이터가 없습니다.")
        st.info("**데이터 입력 안내**: '데이터 입력' 메뉴에서 월별 데이터를 입력하면 자동으로 반기 보고서에 반영됩니다.")
        return
    
    # 반기 집계
    semi_annual_summary = st.session_state.data_manager.aggregate_period_data(period_data)
    
    st.markdown("---")
    
    # 보고서 헤더
    st.markdown(f"""
    <div class="report-header">
        <h2 style="color: white !important; margin: 0; font-size: 1.6rem; font-family: 'Inter', sans-serif; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">RTB {year}년 {period_name} 보고서</h2>
        <div style="margin-top: 1rem; font-size: 1rem; color: white !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.7);">
            <strong>작성일:</strong> {datetime.now().strftime('%Y년 %m월 %d일')} &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>보고기간:</strong> {year}년 {months[0]}월 ~ {months[-1]}월 &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>작성자:</strong> RTB 회계팀
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 요약 정보
    col1, col2, col3 = st.columns(3)
    
    total_revenue = sum(semi_annual_summary['매출'].values())
    total_expense = sum(semi_annual_summary['매입'].values())
    net_profit = total_revenue - total_expense
    
    with col1:
        st.markdown(f'<div class="metric-card"><h3 style="margin: 0;">{period_name} 총 매출<br><span style="color: red !important;">{total_revenue:,}원</span></h3></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3 style="margin: 0;">{period_name} 총 매입<br><span style="color: blue !important;">{total_expense:,}원</span></h3></div>', unsafe_allow_html=True)
    with col3:
        profit_color = "red" if net_profit >= 0 else "blue"
        st.markdown(f'<div class="metric-card"><h3 style="margin: 0;">{period_name} 순이익<br><span style="color: {profit_color} !important;">{net_profit:,}원</span></h3></div>', unsafe_allow_html=True)
    
    # 상세 분석
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("매출처별 집계")
        revenue_df = pd.DataFrame(list(semi_annual_summary['매출'].items()))
        revenue_df.columns = ['매출처', '금액(원)']
        revenue_df['금액(원)'] = revenue_df['금액(원)'].apply(lambda x: f"{x:,}")
        st.dataframe(revenue_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("매입 항목별 집계")
        expense_df = pd.DataFrame(list(semi_annual_summary['매입'].items()))
        expense_df.columns = ['항목', '금액(원)']
        expense_df['금액(원)'] = expense_df['금액(원)'].apply(lambda x: f"{x:,}")
        st.dataframe(expense_df, hide_index=True, use_container_width=True)
    
    # 내보내기
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("PDF 다운로드", key="semi_pdf"):
            report_data = {
                'period': f"{year}년 {period_name}",
                'summary': semi_annual_summary,
                'months_data': period_data
            }
            pdf_file = st.session_state.export_manager.generate_pdf_report(report_data, f"RTB_{year}년_{period_name}_보고서")
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="PDF 파일 다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_{period_name}_보고서.pdf",
                    mime="application/pdf",
                    key="semi_pdf_download"
                )

def show_annual_report():
    st.header("연말 보고서")
    
    year = st.selectbox("년도", list(range(2020, 2030)), index=5, key="annual_year")
    
    # 연간 데이터 수집
    all_data = st.session_state.data_manager.get_all_data()
    annual_data = {}
    
    for month in range(1, 13):
        month_key = f"{year}-{month:02d}"
        if month_key in all_data:
            annual_data[month_key] = all_data[month_key]
    
    if not annual_data:
        st.warning(f"{year}년 데이터가 없습니다.")
        st.info("**데이터 입력 안내**: '데이터 입력' 메뉴에서 월별 데이터를 입력하면 자동으로 연말 보고서에 반영됩니다.")
        return
    
    # 연간 집계
    annual_summary = st.session_state.data_manager.aggregate_period_data(annual_data)
    
    st.markdown("---")
    
    # 보고서 헤더
    st.markdown(f"""
    <div class="report-header">
        <h2 style="color: white !important; margin: 0; font-size: 1.6rem; font-family: 'Inter', sans-serif; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">RTB {year}년 연말 보고서</h2>
        <div style="margin-top: 1rem; font-size: 1rem; color: white !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.7);">
            <strong>작성일:</strong> {datetime.now().strftime('%Y년 %m월 %d일')} &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>보고기간:</strong> {year}년 전체 &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>작성자:</strong> RTB 회계팀
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 핵심 지표 (큰 숫자로 강조)
    total_revenue = sum(annual_summary['매출'].values())
    total_expense = sum(annual_summary['매입'].values())
    net_profit = total_revenue - total_expense
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'<div class="metric-card"><h3 style="margin: 0;">연간 총 매출<br><span style="color: red !important;">{total_revenue:,}원</span></h3></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="metric-card"><h3 style="margin: 0;">연간 총 매입<br><span style="color: blue !important;">{total_expense:,}원</span></h3></div>', unsafe_allow_html=True)
    
    with col3:
        profit_color = "red" if net_profit >= 0 else "blue"
        st.markdown(f'<div class="metric-card"><h3 style="margin: 0;">연간 순이익<br><span style="color: {profit_color} !important;">{net_profit:,}원</span></h3></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 매출/매입 비교 분석
    st.subheader("매출 vs 매입 비교")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 매출 세부 내역")
        
        # 전자세금계산서매출 소계
        electronic_sources = ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR"]
        electronic_total = sum(annual_summary['매출'].get(source, 0) for source in electronic_sources)
        
        # 영세매출 소계
        zero_sources = ["Everllence LEO", "Mitsui"]
        zero_total = sum(annual_summary['매출'].get(source, 0) for source in zero_sources)
        
        # 기타매출
        other_total = annual_summary['매출'].get("기타", 0)
        
        revenue_summary = {
            "전자세금계산서매출": electronic_total,
            "영세매출": zero_total,
            "기타매출": other_total
        }
        
        # 매출 구성 표
        revenue_df = pd.DataFrame(list(revenue_summary.items()))
        revenue_df.columns = ['구분', '금액']
        revenue_df['금액'] = revenue_df['금액'].apply(lambda x: f"{x:,}원")
        revenue_df['비율'] = [f"{(v/total_revenue*100):.1f}%" for v in revenue_summary.values()]
        st.dataframe(revenue_df, hide_index=True, use_container_width=True)
        
        # 매출 파이차트
        revenue_pie = st.session_state.viz_manager.create_revenue_summary_pie_chart(revenue_summary)
        st.plotly_chart(revenue_pie, use_container_width=True)
    
    with col2:
        st.markdown("#### 매입 세부 내역")
        
        # 매입 구성 표
        expense_df = pd.DataFrame(list(annual_summary['매입'].items()))
        expense_df.columns = ['항목', '금액']
        expense_df['금액'] = expense_df['금액'].apply(lambda x: f"{x:,}원")
        expense_df['비율'] = [f"{(v/total_expense*100):.1f}%" for v in annual_summary['매입'].values()]
        st.dataframe(expense_df, hide_index=True, use_container_width=True)
        
        # 매입 파이차트
        expense_pie = st.session_state.viz_manager.create_expense_pie_chart(annual_summary['매입'])
        st.plotly_chart(expense_pie, use_container_width=True)
    
    st.markdown("---")
    
    # 매출 vs 매입 비교 차트
    st.subheader("매출 vs 매입 총액 비교")
    comparison_chart = st.session_state.viz_manager.create_revenue_expense_comparison_chart(total_revenue, total_expense, net_profit)
    st.plotly_chart(comparison_chart, use_container_width=True)
    
    # 내보내기 버튼
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("PDF 다운로드", key="annual_pdf"):
            report_data = {
                'period': f"{year}년",
                'summary': annual_summary,
                'total_revenue': total_revenue,
                'total_expense': total_expense,
                'net_profit': net_profit,
                'revenue_summary': revenue_summary
            }
            pdf_file = st.session_state.export_manager.generate_pdf_report(report_data, f"RTB_{year}년_연말보고서")
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="PDF 파일 다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_연말보고서.pdf",
                    mime="application/pdf",
                    key="annual_pdf_download"
                )
    
    with col2:
        if st.button("Excel 다운로드", key="annual_excel"):
            excel_file = st.session_state.export_manager.generate_excel_report(annual_summary, f"RTB_{year}년_연말보고서")
            with open(excel_file, "rb") as file:
                st.download_button(
                    label="Excel 파일 다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_연말보고서.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="annual_excel_download"
                )

def show_settings():
    st.header("시스템 설정")
    
    # 탭으로 설정 메뉴 구분
    tab1, tab2, tab3 = st.tabs(["매출처/매입처 관리", "데이터 관리", "시스템 정보"])
    
    with tab1:
        st.subheader("매출처 및 매입처 관리")
        
        # 매출처 관리
        st.markdown("#### 매출처 관리")
        
        # 세션 상태에 매출처 정보가 없으면 기본값 설정
        if 'revenue_sources' not in st.session_state:
            st.session_state.revenue_sources = {
                'electronic_tax': ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR"],
                'zero_rated': ["Everllence LEO", "Mitsui"],
                'other': ["기타"]
            }
        
        # 전자세금계산서매출
        st.markdown("**전자세금계산서매출**")
        electronic_tax_sources = st.session_state.revenue_sources['electronic_tax']
        
        col1, col2 = st.columns([3, 1])
        with col1:
            new_electronic_source = st.text_input("새 전자세금계산서매출처 추가", key="new_electronic")
        with col2:
            if st.button("추가", key="add_electronic"):
                if new_electronic_source and new_electronic_source not in electronic_tax_sources:
                    st.session_state.revenue_sources['electronic_tax'].append(new_electronic_source)
                    st.success(f"'{new_electronic_source}' 추가됨")
                    st.rerun()
        
        # 기존 전자세금계산서매출처 수정/삭제
        for i, source in enumerate(electronic_tax_sources):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_name = st.text_input(f"", value=source, key=f"edit_electronic_{i}")
            with col2:
                if st.button("수정", key=f"update_electronic_{i}"):
                    if new_name != source:
                        st.session_state.revenue_sources['electronic_tax'][i] = new_name
                        st.success(f"'{source}' → '{new_name}' 변경됨")
                        st.rerun()
            with col3:
                if st.button("삭제", key=f"delete_electronic_{i}"):
                    st.session_state.revenue_sources['electronic_tax'].remove(source)
                    st.success(f"'{source}' 삭제됨")
                    st.rerun()
        
        st.markdown("---")
        
        # 영세매출
        st.markdown("**영세매출**")
        zero_rated_sources = st.session_state.revenue_sources['zero_rated']
        
        col1, col2 = st.columns([3, 1])
        with col1:
            new_zero_source = st.text_input("새 영세매출처 추가", key="new_zero")
        with col2:
            if st.button("추가", key="add_zero"):
                if new_zero_source and new_zero_source not in zero_rated_sources:
                    st.session_state.revenue_sources['zero_rated'].append(new_zero_source)
                    st.success(f"'{new_zero_source}' 추가됨")
                    st.rerun()
        
        # 기존 영세매출처 수정/삭제
        for i, source in enumerate(zero_rated_sources):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_name = st.text_input(f"", value=source, key=f"edit_zero_{i}")
            with col2:
                if st.button("수정", key=f"update_zero_{i}"):
                    if new_name != source:
                        st.session_state.revenue_sources['zero_rated'][i] = new_name
                        st.success(f"'{source}' → '{new_name}' 변경됨")
                        st.rerun()
            with col3:
                if st.button("삭제", key=f"delete_zero_{i}"):
                    st.session_state.revenue_sources['zero_rated'].remove(source)
                    st.success(f"'{source}' 삭제됨")
                    st.rerun()
        
        st.markdown("---")
        
        # 매입처 관리
        st.markdown("#### 매입 항목 관리")
        
        # 세션 상태에 매입 항목이 없으면 기본값 설정
        if 'expense_items' not in st.session_state:
            st.session_state.expense_items = ["급여", "수당", "법인카드 사용액", "전자세금계산서", "세금", "이자", "퇴직금", "기타"]
        
        expense_items = st.session_state.expense_items
        
        col1, col2 = st.columns([3, 1])
        with col1:
            new_expense_item = st.text_input("새 매입 항목 추가", key="new_expense")
        with col2:
            if st.button("추가", key="add_expense"):
                if new_expense_item and new_expense_item not in expense_items:
                    st.session_state.expense_items.append(new_expense_item)
                    st.success(f"'{new_expense_item}' 추가됨")
                    st.rerun()
        
        # 기존 매입 항목 수정/삭제
        for i, item in enumerate(expense_items):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_name = st.text_input(f"", value=item, key=f"edit_expense_{i}")
            with col2:
                if st.button("수정", key=f"update_expense_{i}"):
                    if new_name != item:
                        st.session_state.expense_items[i] = new_name
                        st.success(f"'{item}' → '{new_name}' 변경됨")
                        st.rerun()
            with col3:
                if st.button("삭제", key=f"delete_expense_{i}"):
                    st.session_state.expense_items.remove(item)
                    st.success(f"'{item}' 삭제됨")
                    st.rerun()
        
        st.markdown("---")
        st.warning("⚠️ 매출처나 매입처를 변경하면 기존 데이터와 일치하지 않을 수 있습니다. 변경 전 데이터를 백업하는 것을 권장합니다.")
    
    with tab2:
        st.subheader("📊 데이터 관리")
        
        # 데이터 백업
        if st.button("💾 데이터 백업"):
            backup_file = st.session_state.data_manager.backup_data()
            st.success(f"✅ 데이터가 백업되었습니다: {backup_file}")
        
        # 데이터 복원
        uploaded_file = st.file_uploader("📥 백업 파일 업로드", type=['json'])
        if uploaded_file is not None:
            if st.button("🔄 데이터 복원"):
                try:
                    backup_data = json.load(uploaded_file)
                    st.session_state.data_manager.restore_data(backup_data)
                    st.success("✅ 데이터가 복원되었습니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 복원 실패: {str(e)}")
    
    with tab3:
        # 시스템 정보
        st.subheader("ℹ️ 시스템 정보")
        st.info("""
        **RTB 회계 통합 보고서 시스템 v1.0**
        
        • 개발: RTB 회계팀
        • 기능: 월말/반기/연말 보고서 자동 생성
        • 지원: 매출처별 분석, PDF/Excel 내보내기
        • 업데이트: 2025년 7월
        """)

if __name__ == "__main__":
    main()
