import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any

class VisualizationManager:
    def __init__(self):
        self.color_palette = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#FFB347', '#87CEEB', '#F0E68C', '#FFE4E1'
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
                'font': {'size': 18}
            },
            showlegend=True,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            font=dict(family="Arial", size=12)
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
                'font': {'size': 18}
            },
            showlegend=True,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            font=dict(family="Arial", size=12)
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
        electronic_tax_sources = ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "General Maritime", "Jodiac", "BCKR"]
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
