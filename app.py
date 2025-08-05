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
    page_title="RTB 회계 통합 보고서",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# RTB 브랜드 스타일링
st.markdown("""
<style>
    /* RTB 브랜드 색상 */
    :root {
        --rtb-burgundy: #B8344F;
        --rtb-burgundy-light: #D32F4A;
        --rtb-gray: #6B7280;
        --rtb-light-gray: #F3F4F6;
        --rtb-dark-gray: #374151;
    }
    
    /* 전체 앱 스타일 - 안전한 DOM 조작 */
    .main .block-container {
        padding-top: 0.5rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
        max-width: 100%;
    }
    
    /* Streamlit DOM 안정성 개선 */
    .stApp {
        overflow-x: hidden;
    }
    
    /* 안전한 요소 선택자 */
    div[data-testid="stAppViewContainer"] {
        background-color: #fafafa;
    }
    
    /* 제목 스타일 */
    h1 {
        color: var(--rtb-burgundy) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.4rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* 캡션 스타일 - 안전한 선택자 */
    [data-testid="caption"] {
        font-size: 0.8rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 서브헤더 스타일 */
    h2, h3 {
        color: var(--rtb-dark-gray) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 보고서 헤더 박스 */
    .report-header {
        background: linear-gradient(135deg, var(--rtb-burgundy), var(--rtb-burgundy-light));
        color: white !important;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
        border-radius: 6px;
        padding: 0.8rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 0.8rem;
    }
    
    /* burgundy 배경 메트릭 카드에서 흰색 텍스트 우선 적용 - 안전한 선택자 */
    div[style*="background: linear-gradient(135deg, #9C2A4A"] h2,
    div[style*="background: linear-gradient(135deg, #9C2A4A"] h3,
    div[style*="background: linear-gradient(135deg, #9C2A4A"] h4 {
        color: white !important;
    }
    
    /* DOM 안정성 개선 */
    .element-container {
        position: relative;
    }
    
    /* 안전한 애니메이션 */
    * {
        transition: none !important;
    }
    
    /* JavaScript 오류 방지 */
    <script>
    // DOM 조작 오류 방지
    window.addEventListener('error', function(e) {
        if (e.message.includes('removeChild') || e.message.includes('Node')) {
            e.preventDefault();
            return false;
        }
    });
    
    // Streamlit DOM 안정성 개선
    document.addEventListener('DOMContentLoaded', function() {
        // 안전한 DOM 조작
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    // DOM 변경 감지시 안전하게 처리
                    try {
                        // 필요한 경우에만 DOM 조작
                    } catch (error) {
                        console.warn('DOM 조작 오류 무시:', error);
                    }
                }
            });
        });
        
        // DOM 변경 감지 시작
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
    </script>
    
    /* 연말 보고서 헤더 강제 흰색 적용 */
    .annual-report-header h2,
    .annual-report-header div,
    .annual-report-header strong,
    .annual-report-header span {
        color: white !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5) !important;
    }
    
    /* 월말 보고서 헤더 강제 흰색 적용 */
    .monthly-report-header h2,
    .monthly-report-header div,
    .monthly-report-header strong,
    .monthly-report-header span {
        color: white !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5) !important;
    }
    
    /* 반기 보고서 헤더 강제 흰색 적용 */
    .semi-annual-report-header h2,
    .semi-annual-report-header div,
    .semi-annual-report-header strong,
    .semi-annual-report-header span {
        color: white !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5) !important;
    }
    
    /* 업체별 매출변동 비교 헤더 강제 흰색 적용 */
    .revenue-trend-header h2,
    .revenue-trend-header div,
    .revenue-trend-header strong,
    .revenue-trend-header span {
        color: white !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5) !important;
    }
    
    /* 모바일 반응형 - 보고일정 세로 배열 */
    .schedule-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
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
    
    /* 모바일 전용 스타일 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.25rem !important;
        }
        
        .schedule-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.25rem;
            font-size: 0.85rem;
        }
        
        .schedule-card {
            margin-bottom: 0.8rem;
            padding: 0.8rem;
        }
        
        /* 테이블 모바일 최적화 */
        .dataframe {
            font-size: 0.8rem !important;
        }
        
        .dataframe th, .dataframe td {
            padding: 0.4rem !important;
        }
        
        /* 헤더 컴팩트 */
        .monthly-report-header, .semi-annual-report-header, .annual-report-header {
            padding: 0.8rem !important;
            margin-bottom: 0.8rem !important;
        }
        
        .monthly-report-header h2, .semi-annual-report-header h2, .annual-report-header h2 {
            font-size: 1.1rem !important;
        }
        
        .monthly-report-header div, .semi-annual-report-header div, .annual-report-header div {
            font-size: 0.75rem !important;
        }
        
        /* 차트 컨테이너 높이 조정 */
        .js-plotly-plot {
            height: 300px !important;
        }
        
        /* 선택박스 폰트 크기 */
        .stSelectbox label {
            font-size: 0.9rem !important;
        }
        
        /* 입력 폼 컴팩트 */
        .stNumberInput label {
            font-size: 0.85rem !important;
        }
        
        /* 모바일용 컬럼 스택 */
        .row-widget.stHorizontal {
            flex-direction: column !important;
        }
        
        /* 매출/매입 카드 모바일 최적화 */
        .metric-card h4 {
            font-size: 1rem !important;
        }
        
        .metric-card div {
            font-size: 0.8rem !important;
        }
        
        /* 사이드바 모바일 최적화 */
        .css-1d391kg {
            padding: 0.5rem !important;
        }
        
        .stSelectbox > div > div {
            font-size: 0.85rem !important;
        }
        
        /* 다운로드 버튼 컴팩트 */
        .stButton > button {
            height: 2.2rem !important;
            font-size: 0.8rem !important;
            padding: 0.3rem 0.8rem !important;
        }
        
        .stDownloadButton > button {
            height: 2rem !important;
            font-size: 0.75rem !important;
            padding: 0.25rem 0.6rem !important;
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
        font-size: 0.9rem !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
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
    
    # 안전한 헤더 표시 (JavaScript 오류 방지)
    try:
        # 헤더에 로고와 제목 표시 (모바일 최적화)
        col1, col2 = st.columns([1, 5])
        
        with col1:
            try:
                st.image("assets/rtb_logo.png", width=60)
            except:
                st.markdown("🏢")
        
        with col2:
            st.title("RTB 회계 통합 보고서")
            st.caption("실시간 기업회계관리 시스템")
    except Exception as e:
        # 오류 발생시 간단한 헤더로 대체
        st.title("RTB 회계 통합 보고서")
        st.caption("실시간 기업회계관리 시스템")
    
    st.markdown('<div style="margin: 0.5rem 0;"></div>', unsafe_allow_html=True)
    
    # 사이드바 메뉴 (관리자 권한에 따라 다르게 표시)
    with st.sidebar:
        st.header("📋 메뉴")
        
        try:
            if is_admin:
                menu_options = ["📝 데이터 입력", "📈 월말 보고서", "📊 반기 보고서", "📋 연말 보고서", "📈 업체별 매출변동 비교", "⚙️ 설정"]
            else:
                menu_options = ["📈 월말 보고서", "📊 반기 보고서", "📋 연말 보고서", "📈 업체별 매출변동 비교"]
            
            menu = st.selectbox(
                "보고서 유형 선택",
                menu_options
            )
        except Exception as e:
            # 오류 발생시 기본 메뉴로 대체
            menu_options = ["📈 월말 보고서", "📊 반기 보고서", "📋 연말 보고서"]
            menu = st.selectbox("보고서 유형 선택", menu_options)
        
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
    elif menu == "📈 업체별 매출변동 비교":
        show_revenue_trend_comparison()
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
    
    # 년월 선택 (컴팩트)
    col1, col2 = st.columns([3, 3])
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
    <div class="monthly-report-header" style="background: linear-gradient(135deg, #B8344F, #D32F4A); color: white !important; padding: 1.2rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);">
        <h2 style="color: white !important; margin: 0; font-size: 1.4rem; font-family: 'Inter', sans-serif; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);">RTB {year}년 월말보고</h2>
        <div style="margin-top: 0.8rem; font-size: 0.9rem; color: white !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
            <strong style="color: white !important;">보고일:</strong> <span style="color: white !important;">{report_year}년 {report_month:02d}월 15일</span> &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong style="color: white !important;">작성자:</strong> <span style="color: white !important;">RTB 회계팀</span>
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
            <div style="text-align: right; font-size: 1.3rem; font-weight: 700; padding: 0.5rem; background: #fff; border-radius: 6px; border: 1px solid #e9ecef;">
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
            <div style="text-align: right; font-size: 1.3rem; font-weight: 700; padding: 0.5rem; background: #fff; border-radius: 6px; border: 1px solid #e9ecef;">
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
        <div style="background: white; border: 3px solid #6c757d; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
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
        <div style="background: white; border: 3px solid #6c757d; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
            <h3 style="margin: 0; text-align: center; font-size: 1.4rem; font-weight: 700;">
                매입 총계: <span style="color: blue;">{total_expense:,}원</span>
            </h3>
        </div>
        ''', unsafe_allow_html=True)
    
    # 순이익 계산
    net_profit = total_revenue - total_expense
    st.markdown("---")
    profit_color = "red" if net_profit >= 0 else "blue"
    
    st.markdown(f'''
    <div style="background: white; border: 3px solid #6c757d; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
        <h3 style="margin: 0; text-align: center; font-size: 1.4rem; font-weight: 700;">
            순이익: <span style="color: {profit_color};">{net_profit:,}원</span>
        </h3>
    </div>
    ''', unsafe_allow_html=True)
    
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
        if st.button("📄 PDF", key="monthly_pdf", use_container_width=True):
            pdf_file = st.session_state.export_manager.generate_pdf_report(report, f"RTB_{year}년_{month}월_월말보고서")
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_{month}월_월말보고서.pdf",
                    mime="application/pdf",
                    key="monthly_pdf_download",
                    use_container_width=True
                )
    
    with col2:
        if st.button("📊 Excel", key="monthly_excel", use_container_width=True):
            excel_file = st.session_state.export_manager.generate_excel_report(data, f"RTB_{year}년_{month}월_월말보고서")
            with open(excel_file, "rb") as file:
                st.download_button(
                    label="다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_{month}월_월말보고서.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="monthly_excel_download",
                    use_container_width=True
                )

def show_semi_annual_report():
    st.header("반기 보고서")
    
    col1, col2 = st.columns([3, 4])
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
        st.info("**데이터 입력 안내**: '데이터 입력' 메뉴에서 월별 데이터를 입력하면 자동으로 반기 보고서에 반영됩니다.")
        return
    
    # 반기 집계
    semi_annual_summary = st.session_state.data_manager.aggregate_period_data(period_data)
    
    st.markdown("---")
    
    # 보고서 헤더
    # 보고일 계산 (상반기: 7월 15일, 하반기: 다음해 1월 15일)
    if period_name == "상반기":
        report_date = f"{year}년 07월 15일"
    else:  # 하반기
        report_date = f"{year + 1}년 01월 15일"
    
    st.markdown(f"""
    <div class="semi-annual-report-header" style="background: linear-gradient(135deg, #B8344F, #D32F4A); color: white !important; padding: 1.2rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);">
        <h2 style="color: white !important; margin: 0; font-size: 1.4rem; font-family: 'Inter', sans-serif; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);">RTB {year}년 {period_name} 보고서</h2>
        <div style="margin-top: 0.8rem; font-size: 0.9rem; color: white !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
            <strong style="color: white !important;">보고일:</strong> <span style="color: white !important;">{report_date}</span> &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong style="color: white !important;">보고기간:</strong> <span style="color: white !important;">{year}년 {months[0]}월 ~ {months[-1]}월</span> &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong style="color: white !important;">작성자:</strong> <span style="color: white !important;">RTB 회계팀</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 요약 정보
    col1, col2, col3 = st.columns(3)
    
    total_revenue = sum(semi_annual_summary['매출'].values())
    total_expense = sum(semi_annual_summary['매입'].values())
    net_profit = total_revenue - total_expense
    
    with col1:
        st.markdown(f'''
        <div style="background: white; border: 3px solid #6c757d; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
            <h3 style="margin: 0; text-align: center; font-size: 1.4rem; font-weight: 700;">
                {period_name} 총 매출<br><span style="color: red;">{total_revenue:,}원</span>
            </h3>
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
        <div style="background: white; border: 3px solid #6c757d; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
            <h3 style="margin: 0; text-align: center; font-size: 1.4rem; font-weight: 700;">
                {period_name} 총 매입<br><span style="color: blue;">{total_expense:,}원</span>
            </h3>
        </div>
        ''', unsafe_allow_html=True)
    with col3:
        profit_color = "red" if net_profit >= 0 else "blue"
        st.markdown(f'''
        <div style="background: white; border: 3px solid #6c757d; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
            <h3 style="margin: 0; text-align: center; font-size: 1.4rem; font-weight: 700;">
                {period_name} 순이익<br><span style="color: {profit_color};">{net_profit:,}원</span>
            </h3>
        </div>
        ''', unsafe_allow_html=True)
    
    # 상세 분석
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("매출처별 집계")
        
        # 매출처를 카테고리별로 분류하여 표시
        electronic_tax_sources = ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR"]
        zero_rated_sources = ["Everllence LEO", "Mitsui"]
        
        # 전자세금계산서매출 집계
        electronic_total = 0
        electronic_items = []
        for source in electronic_tax_sources:
            amount = semi_annual_summary['매출'].get(source, 0)
            if amount > 0:
                electronic_items.append(f'<div style="display: flex; justify-content: space-between; padding: 0.2rem 0; border-bottom: 1px solid #e9ecef;"><span style="font-size: 0.9rem;">{source}</span><span style="font-weight: 600; font-size: 0.9rem;">{amount:,}원</span></div>')
                electronic_total += amount
        
        if electronic_total > 0:
            st.markdown(f'''
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; border-left: 3px solid #6c757d;">
                <h5 style="margin: 0 0 0.5rem 0; color: #2c3e50; font-weight: 600;">전자세금계산서매출</h5>
                <div style="background: white; padding: 0.8rem; border-radius: 4px; margin-bottom: 0.5rem;">
                    {''.join(electronic_items)}
                </div>
                <div style="text-align: right; font-size: 1.1rem; font-weight: 700; color: red;">
                    소계: {electronic_total:,}원
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # 영세매출 집계
        zero_total = 0
        zero_items = []
        for source in zero_rated_sources:
            amount = semi_annual_summary['매출'].get(source, 0)
            if amount > 0:
                zero_items.append(f'<div style="display: flex; justify-content: space-between; padding: 0.2rem 0; border-bottom: 1px solid #e9ecef;"><span style="font-size: 0.9rem;">{source}</span><span style="font-weight: 600; font-size: 0.9rem;">{amount:,}원</span></div>')
                zero_total += amount
        
        if zero_total > 0:
            st.markdown(f'''
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; border-left: 3px solid #6c757d;">
                <h5 style="margin: 0 0 0.5rem 0; color: #2c3e50; font-weight: 600;">영세매출</h5>
                <div style="background: white; padding: 0.8rem; border-radius: 4px; margin-bottom: 0.5rem;">
                    {''.join(zero_items)}
                </div>
                <div style="text-align: right; font-size: 1.1rem; font-weight: 700; color: red;">
                    소계: {zero_total:,}원
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # 기타매출 집계
        other_amount = semi_annual_summary['매출'].get("기타", 0)
        if other_amount > 0:
            st.markdown(f'''
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; border-left: 3px solid #6c757d;">
                <h5 style="margin: 0 0 0.5rem 0; color: #2c3e50; font-weight: 600;">기타매출</h5>
                <div style="background: white; padding: 0.8rem; border-radius: 4px; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; padding: 0.2rem 0;"><span style="font-size: 0.9rem;">기타</span><span style="font-weight: 600; font-size: 0.9rem;">{other_amount:,}원</span></div>
                </div>
                <div style="text-align: right; font-size: 1.1rem; font-weight: 700; color: red;">
                    소계: {other_amount:,}원
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
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
        if st.button("📄 PDF", key="semi_pdf", use_container_width=True):
            report_data = {
                'period': f"{year}년 {period_name}",
                'summary': semi_annual_summary,
                'months_data': period_data
            }
            pdf_file = st.session_state.export_manager.generate_pdf_report(report_data, f"RTB_{year}년_{period_name}_보고서")
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_{period_name}_보고서.pdf",
                    mime="application/pdf",
                    key="semi_pdf_download",
                    use_container_width=True
                )
    
    with col2:
        if st.button("📊 Excel", key="semi_excel", use_container_width=True):
            excel_file = st.session_state.export_manager.generate_excel_report(semi_annual_summary, f"RTB_{year}년_{period_name}_보고서")
            with open(excel_file, "rb") as file:
                st.download_button(
                    label="다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_{period_name}_보고서.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="semi_excel_download",
                    use_container_width=True
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
    <div class="annual-report-header" style="background: linear-gradient(135deg, #B8344F, #D32F4A); color: white !important; padding: 1.2rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);">
        <h2 style="color: white !important; margin: 0; font-size: 1.4rem; font-family: 'Inter', sans-serif; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);">RTB {year}년 연말 보고서</h2>
        <div style="margin-top: 0.8rem; font-size: 0.9rem; color: white !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
            <strong style="color: white !important;">보고일:</strong> <span style="color: white !important;">2026년 01월 15일</span> &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong style="color: white !important;">보고기간:</strong> <span style="color: white !important;">{year}년 전체</span> &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong style="color: white !important;">작성자:</strong> <span style="color: white !important;">RTB 회계팀</span>
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
        st.markdown(f'''
        <div style="background: white; border: 3px solid #6c757d; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
            <h3 style="margin: 0; text-align: center; font-size: 1.4rem; font-weight: 700;">
                연간 총 매출<br><span style="color: red;">{total_revenue:,}원</span>
            </h3>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div style="background: white; border: 3px solid #6c757d; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
            <h3 style="margin: 0; text-align: center; font-size: 1.4rem; font-weight: 700;">
                연간 총 매입<br><span style="color: blue;">{total_expense:,}원</span>
            </h3>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        profit_color = "red" if net_profit >= 0 else "blue"
        st.markdown(f'''
        <div style="background: white; border: 3px solid #6c757d; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
            <h3 style="margin: 0; text-align: center; font-size: 1.4rem; font-weight: 700;">
                연간 순이익<br><span style="color: {profit_color};">{net_profit:,}원</span>
            </h3>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 매출/매입 상세 분석
    st.subheader("매출 vs 매입 상세 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 매출 세부 내역")
        
        # 매출처를 카테고리별로 분류하여 표시
        electronic_tax_sources = ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR"]
        zero_rated_sources = ["Everllence LEO", "Mitsui"]
        
        # 전자세금계산서매출 집계
        electronic_total = 0
        electronic_items = []
        for source in electronic_tax_sources:
            amount = annual_summary['매출'].get(source, 0)
            if amount > 0:
                electronic_items.append(f'<div style="display: flex; justify-content: space-between; padding: 0.15rem 0; border-bottom: 1px solid #e9ecef;"><span style="font-size: 0.85rem;">{source}</span><span style="font-weight: 600; font-size: 0.85rem;">{amount:,}원</span></div>')
                electronic_total += amount
        
        if electronic_total > 0:
            st.markdown(f'''
            <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.8rem; border-left: 3px solid #6c757d;">
                <h6 style="margin: 0 0 0.4rem 0; color: #2c3e50; font-weight: 600;">전자세금계산서매출</h6>
                <div style="background: white; padding: 0.6rem; border-radius: 4px; margin-bottom: 0.4rem;">
                    {''.join(electronic_items)}
                </div>
                <div style="text-align: right; font-size: 1rem; font-weight: 700; color: red;">
                    소계: {electronic_total:,}원
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # 영세매출 집계
        zero_total = 0
        zero_items = []
        for source in zero_rated_sources:
            amount = annual_summary['매출'].get(source, 0)
            if amount > 0:
                zero_items.append(f'<div style="display: flex; justify-content: space-between; padding: 0.15rem 0; border-bottom: 1px solid #e9ecef;"><span style="font-size: 0.85rem;">{source}</span><span style="font-weight: 600; font-size: 0.85rem;">{amount:,}원</span></div>')
                zero_total += amount
        
        if zero_total > 0:
            st.markdown(f'''
            <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.8rem; border-left: 3px solid #6c757d;">
                <h6 style="margin: 0 0 0.4rem 0; color: #2c3e50; font-weight: 600;">영세매출</h6>
                <div style="background: white; padding: 0.6rem; border-radius: 4px; margin-bottom: 0.4rem;">
                    {''.join(zero_items)}
                </div>
                <div style="text-align: right; font-size: 1rem; font-weight: 700; color: red;">
                    소계: {zero_total:,}원
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # 기타매출 집계
        other_amount = annual_summary['매출'].get("기타", 0)
        if other_amount > 0:
            st.markdown(f'''
            <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.8rem; border-left: 3px solid #6c757d;">
                <h6 style="margin: 0 0 0.4rem 0; color: #2c3e50; font-weight: 600;">기타매출</h6>
                <div style="background: white; padding: 0.6rem; border-radius: 4px; margin-bottom: 0.4rem;">
                    <div style="display: flex; justify-content: space-between; padding: 0.15rem 0;"><span style="font-size: 0.85rem;">기타</span><span style="font-weight: 600; font-size: 0.85rem;">{other_amount:,}원</span></div>
                </div>
                <div style="text-align: right; font-size: 1rem; font-weight: 700; color: red;">
                    소계: {other_amount:,}원
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 매입 세부 내역")
        
        # 매입 구성 표
        expense_df = pd.DataFrame(list(annual_summary['매입'].items()))
        expense_df.columns = ['항목', '금액']
        expense_df['금액'] = expense_df['금액'].apply(lambda x: f"{x:,}원")
        expense_df['비율'] = [f"{(v/total_expense*100):.1f}%" for v in annual_summary['매입'].values()]
        st.dataframe(expense_df, hide_index=True, use_container_width=True)
    
    # 구성 비교 차트 (매출구성 vs 매입분포)
    st.markdown("---")
    st.subheader("매출구성 vs 매입분포 비교")
    
    # revenue_summary 재생성
    revenue_summary = {
        "전자세금계산서매출": electronic_total,
        "영세매출": zero_total,
        "기타매출": other_amount
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 매출구성 분포")
        revenue_pie_compare = st.session_state.viz_manager.create_revenue_summary_pie_chart(revenue_summary)
        st.plotly_chart(revenue_pie_compare, use_container_width=True, key="annual_revenue_pie_compare")
    
    with col2:
        st.markdown("##### 매입항목별 분포") 
        expense_pie_compare = st.session_state.viz_manager.create_expense_pie_chart(annual_summary['매입'])
        st.plotly_chart(expense_pie_compare, use_container_width=True, key="annual_expense_pie_compare")
    
    st.markdown("---")
    
    # 매출 vs 매입 비교 차트
    st.subheader("매출 vs 매입 총액 비교")
    comparison_chart = st.session_state.viz_manager.create_revenue_expense_comparison_chart(total_revenue, total_expense, net_profit)
    st.plotly_chart(comparison_chart, use_container_width=True)
    
    # 내보내기 버튼
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 PDF", key="annual_pdf", use_container_width=True):
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
                    label="다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_연말보고서.pdf",
                    mime="application/pdf",
                    key="annual_pdf_download",
                    use_container_width=True
                )
    
    with col2:
        if st.button("📊 Excel", key="annual_excel", use_container_width=True):
            excel_file = st.session_state.export_manager.generate_excel_report(annual_summary, f"RTB_{year}년_연말보고서")
            with open(excel_file, "rb") as file:
                st.download_button(
                    label="다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_연말보고서.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="annual_excel_download",
                    use_container_width=True
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

def show_revenue_trend_comparison():
    st.header("업체별 매출변동 비교")
    
    # 연도 범위 선택
    col1, col2 = st.columns(2)
    with col1:
        start_year = st.selectbox("시작 연도", list(range(2020, 2030)), index=3, key="trend_start_year")
    with col2:
        end_year = st.selectbox("종료 연도", list(range(2020, 2030)), index=5, key="trend_end_year")
    
    if start_year > end_year:
        st.error("시작 연도가 종료 연도보다 클 수 없습니다.")
        return
    
    # 전체 데이터 수집
    all_data = st.session_state.data_manager.get_all_data()
    
    # 매출처별 연도별 데이터 집계
    revenue_sources = ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR", 
                      "Everllence LEO", "Mitsui", "기타"]
    
    # 연도별 매출처별 데이터 구조: {year: {source: total_amount}}
    yearly_data = {}
    years = list(range(start_year, end_year + 1))
    
    for year in years:
        yearly_data[year] = {source: 0 for source in revenue_sources}
        
        # 해당 연도의 모든 월 데이터 합계
        for month in range(1, 13):
            month_key = f"{year}-{month:02d}"
            if month_key in all_data:
                month_data = all_data[month_key].get('매출', {})
                for source in revenue_sources:
                    yearly_data[year][source] += month_data.get(source, 0)
    
    # 데이터가 있는지 확인
    has_data = any(sum(yearly_data[year].values()) > 0 for year in years)
    if not has_data:
        st.warning(f"{start_year}년부터 {end_year}년까지 매출 데이터가 없습니다.")
        st.info("**데이터 입력 안내**: '데이터 입력' 메뉴에서 월별 데이터를 입력하면 자동으로 반영됩니다.")
        return
    
    st.markdown("---")
    
    # 보고서 헤더
    st.markdown(f"""
    <div class="revenue-trend-header" style="background: linear-gradient(135deg, #B8344F, #D32F4A); color: white !important; padding: 1.2rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);">
        <h2 style="color: white !important; margin: 0; font-size: 1.4rem; font-family: 'Inter', sans-serif; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);">업체별 매출변동 비교 분석</h2>
        <div style="margin-top: 0.8rem; font-size: 0.9rem; color: white !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
            <strong style="color: white !important;">분석기간:</strong> <span style="color: white !important;">{start_year}년 ~ {end_year}년</span> &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong style="color: white !important;">작성자:</strong> <span style="color: white !important;">RTB 회계팀</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 꺾은선 그래프 생성
    st.subheader("매출처별 연도별 매출 추이")
    
    # Plotly 그래프 데이터 준비
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    fig = go.Figure()
    
    # 색상 팔레트
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471']
    
    for i, source in enumerate(revenue_sources):
        amounts = [yearly_data[year][source] for year in years]
        
        # 0이 아닌 데이터가 있는 경우만 그래프에 추가
        if any(amount > 0 for amount in amounts):
            fig.add_trace(go.Scatter(
                x=years,
                y=amounts,
                mode='lines+markers',
                name=source,
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=8, symbol='circle'),
                hovertemplate=f'<b>{source}</b><br>연도: %{{x}}<br>매출: %{{y:,.0f}}원<extra></extra>'
            ))
    
    fig.update_layout(
        title='매출처별 연도별 매출 추이',
        xaxis_title='연도',
        yaxis_title='매출 (원)',
        font=dict(family='Inter, sans-serif'),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
        template='plotly_white'
    )
    
    fig.update_xaxes(tickmode='linear', tick0=start_year, dtick=1)
    fig.update_yaxes(tickformat=',.0f')
    
    st.plotly_chart(fig, use_container_width=True, key="revenue_trend_line_chart")
    
    # 요약 통계
    st.markdown("---")
    st.subheader("매출처별 요약 통계")
    
    # 각 매출처별 통계 계산
    summary_data = []
    for source in revenue_sources:
        amounts = [yearly_data[year][source] for year in years]
        if any(amount > 0 for amount in amounts):
            total = sum(amounts)
            avg = total / len(years)
            max_amount = max(amounts)
            min_amount = min(amounts)
            max_year = years[amounts.index(max_amount)]
            min_year = years[amounts.index(min_amount)]
            
            summary_data.append({
                '매출처': source,
                '총 매출': f"{total:,}원",
                '연평균': f"{avg:,.0f}원",
                '최고매출': f"{max_amount:,}원 ({max_year}년)",
                '최저매출': f"{min_amount:,}원 ({min_year}년)"
            })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # 매출 증감률 분석
    st.markdown("---")
    st.subheader("전년 대비 매출 증감률")
    
    if len(years) > 1:
        growth_data = []
        for source in revenue_sources:
            amounts = [yearly_data[year][source] for year in years]
            if any(amount > 0 for amount in amounts):
                for i in range(1, len(years)):
                    prev_amount = amounts[i-1]
                    curr_amount = amounts[i]
                    if prev_amount > 0:
                        growth_rate = ((curr_amount - prev_amount) / prev_amount) * 100
                        growth_data.append({
                            '매출처': source,
                            '연도': f"{years[i-1]}→{years[i]}",
                            '이전년도': f"{prev_amount:,}원",
                            '해당년도': f"{curr_amount:,}원",
                            '증감률': f"{growth_rate:+.1f}%"
                        })
        
        if growth_data:
            growth_df = pd.DataFrame(growth_data)
            st.dataframe(growth_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
