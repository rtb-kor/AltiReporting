import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any

class VisualizationManager:
    def __init__(self):
        # RTB 브랜드 색상 팔레트 (로고 기반 버건디)
        self.color_palette = [
            '#8B1538',  # RTB 로고 버건디
            '#A01E47',  # 밝은 버건디
            '#B91C1C',  # 진한 레드
            '#6B7280',  # RTB 그레이
            '#374151',  # 진한 그레이
            '#DC2626',  # 보조 레드
            '#9CA3AF',  # 밝은 그레이
            '#4B5563',  # 중간 그레이
            '#F3F4F6',  # 연한 그레이
            '#E5E7EB'   # 매우 연한 그레이
        ]
    
    def create_revenue_pie_chart(self, revenue_data: Dict[str, int]) -> go.Figure:
        """매출처별 파이차트 생성"""
        if not revenue_data or sum(revenue_data.values()) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        # 0이 아닌 값만 필터링
        filtered_data = {k: v for k, v in revenue_data.items() if v > 0}
        
        if not filtered_data:
            fig = go.Figure()
            fig.add_annotation(
                text="매출 데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        labels = list(filtered_data.keys())
        values = list(filtered_data.values())
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=self.color_palette[:len(labels)],
            texttemplate='%{label}<br>%{value:,}원<br>(%{percent})',
            textposition="auto",
            hovertemplate='<b>%{label}</b><br>' +
                         '금액: %{value:,}원<br>' +
                         '비율: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': '매출처별 분포',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'family': 'Inter, sans-serif', 'color': '#8B1538'}
            },
            showlegend=True,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            font=dict(family="Inter, sans-serif", size=12, color='#374151'),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
    
    def create_expense_pie_chart(self, expense_data: Dict[str, int]) -> go.Figure:
        """매입 항목별 파이차트 생성"""
        if not expense_data or sum(expense_data.values()) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        # 0이 아닌 값만 필터링
        filtered_data = {k: v for k, v in expense_data.items() if v > 0}
        
        if not filtered_data:
            fig = go.Figure()
            fig.add_annotation(
                text="매입 데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        labels = list(filtered_data.keys())
        values = list(filtered_data.values())
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=self.color_palette[:len(labels)],
            texttemplate='%{label}<br>%{value:,}원<br>(%{percent})',
            textposition="auto",
            hovertemplate='<b>%{label}</b><br>' +
                         '금액: %{value:,}원<br>' +
                         '비율: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': '매입 항목별 분포',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'family': 'Inter, sans-serif', 'color': '#8B1538'}
            },
            showlegend=True,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            font=dict(family="Inter, sans-serif", size=12, color='#374151'),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
    
    def create_monthly_trend_chart(self, monthly_data: Dict[str, Any]) -> go.Figure:
        """월별 추이 차트 생성"""
        if not monthly_data:
            fig = go.Figure()
            fig.add_annotation(
                text="데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        # 데이터 준비
        months = sorted(monthly_data.keys())
        revenues = []
        expenses = []
        profits = []
        
        for month in months:
            data = monthly_data[month]
            revenue = sum(data.get('매출', {}).values())
            expense = sum(data.get('매입', {}).values())
            profit = revenue - expense
            
            revenues.append(revenue)
            expenses.append(expense)
            profits.append(profit)
        
        # 월 표시를 위한 라벨 생성
        month_labels = [f"{month.split('-')[0]}년 {int(month.split('-')[1])}월" for month in months]
        
        fig = go.Figure()
        
        # 매출 라인
        fig.add_trace(go.Scatter(
            x=month_labels,
            y=revenues,
            mode='lines+markers',
            name='매출',
            line=dict(color='#4ECDC4', width=3),
            marker=dict(size=8),
            hovertemplate='<b>매출</b><br>' +
                         '%{x}<br>' +
                         '%{y:,}원<br>' +
                         '<extra></extra>'
        ))
        
        # 매입 라인
        fig.add_trace(go.Scatter(
            x=month_labels,
            y=expenses,
            mode='lines+markers',
            name='매입',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8),
            hovertemplate='<b>매입</b><br>' +
                         '%{x}<br>' +
                         '%{y:,}원<br>' +
                         '<extra></extra>'
        ))
        
        # 순이익 라인
        fig.add_trace(go.Scatter(
            x=month_labels,
            y=profits,
            mode='lines+markers',
            name='순이익',
            line=dict(color='#45B7D1', width=3),
            marker=dict(size=8),
            hovertemplate='<b>순이익</b><br>' +
                         '%{x}<br>' +
                         '%{y:,}원<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': '월별 실적 추이',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title="기간",
            yaxis_title="금액 (원)",
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            font=dict(family="Arial", size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified'
        )
        
        # Y축 포맷팅
        fig.update_layout(yaxis=dict(tickformat=','))
        
        return fig
    
    def create_revenue_source_comparison(self, period_data: Dict[str, Any]) -> go.Figure:
        """매출처별 기간 비교 차트"""
        if not period_data:
            fig = go.Figure()
            fig.add_annotation(
                text="데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        # 매출처별 월별 데이터 준비 (전자세금계산서매출 + 영세매출 + 기타)
        electronic_tax_sources = ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR"]
        zero_rated_sources = ["Everllence LEO", "Mitsui"]
        other_sources = ["기타"]
        revenue_sources = electronic_tax_sources + [s for s in zero_rated_sources if s not in electronic_tax_sources] + other_sources
        months = sorted(period_data.keys())
        month_labels = [f"{month.split('-')[1]}월" for month in months]
        
        fig = go.Figure()
        
        for i, source in enumerate(revenue_sources):
            values = []
            for month in months:
                values.append(period_data[month].get('매출', {}).get(source, 0))
            
            if sum(values) > 0:  # 데이터가 있는 매출처만 표시
                fig.add_trace(go.Bar(
                    name=source,
                    x=month_labels,
                    y=values,
                    marker_color=self.color_palette[i % len(self.color_palette)],
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                 '%{x}<br>' +
                                 '%{y:,}원<br>' +
                                 '<extra></extra>'
                ))
        
        fig.update_layout(
            title={
                'text': '매출처별 월별 비교',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title="월",
            yaxis_title="매출액 (원)",
            barmode='group',
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            font=dict(family="Arial", size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_layout(yaxis=dict(tickformat=','))
        
        return fig
    
    def create_expense_breakdown_chart(self, expense_data: Dict[str, int]) -> go.Figure:
        """매입 항목별 막대차트"""
        if not expense_data or sum(expense_data.values()) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        # 0이 아닌 값만 필터링 및 정렬
        filtered_data = {k: v for k, v in expense_data.items() if v > 0}
        sorted_data = dict(sorted(filtered_data.items(), key=lambda x: x[1], reverse=True))
        
        if not sorted_data:
            fig = go.Figure()
            fig.add_annotation(
                text="매입 데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        items = list(sorted_data.keys())
        values = list(sorted_data.values())
        
        fig = go.Figure(data=[go.Bar(
            x=items,
            y=values,
            marker_color=self.color_palette[:len(items)],
            text=[f'{v:,}원' for v in values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>' +
                         '금액: %{y:,}원<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': '매입 항목별 금액',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title="매입 항목",
            yaxis_title="금액 (원)",
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            font=dict(family="Arial", size=12)
        )
        
        fig.update_layout(
            yaxis=dict(tickformat=','),
            xaxis=dict(tickangle=45)
        )
        
        return fig
    
    def create_profit_analysis_chart(self, monthly_data: Dict[str, Any]) -> go.Figure:
        """수익률 분석 차트"""
        if not monthly_data:
            fig = go.Figure()
            fig.add_annotation(
                text="데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        months = sorted(monthly_data.keys())
        profit_margins = []
        
        for month in months:
            data = monthly_data[month]
            revenue = sum(data.get('매출', {}).values())
            expense = sum(data.get('매입', {}).values())
            profit_margin = ((revenue - expense) / revenue * 100) if revenue > 0 else 0
            profit_margins.append(profit_margin)
        
        month_labels = [f"{month.split('-')[1]}월" for month in months]
        
        # 색상 결정 (수익률에 따라)
        colors = []
        for margin in profit_margins:
            if margin >= 20:
                colors.append('#4ECDC4')  # 녹색 (우수)
            elif margin >= 10:
                colors.append('#FFEAA7')  # 노란색 (양호)
            else:
                colors.append('#FF6B6B')  # 빨간색 (부진)
        
        fig = go.Figure(data=[go.Bar(
            x=month_labels,
            y=profit_margins,
            marker_color=colors,
            text=[f'{m:.1f}%' for m in profit_margins],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>' +
                         '수익률: %{y:.1f}%<br>' +
                         '<extra></extra>'
        )])
        
        # 기준선 추가
        fig.add_hline(y=20, line_dash="dash", line_color="green", 
                     annotation_text="우수 기준 (20%)", annotation_position="right")
        fig.add_hline(y=10, line_dash="dash", line_color="orange", 
                     annotation_text="적정 기준 (10%)", annotation_position="right")
        
        fig.update_layout(
            title={
                'text': '월별 수익률 분석',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title="월",
            yaxis_title="수익률 (%)",
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            font=dict(family="Arial", size=12)
        )
        
        return fig
    
    def create_revenue_summary_pie_chart(self, revenue_summary: Dict[str, int]) -> go.Figure:
        """매출 구성 요약 파이차트 생성 (전자세금계산서/영세/기타)"""
        if not revenue_summary or sum(revenue_summary.values()) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="매출 데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        # 0이 아닌 값만 필터링
        filtered_data = {k: v for k, v in revenue_summary.items() if v > 0}
        
        if not filtered_data:
            fig = go.Figure()
            fig.add_annotation(
                text="매출 데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        labels = list(filtered_data.keys())
        values = list(filtered_data.values())
        
        # 매출 유형별 색상
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors[:len(labels)],
            texttemplate='%{label}<br>%{percent}',
            textposition="auto",
            textfont_size=12,
            hovertemplate='<b>%{label}</b><br>' +
                         '금액: %{value:,}원<br>' +
                         '비율: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': '매출 구성',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            showlegend=True,
            height=350,
            margin=dict(t=40, b=40, l=40, r=40),
            font=dict(family="Arial", size=11)
        )
        
        return fig
    
    def create_simple_monthly_trend(self, monthly_data: Dict[str, Any]) -> go.Figure:
        """심플한 월별 추이 차트 (매출/순이익만)"""
        if not monthly_data:
            fig = go.Figure()
            fig.add_annotation(
                text="데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            return fig
        
        # 데이터 준비
        months = sorted(monthly_data.keys())
        revenues = []
        profits = []
        
        for month in months:
            data = monthly_data[month]
            revenue = sum(data.get('매출', {}).values())
            expense = sum(data.get('매입', {}).values())
            profit = revenue - expense
            
            revenues.append(revenue)
            profits.append(profit)
        
        # 월 표시를 위한 라벨 생성
        month_labels = [f"{int(month.split('-')[1])}월" for month in months]
        
        fig = go.Figure()
        
        # 매출 막대그래프
        fig.add_trace(go.Bar(
            x=month_labels,
            y=revenues,
            name='매출',
            marker_color='#4ECDC4',
            yaxis='y',
            hovertemplate='<b>매출</b><br>' +
                         '%{x}: %{y:,}원<br>' +
                         '<extra></extra>'
        ))
        
        # 순이익 라인차트
        fig.add_trace(go.Scatter(
            x=month_labels,
            y=profits,
            mode='lines+markers',
            name='순이익',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='<b>순이익</b><br>' +
                         '%{x}: %{y:,}원<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': '월별 실적 추이',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title="월",
            yaxis=dict(
                title="매출 (원)",
                side="left",
                showgrid=True
            ),
            yaxis2=dict(
                title="순이익 (원)",
                side="right",
                overlaying="y",
                showgrid=False
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=400,
            margin=dict(t=60, b=50, l=50, r=50),
            font=dict(family="Arial", size=12),
            hovermode='x unified'
        )
        
        return fig
    
    def create_revenue_expense_comparison_chart(self, total_revenue: int, total_expense: int, net_profit: int) -> go.Figure:
        """매출 vs 매입 총액 비교 차트 생성"""
        categories = ['매출', '매입', '순이익']
        values = [total_revenue, total_expense, net_profit]
        colors = ['#4ECDC4', '#FF6B6B', '#45B7D1' if net_profit >= 0 else '#FF4444']
        
        fig = go.Figure()
        
        # 막대그래프
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f'{v:,}원' for v in values],
            textposition='auto',
            textfont_size=14,
            hovertemplate='<b>%{x}</b><br>' +
                         '금액: %{y:,}원<br>' +
                         '<extra></extra>'
        ))
        
        # 0원 기준선 추가
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title={
                'text': '연간 재무 성과 비교',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            xaxis_title="구분",
            yaxis_title="금액 (원)",
            showlegend=False,
            height=400,
            margin=dict(t=60, b=50, l=50, r=50),
            font=dict(family="Arial", size=12),
            yaxis=dict(
                tickformat=',',
                showgrid=True,
                gridcolor='lightgray'
            ),
            plot_bgcolor='white'
        )
        
        return fig
