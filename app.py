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
            menu_options = ["📊 대시보드", "📝 데이터 입력", "📈 월말 보고서", "📊 반기 보고서", "📋 연말 보고서", "⚙️ 설정"]
        else:
            menu_options = ["📊 대시보드", "📈 월말 보고서", "📊 반기 보고서", "📋 연말 보고서"]
        
        menu = st.selectbox(
            "보고서 유형 선택",
            menu_options
        )
        
        st.markdown("---")
        st.subheader("🗓️ 보고 일정")
        st.info("• 월말 보고: 매월 15일\n• 반기 보고: 7월/1월 15일\n• 연말 보고: 1월 15일")
        
        # 현재 날짜 표시
        today = date.today()
        st.markdown(f"**오늘 날짜:** {today.strftime('%Y년 %m월 %d일')}")
    
    # 메뉴별 페이지 라우팅
    if menu == "📊 대시보드":
        show_dashboard()
    elif menu == "📝 데이터 입력":
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

def show_dashboard():
    st.header("📊 RTB 회계 대시보드")
    
    # 최근 데이터 요약
    data = st.session_state.data_manager.get_all_data()
    
    if not data:
        st.warning("입력된 데이터가 없습니다. '데이터 입력' 메뉴에서 데이터를 입력해주세요.")
        st.info("💡 **자동 집계 시스템**: 월별 데이터를 입력하면 반기/연말 보고서에 자동으로 반영됩니다.")
        return
    
    # 기본 통계
    col1, col2, col3, col4 = st.columns(4)
    
    latest_month = max(data.keys()) if data else None
    if latest_month:
        latest_data = data[latest_month]
        total_revenue = sum(latest_data.get('매출', {}).values())
        total_expenses = sum(latest_data.get('매입', {}).values())
        net_profit = total_revenue - total_expenses
        
        with col1:
            st.metric("최근월 총 매출", f"{total_revenue:,}원")
        with col2:
            st.metric("최근월 총 매입", f"{total_expenses:,}원")
        with col3:
            st.metric("최근월 순이익", f"{net_profit:,}원", delta=f"{net_profit}")
        with col4:
            revenue_growth = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
            st.metric("수익률", f"{revenue_growth:.1f}%")
    
    st.markdown("---")
    
    # 시각화
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏭 매출처별 분포")
        if latest_month and data[latest_month].get('매출'):
            pie_chart = st.session_state.viz_manager.create_revenue_pie_chart(data[latest_month]['매출'])
            st.plotly_chart(pie_chart, use_container_width=True)
    
    with col2:
        st.subheader("💸 매입 항목별 분포")
        if latest_month and data[latest_month].get('매입'):
            expense_pie = st.session_state.viz_manager.create_expense_pie_chart(data[latest_month]['매입'])
            st.plotly_chart(expense_pie, use_container_width=True)
    
    # 데이터 입력 현황 표시
    st.markdown("---")
    st.subheader("📅 데이터 입력 현황")
    
    # 현재 연도 기준으로 월별 입력 현황 표시
    current_year = datetime.now().year
    months_with_data = []
    months_without_data = []
    
    for month in range(1, 13):
        month_key = f"{current_year}-{month:02d}"
        if month_key in data:
            months_with_data.append(f"{month}월")
        else:
            months_without_data.append(f"{month}월")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if months_with_data:
            st.success(f"**입력 완료 ({len(months_with_data)}개월)**: {', '.join(months_with_data)}")
        else:
            st.info("입력된 데이터가 없습니다.")
    
    with col2:
        if months_without_data:
            st.warning(f"**입력 필요 ({len(months_without_data)}개월)**: {', '.join(months_without_data)}")
        else:
            st.success("모든 월 데이터 입력 완료!")
    
    if months_with_data:
        st.info(f"💡 **자동 집계**: 입력된 {len(months_with_data)}개월 데이터가 반기/연말 보고서에 자동 반영됩니다.")

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
    
    # 관리 버튼들
    with st.expander("⚙️ 매출처/매입처 관리"):
        tab1, tab2, tab3 = st.tabs(["전자세금계산서매출", "영세매출", "매입항목"])
        
        with tab1:
            # 전자세금계산서매출처 관리
            col_input, col_add = st.columns([3, 1])
            with col_input:
                new_electronic = st.text_input("새 전자세금계산서매출처 (영어/한글 모두 가능)", key="new_electronic", placeholder="예: ABC Company Ltd.")
            with col_add:
                if st.button("추가", key="add_electronic"):
                    if new_electronic and new_electronic.strip() and new_electronic not in st.session_state.revenue_sources['electronic_tax']:
                        # 입력값 정리 (앞뒤 공백 제거)
                        clean_name = new_electronic.strip()
                        st.session_state.revenue_sources['electronic_tax'].append(clean_name)
                        st.success(f"'{clean_name}' 추가됨")
                        st.rerun()
            
            for i, source in enumerate(st.session_state.revenue_sources['electronic_tax'][:]):
                col_name, col_del = st.columns([3, 1])
                with col_name:
                    st.text(source)
                with col_del:
                    if st.button("🗑️", key=f"del_electronic_{i}"):
                        st.session_state.revenue_sources['electronic_tax'].remove(source)
                        st.rerun()
        
        with tab2:
            # 영세매출처 관리
            col_input, col_add = st.columns([3, 1])
            with col_input:
                new_zero = st.text_input("새 영세매출처 (영어/한글 모두 가능)", key="new_zero", placeholder="예: Global Trade Co.")
            with col_add:
                if st.button("추가", key="add_zero"):
                    if new_zero and new_zero.strip() and new_zero not in st.session_state.revenue_sources['zero_rated']:
                        clean_name = new_zero.strip()
                        st.session_state.revenue_sources['zero_rated'].append(clean_name)
                        st.success(f"'{clean_name}' 추가됨")
                        st.rerun()
            
            for i, source in enumerate(st.session_state.revenue_sources['zero_rated'][:]):
                col_name, col_del = st.columns([3, 1])
                with col_name:
                    st.text(source)
                with col_del:
                    if st.button("🗑️", key=f"del_zero_{i}"):
                        st.session_state.revenue_sources['zero_rated'].remove(source)
                        st.rerun()
        
        with tab3:
            # 매입 항목 관리
            col_input, col_add = st.columns([3, 1])
            with col_input:
                new_expense = st.text_input("새 매입 항목 (영어/한글 모두 가능)", key="new_expense", placeholder="예: Office Supplies")
            with col_add:
                if st.button("추가", key="add_expense"):
                    if new_expense and new_expense.strip() and new_expense not in st.session_state.expense_items:
                        clean_name = new_expense.strip()
                        st.session_state.expense_items.append(clean_name)
                        st.success(f"'{clean_name}' 추가됨")
                        st.rerun()
            
            for i, item in enumerate(st.session_state.expense_items[:]):
                col_name, col_del = st.columns([3, 1])
                with col_name:
                    st.text(item)
                with col_del:
                    if st.button("🗑️", key=f"del_expense_{i}"):
                        st.session_state.expense_items.remove(item)
                        st.rerun()
    
    # 매출/매입 입력
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 매출")
        revenue_data = {}
        
        # 전자세금계산서매출
        st.markdown("**📋 전자세금계산서매출**")
        electronic_total = 0
        for source in st.session_state.revenue_sources['electronic_tax']:
            current_value = existing_data.get('매출', {}).get(source, 0)
            value = st.number_input(f"{source}", value=current_value, min_value=0, step=1000000, key=f"electronic_{source}")
            revenue_data[source] = value
            electronic_total += value
        st.info(f"소계: {electronic_total:,}원")
        
        # 영세매출
        st.markdown("**🌐 영세매출**")
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
        st.markdown("**📦 기타 매출**")
        current_other = existing_data.get('매출', {}).get("기타", 0)
        other_revenue = st.number_input("기타", value=current_other, min_value=0, step=1000000, key="other_revenue")
        revenue_data["기타"] = other_revenue
        
        total_revenue = sum(revenue_data.values())
        st.success(f"**총 매출: {total_revenue:,}원**")
    
    with col2:
        st.subheader("💸 매입")
        expense_data = {}
        
        for item in st.session_state.expense_items:
            current_value = existing_data.get('매입', {}).get(item, 0)
            value = st.number_input(f"{item}", value=current_value, min_value=0, step=100000, key=f"expense_{item}")
            expense_data[item] = value
        
        total_expense = sum(expense_data.values())
        net_profit = total_revenue - total_expense
        st.success(f"**총 매입: {total_expense:,}원**")
        st.success(f"**순이익: {net_profit:,}원**")
    
    # 저장 버튼
    st.markdown("---")
    if st.button("💾 데이터 저장", type="primary", use_container_width=True):
        month_data = {
            "매출": revenue_data,
            "매입": expense_data,
            "입력일시": datetime.now().isoformat()
        }
        
        st.session_state.data_manager.save_month_data(month_key, month_data)
        
        # 성공 메시지와 자동 반영 안내
        st.success(f"✅ {year}년 {month}월 데이터가 저장되었습니다!")
        st.info("""
        📊 **자동 집계 시스템 안내**
        - 반기 보고서: 저장한 월별 데이터가 자동으로 상/하반기 집계에 반영됩니다
        - 연말 보고서: 저장한 월별 데이터가 자동으로 연간 집계에 반영됩니다
        - 새로 추가한 매출처/매입처도 자동으로 보고서에 포함됩니다
        """)
        st.rerun()

def show_monthly_report():
    st.header("📈 월말 보고서")
    
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
    header_col1, header_col2 = st.columns([1, 4])
    
    with header_col1:
        try:
            st.image("assets/rtb_logo.png", width=80)
        except:
            st.write("🏢")
    
    with header_col2:
        st.markdown(f"""
        ## RTB {year}년 {month}월 월말 보고서
        **작성일:** {datetime.now().strftime('%Y년 %m월 %d일')}  
        **보고기간:** {year}년 {month}월 1일 ~ {year}년 {month}월 말일  
        **작성자:** RTB 회계팀
        """)
    
    # 요약 테이블
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 매출 현황")
        
        # 전자세금계산서매출
        st.markdown("**📋 전자세금계산서매출**")
        electronic_tax_sources = ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR"]
        electronic_data = []
        electronic_total = 0
        for source in electronic_tax_sources:
            amount = data['매출'].get(source, 0)
            electronic_data.append([source, f"{amount:,}"])
            electronic_total += amount
        
        electronic_df = pd.DataFrame(electronic_data)
        electronic_df.columns = ['매출처', '금액(원)']
        st.dataframe(electronic_df, hide_index=True, use_container_width=True)
        st.info(f"전자세금계산서매출 소계: {electronic_total:,}원")
        
        # 영세매출
        st.markdown("**🌐 영세매출**")
        zero_rated_sources = ["Everllence LEO", "Mitsui"]
        zero_data = []
        zero_total = 0
        for source in zero_rated_sources:
            amount = data['매출'].get(source, 0)
            zero_data.append([source, f"{amount:,}"])
            zero_total += amount
        
        zero_df = pd.DataFrame(zero_data)
        zero_df.columns = ['매출처', '금액(원)']
        st.dataframe(zero_df, hide_index=True, use_container_width=True)
        st.info(f"영세매출 소계: {zero_total:,}원")
        
        # 기타 매출
        st.markdown("**📦 기타 매출**")
        other_amount = data['매출'].get("기타", 0)
        other_df = pd.DataFrame([["기타", f"{other_amount:,}"]])
        other_df.columns = ['매출처', '금액(원)']
        st.dataframe(other_df, hide_index=True, use_container_width=True)
        
        total_revenue = sum(data['매출'].values())
        st.success(f"**매출 총계: {total_revenue:,}원**")
    
    with col2:
        st.subheader("💸 매입 현황")
        expense_df = pd.DataFrame(list(data['매입'].items()))
        expense_df.columns = ['항목', '금액(원)']
        expense_df['금액(원)'] = expense_df['금액(원)'].apply(lambda x: f"{x:,}")
        st.dataframe(expense_df, hide_index=True, use_container_width=True)
        
        total_expense = sum(data['매입'].values())
        st.metric("매입 총계", f"{total_expense:,}원")
    
    # 순이익 계산
    net_profit = total_revenue - total_expense
    st.markdown("---")
    st.metric("🎯 순이익", f"{net_profit:,}원", delta=f"{net_profit}")
    
    # 시각화
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 매출처별 분포")
        pie_chart = st.session_state.viz_manager.create_revenue_pie_chart(data['매출'])
        st.plotly_chart(pie_chart, use_container_width=True)
    
    with col2:
        st.subheader("📊 매입 항목별 분포")
        expense_pie = st.session_state.viz_manager.create_expense_pie_chart(data['매입'])
        st.plotly_chart(expense_pie, use_container_width=True)
    
    # 내보내기 버튼
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 PDF 다운로드"):
            pdf_file = st.session_state.export_manager.generate_pdf_report(report, f"RTB_{year}년_{month}월_월말보고서")
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="📥 PDF 파일 다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_{month}월_월말보고서.pdf",
                    mime="application/pdf"
                )
    
    with col2:
        if st.button("📊 Excel 다운로드"):
            excel_file = st.session_state.export_manager.generate_excel_report(data, f"RTB_{year}년_{month}월_월말보고서")
            with open(excel_file, "rb") as file:
                st.download_button(
                    label="📥 Excel 파일 다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_{month}월_월말보고서.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

def show_semi_annual_report():
    st.header("📊 반기 보고서")
    
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
        st.info("💡 **데이터 입력 안내**: '데이터 입력' 메뉴에서 월별 데이터를 입력하면 자동으로 반기 보고서에 반영됩니다.")
        return
    
    # 반기 집계
    semi_annual_summary = st.session_state.data_manager.aggregate_period_data(period_data)
    
    st.markdown("---")
    
    # 보고서 헤더
    header_col1, header_col2 = st.columns([1, 4])
    
    with header_col1:
        try:
            st.image("assets/rtb_logo.png", width=80)
        except:
            st.write("🏢")
    
    with header_col2:
        st.markdown(f"""
        ## RTB {year}년 {period_name} 보고서
        **작성일:** {datetime.now().strftime('%Y년 %m월 %d일')}  
        **보고기간:** {year}년 {months[0]}월 ~ {months[-1]}월  
        **작성자:** RTB 회계팀
        """)
    
    # 요약 정보
    col1, col2, col3 = st.columns(3)
    
    total_revenue = sum(semi_annual_summary['매출'].values())
    total_expense = sum(semi_annual_summary['매입'].values())
    net_profit = total_revenue - total_expense
    
    with col1:
        st.metric(f"{period_name} 총 매출", f"{total_revenue:,}원")
    with col2:
        st.metric(f"{period_name} 총 매입", f"{total_expense:,}원")
    with col3:
        st.metric(f"{period_name} 순이익", f"{net_profit:,}원")
    
    # 상세 분석
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 매출처별 집계")
        revenue_df = pd.DataFrame(list(semi_annual_summary['매출'].items()))
        revenue_df.columns = ['매출처', '금액(원)']
        revenue_df['금액(원)'] = revenue_df['금액(원)'].apply(lambda x: f"{x:,}")
        st.dataframe(revenue_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("💸 매입 항목별 집계")
        expense_df = pd.DataFrame(list(semi_annual_summary['매입'].items()))
        expense_df.columns = ['항목', '금액(원)']
        expense_df['금액(원)'] = expense_df['금액(원)'].apply(lambda x: f"{x:,}")
        st.dataframe(expense_df, hide_index=True, use_container_width=True)
    
    # 내보내기
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 PDF 다운로드", key="semi_pdf"):
            report_data = {
                'period': f"{year}년 {period_name}",
                'summary': semi_annual_summary,
                'months_data': period_data
            }
            pdf_file = st.session_state.export_manager.generate_pdf_report(report_data, f"RTB_{year}년_{period_name}_보고서")
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="📥 PDF 파일 다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_{period_name}_보고서.pdf",
                    mime="application/pdf",
                    key="semi_pdf_download"
                )

def show_annual_report():
    st.header("📋 연말 보고서")
    
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
        st.info("💡 **데이터 입력 안내**: '데이터 입력' 메뉴에서 월별 데이터를 입력하면 자동으로 연말 보고서에 반영됩니다.")
        return
    
    # 연간 집계
    annual_summary = st.session_state.data_manager.aggregate_period_data(annual_data)
    
    st.markdown("---")
    
    # 보고서 헤더
    header_col1, header_col2 = st.columns([1, 4])
    
    with header_col1:
        try:
            st.image("assets/rtb_logo.png", width=100)
        except:
            st.write("🏢")
    
    with header_col2:
        st.markdown(f"""
        # RTB {year}년 연말 보고서
        **작성일:** {datetime.now().strftime('%Y년 %m월 %d일')}  
        **보고기간:** {year}년 전체  
        **작성:** RTB 회계팀
        """)
    
    st.markdown("---")
    
    # 핵심 지표 (큰 숫자로 강조)
    total_revenue = sum(annual_summary['매출'].values())
    total_expense = sum(annual_summary['매입'].values())
    net_profit = total_revenue - total_expense
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="💰 연간 총 매출",
            value=f"{total_revenue:,}원",
            delta=None
        )
    
    with col2:
        st.metric(
            label="💸 연간 총 매입", 
            value=f"{total_expense:,}원",
            delta=None
        )
    
    with col3:
        profit_color = "normal" if net_profit >= 0 else "inverse"
        st.metric(
            label="🎯 연간 순이익",
            value=f"{net_profit:,}원",
            delta=f"{net_profit:,}원" if net_profit != 0 else None
        )
    
    st.markdown("---")
    
    # 매출/매입 비교 분석
    st.subheader("📊 매출 vs 매입 비교")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 매출 세부 내역")
        
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
        st.markdown("#### 💸 매입 세부 내역")
        
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
    st.subheader("📈 매출 vs 매입 총액 비교")
    comparison_chart = st.session_state.viz_manager.create_revenue_expense_comparison_chart(total_revenue, total_expense, net_profit)
    st.plotly_chart(comparison_chart, use_container_width=True)
    
    # 내보내기 버튼
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 PDF 다운로드", key="annual_pdf"):
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
                    label="📥 PDF 파일 다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_연말보고서.pdf",
                    mime="application/pdf",
                    key="annual_pdf_download"
                )
    
    with col2:
        if st.button("📊 Excel 다운로드", key="annual_excel"):
            excel_file = st.session_state.export_manager.generate_excel_report(annual_summary, f"RTB_{year}년_연말보고서")
            with open(excel_file, "rb") as file:
                st.download_button(
                    label="📥 Excel 파일 다운로드",
                    data=file.read(),
                    file_name=f"RTB_{year}년_연말보고서.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="annual_excel_download"
                )

def show_settings():
    st.header("⚙️ 시스템 설정")
    
    # 탭으로 설정 메뉴 구분
    tab1, tab2, tab3 = st.tabs(["💼 매출처/매입처 관리", "📊 데이터 관리", "ℹ️ 시스템 정보"])
    
    with tab1:
        st.subheader("💼 매출처 및 매입처 관리")
        
        # 매출처 관리
        st.markdown("#### 📈 매출처 관리")
        
        # 세션 상태에 매출처 정보가 없으면 기본값 설정
        if 'revenue_sources' not in st.session_state:
            st.session_state.revenue_sources = {
                'electronic_tax': ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR"],
                'zero_rated': ["Everllence LEO", "Mitsui"],
                'other': ["기타"]
            }
        
        # 전자세금계산서매출
        st.markdown("**🧾 전자세금계산서매출**")
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
        st.markdown("**🌐 영세매출**")
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
        st.markdown("#### 📉 매입 항목 관리")
        
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
