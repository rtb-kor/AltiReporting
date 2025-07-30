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

def main():
    st.title("🏢 RTB 회계 통합 보고서 시스템")
    st.markdown("---")
    
    # 사이드바 메뉴
    with st.sidebar:
        st.header("📋 메뉴")
        menu = st.selectbox(
            "보고서 유형 선택",
            ["📊 대시보드", "📝 데이터 입력", "📈 월말 보고서", "📊 반기 보고서", "📋 연말 보고서", "⚙️ 설정"]
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
        show_data_input()
    elif menu == "📈 월말 보고서":
        show_monthly_report()
    elif menu == "📊 반기 보고서":
        show_semi_annual_report()
    elif menu == "📋 연말 보고서":
        show_annual_report()
    elif menu == "⚙️ 설정":
        show_settings()

def show_dashboard():
    st.header("📊 RTB 회계 대시보드")
    
    # 최근 데이터 요약
    data = st.session_state.data_manager.get_all_data()
    
    if not data:
        st.warning("입력된 데이터가 없습니다. '데이터 입력' 메뉴에서 데이터를 입력해주세요.")
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
        st.subheader("📈 월별 매출 추이")
        if data:
            monthly_chart = st.session_state.viz_manager.create_monthly_trend_chart(data)
            st.plotly_chart(monthly_chart, use_container_width=True)
    
    with col2:
        st.subheader("🏭 매출처별 분포")
        if latest_month and data[latest_month].get('매출'):
            pie_chart = st.session_state.viz_manager.create_revenue_pie_chart(data[latest_month]['매출'])
            st.plotly_chart(pie_chart, use_container_width=True)

def show_data_input():
    st.header("📝 데이터 입력")
    
    # 년월 선택
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("년도", list(range(2020, 2030)), index=5)  # 2025가 기본값
    with col2:
        month = st.selectbox("월", list(range(1, 13)), index=6)  # 7월이 기본값
    
    month_key = f"{year}-{month:02d}"
    
    st.markdown("---")
    
    # 기존 데이터 로드
    existing_data = st.session_state.data_manager.get_month_data(month_key)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 매출 입력")
        
        # 매출처별 입력
        revenue_sources = ["현대중공업", "삼성중공업", "STX조선해양", "해외업체(USD)", "기타"]
        revenue_data = {}
        
        for source in revenue_sources:
            current_value = existing_data.get('매출', {}).get(source, 0)
            if source == "해외업체(USD)":
                value = st.number_input(f"{source} (원화환산)", value=current_value, min_value=0, step=1000000)
            else:
                value = st.number_input(f"{source} (원)", value=current_value, min_value=0, step=1000000)
            revenue_data[source] = value
    
    with col2:
        st.subheader("💸 매입 입력")
        
        # 매입 항목
        expense_items = [
            "원자재비", "외주비", "급여", "복리후생비", 
            "임차료", "공과금", "기타운영비", "세금"
        ]
        expense_data = {}
        
        for item in expense_items:
            current_value = existing_data.get('매입', {}).get(item, 0)
            value = st.number_input(f"{item} (원)", value=current_value, min_value=0, step=100000)
            expense_data[item] = value
    
    st.markdown("---")
    
    # 요약 정보
    total_revenue = sum(revenue_data.values())
    total_expense = sum(expense_data.values())
    net_profit = total_revenue - total_expense
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 매출", f"{total_revenue:,}원")
    with col2:
        st.metric("총 매입", f"{total_expense:,}원")
    with col3:
        st.metric("순이익", f"{net_profit:,}원")
    
    # 저장 버튼
    if st.button("💾 데이터 저장", type="primary"):
        month_data = {
            "매출": revenue_data,
            "매입": expense_data,
            "입력일시": datetime.now().isoformat()
        }
        
        st.session_state.data_manager.save_month_data(month_key, month_data)
        st.success(f"✅ {year}년 {month}월 데이터가 저장되었습니다.")
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
    st.markdown(f"""
    ## 📋 RTB {year}년 {month}월 월말 보고서
    **작성일:** {datetime.now().strftime('%Y년 %m월 %d일')}  
    **보고기간:** {year}년 {month}월 1일 ~ {year}년 {month}월 말일  
    **작성자:** RTB 회계팀
    """)
    
    # 요약 테이블
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 매출 현황")
        revenue_df = pd.DataFrame(list(data['매출'].items()), columns=['매출처', '금액(원)'])
        revenue_df['금액(원)'] = revenue_df['금액(원)'].apply(lambda x: f"{x:,}")
        st.dataframe(revenue_df, hide_index=True, use_container_width=True)
        
        total_revenue = sum(data['매출'].values())
        st.metric("매출 총계", f"{total_revenue:,}원")
    
    with col2:
        st.subheader("💸 매입 현황")
        expense_df = pd.DataFrame(list(data['매입'].items()), columns=['항목', '금액(원)'])
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
        return
    
    # 반기 집계
    semi_annual_summary = st.session_state.data_manager.aggregate_period_data(period_data)
    
    st.markdown("---")
    
    # 보고서 헤더
    st.markdown(f"""
    ## 📋 RTB {year}년 {period_name} 보고서
    **작성일:** {datetime.now().strftime('%Y년 %m월 %d일')}  
    **보고기간:** {year}년 {months[0]}월 ~ {months[-1]}월  
    **작성자:** RTB 회계팀
    """)
    
    # 월별 추이
    st.subheader("📈 월별 실적 추이")
    monthly_trend = st.session_state.viz_manager.create_monthly_trend_chart(period_data)
    st.plotly_chart(monthly_trend, use_container_width=True)
    
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
        revenue_df = pd.DataFrame(list(semi_annual_summary['매출'].items()), columns=['매출처', '금액(원)'])
        revenue_df['금액(원)'] = revenue_df['금액(원)'].apply(lambda x: f"{x:,}")
        st.dataframe(revenue_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("💸 매입 항목별 집계")
        expense_df = pd.DataFrame(list(semi_annual_summary['매입'].items()), columns=['항목', '금액(원)'])
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
        return
    
    # 연간 집계
    annual_summary = st.session_state.data_manager.aggregate_period_data(annual_data)
    
    # 상하반기 분리 집계
    first_half = {k: v for k, v in annual_data.items() if int(k.split('-')[1]) <= 6}
    second_half = {k: v for k, v in annual_data.items() if int(k.split('-')[1]) > 6}
    
    first_half_summary = st.session_state.data_manager.aggregate_period_data(first_half) if first_half else {}
    second_half_summary = st.session_state.data_manager.aggregate_period_data(second_half) if second_half else {}
    
    st.markdown("---")
    
    # 보고서 헤더
    st.markdown(f"""
    ## 📋 RTB {year}년 연말 종합 보고서
    **작성일:** {datetime.now().strftime('%Y년 %m월 %d일')}  
    **보고기간:** {year}년 1월 1일 ~ {year}년 12월 31일  
    **작성자:** RTB 회계팀장
    """)
    
    # 연간 요약
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = sum(annual_summary['매출'].values())
    total_expense = sum(annual_summary['매입'].values())
    net_profit = total_revenue - total_expense
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    with col1:
        st.metric("연간 총 매출", f"{total_revenue:,}원")
    with col2:
        st.metric("연간 총 매입", f"{total_expense:,}원")
    with col3:
        st.metric("연간 순이익", f"{net_profit:,}원")
    with col4:
        st.metric("수익률", f"{profit_margin:.1f}%")
    
    # 상하반기 비교
    st.subheader("📊 상하반기 비교 분석")
    
    if first_half_summary and second_half_summary:
        comparison_data = {
            '구분': ['상반기', '하반기', '증감'],
            '매출': [
                sum(first_half_summary['매출'].values()),
                sum(second_half_summary['매출'].values()),
                sum(second_half_summary['매출'].values()) - sum(first_half_summary['매출'].values())
            ],
            '매입': [
                sum(first_half_summary['매입'].values()),
                sum(second_half_summary['매입'].values()),
                sum(second_half_summary['매입'].values()) - sum(first_half_summary['매입'].values())
            ]
        }
        comparison_data['순이익'] = [
            comparison_data['매출'][0] - comparison_data['매입'][0],
            comparison_data['매출'][1] - comparison_data['매입'][1],
            comparison_data['매출'][2] - comparison_data['매입'][2]
        ]
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.iloc[:, 1:] = comparison_df.iloc[:, 1:].applymap(lambda x: f"{x:,}원")
        st.dataframe(comparison_df, hide_index=True, use_container_width=True)
    
    # 연간 추이 차트
    st.subheader("📈 연간 실적 추이")
    annual_trend = st.session_state.viz_manager.create_monthly_trend_chart(annual_data)
    st.plotly_chart(annual_trend, use_container_width=True)
    
    # 매출처별 연간 분석
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏭 매출처별 연간 실적")
        revenue_pie = st.session_state.viz_manager.create_revenue_pie_chart(annual_summary['매출'])
        st.plotly_chart(revenue_pie, use_container_width=True)
    
    with col2:
        st.subheader("💸 매입 항목별 연간 실적")
        expense_pie = st.session_state.viz_manager.create_expense_pie_chart(annual_summary['매입'])
        st.plotly_chart(expense_pie, use_container_width=True)

def show_settings():
    st.header("⚙️ 시스템 설정")
    
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
    
    st.markdown("---")
    
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
