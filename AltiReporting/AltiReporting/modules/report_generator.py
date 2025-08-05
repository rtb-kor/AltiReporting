from datetime import datetime
from typing import Dict, Any, List
import pandas as pd

class ReportGenerator:
    def __init__(self):
        self.company_name = "RTB"
        self.department = "회계팀"
    
    def generate_monthly_report(self, year: int, month: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """월말 보고서 생성"""
        report = {
            'type': 'monthly',
            'period': f"{year}년 {month}월",
            'generated_at': datetime.now().isoformat(),
            'company': self.company_name,
            'department': self.department,
            'data': data,
            'summary': self._calculate_monthly_summary(data),
            'analysis': self._generate_monthly_analysis(data)
        }
        
        return report
    
    def generate_semi_annual_report(self, year: int, period: str, aggregated_data: Dict[str, Any], monthly_data: Dict[str, Any]) -> Dict[str, Any]:
        """반기 보고서 생성"""
        report = {
            'type': 'semi_annual',
            'period': f"{year}년 {period}",
            'generated_at': datetime.now().isoformat(),
            'company': self.company_name,
            'department': self.department,
            'aggregated_data': aggregated_data,
            'monthly_data': monthly_data,
            'summary': self._calculate_period_summary(aggregated_data),
            'trend_analysis': self._generate_trend_analysis(monthly_data),
            'comparison': self._generate_period_comparison(monthly_data)
        }
        
        return report
    
    def generate_annual_report(self, year: int, annual_data: Dict[str, Any], first_half: Dict[str, Any], second_half: Dict[str, Any]) -> Dict[str, Any]:
        """연말 보고서 생성"""
        report = {
            'type': 'annual',
            'period': f"{year}년",
            'generated_at': datetime.now().isoformat(),
            'company': self.company_name,
            'department': self.department,
            'annual_data': annual_data,
            'first_half': first_half,
            'second_half': second_half,
            'summary': self._calculate_annual_summary(annual_data, first_half, second_half),
            'performance_analysis': self._generate_performance_analysis(annual_data),
            'recommendations': self._generate_recommendations(annual_data)
        }
        
        return report
    
    def _calculate_monthly_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """월별 요약 계산"""
        total_revenue = sum(data.get('매출', {}).values())
        total_expense = sum(data.get('매입', {}).values())
        net_profit = total_revenue - total_expense
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'total_expense': total_expense,
            'net_profit': net_profit,
            'profit_margin': profit_margin,
            'top_revenue_source': self._get_top_revenue_source(data.get('매출', {})),
            'top_expense_item': self._get_top_expense_item(data.get('매입', {}))
        }
    
    def _calculate_period_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """기간별 요약 계산"""
        return self._calculate_monthly_summary(data)
    
    def _calculate_annual_summary(self, annual_data: Dict[str, Any], first_half: Dict[str, Any], second_half: Dict[str, Any]) -> Dict[str, Any]:
        """연간 요약 계산"""
        annual_summary = self._calculate_monthly_summary(annual_data)
        
        # 상하반기 비교
        if first_half and second_half:
            first_revenue = sum(first_half.get('매출', {}).values())
            second_revenue = sum(second_half.get('매출', {}).values())
            first_expense = sum(first_half.get('매입', {}).values())
            second_expense = sum(second_half.get('매입', {}).values())
            
            annual_summary.update({
                'first_half_revenue': first_revenue,
                'second_half_revenue': second_revenue,
                'first_half_expense': first_expense,
                'second_half_expense': second_expense,
                'revenue_growth': ((second_revenue - first_revenue) / first_revenue * 100) if first_revenue > 0 else 0,
                'expense_change': ((second_expense - first_expense) / first_expense * 100) if first_expense > 0 else 0
            })
        
        return annual_summary
    
    def _generate_monthly_analysis(self, data: Dict[str, Any]) -> List[str]:
        """월별 분석 의견 생성"""
        analysis = []
        
        revenue_data = data.get('매출', {})
        expense_data = data.get('매입', {})
        
        # 매출 분석
        top_revenue = max(revenue_data.items(), key=lambda x: x[1]) if revenue_data else ("", 0)
        if top_revenue[1] > 0:
            analysis.append(f"주요 매출처는 {top_revenue[0]}로 전체 매출의 {(top_revenue[1]/sum(revenue_data.values())*100):.1f}%를 차지합니다.")
        
        # 매입 분석
        top_expense = max(expense_data.items(), key=lambda x: x[1]) if expense_data else ("", 0)
        if top_expense[1] > 0:
            analysis.append(f"주요 매입 항목은 {top_expense[0]}로 전체 매입의 {(top_expense[1]/sum(expense_data.values())*100):.1f}%를 차지합니다.")
        
        # 수익성 분석
        total_revenue = sum(revenue_data.values())
        total_expense = sum(expense_data.values())
        profit_margin = ((total_revenue - total_expense) / total_revenue * 100) if total_revenue > 0 else 0
        
        if profit_margin > 20:
            analysis.append("수익률이 20%를 초과하여 양호한 수준입니다.")
        elif profit_margin > 10:
            analysis.append("수익률이 10-20% 범위로 적정 수준입니다.")
        else:
            analysis.append("수익률이 10% 미만으로 개선이 필요합니다.")
        
        return analysis
    
    def _generate_trend_analysis(self, monthly_data: Dict[str, Any]) -> List[str]:
        """트렌드 분석 생성"""
        analysis = []
        
        if len(monthly_data) < 2:
            return ["분석을 위한 충분한 데이터가 없습니다."]
        
        months = sorted(monthly_data.keys())
        revenues = [sum(monthly_data[month].get('매출', {}).values()) for month in months]
        
        # 매출 트렌드
        if len(revenues) >= 2:
            trend = "증가" if revenues[-1] > revenues[0] else "감소"
            change_rate = ((revenues[-1] - revenues[0]) / revenues[0] * 100) if revenues[0] > 0 else 0
            analysis.append(f"기간 내 매출이 {abs(change_rate):.1f}% {trend}했습니다.")
        
        return analysis
    
    def _generate_period_comparison(self, monthly_data: Dict[str, Any]) -> Dict[str, Any]:
        """기간별 비교 분석"""
        if len(monthly_data) < 2:
            return {}
        
        months = sorted(monthly_data.keys())
        first_month = monthly_data[months[0]]
        last_month = monthly_data[months[-1]]
        
        comparison = {
            'revenue_change': {},
            'expense_change': {}
        }
        
        # 매출 변화
        for source in first_month.get('매출', {}):
            first_amount = first_month.get('매출', {}).get(source, 0)
            last_amount = last_month.get('매출', {}).get(source, 0)
            change = last_amount - first_amount
            comparison['revenue_change'][source] = {
                'amount': change,
                'rate': (change / first_amount * 100) if first_amount > 0 else 0
            }
        
        return comparison
    
    def _generate_performance_analysis(self, annual_data: Dict[str, Any]) -> List[str]:
        """연간 성과 분석"""
        analysis = []
        
        total_revenue = sum(annual_data.get('매출', {}).values())
        total_expense = sum(annual_data.get('매입', {}).values())
        net_profit = total_revenue - total_expense
        
        # 매출 성과
        if total_revenue >= 10000000000:  # 100억 이상
            analysis.append("연간 매출 100억원을 달성하여 우수한 성과를 보였습니다.")
        elif total_revenue >= 5000000000:  # 50억 이상
            analysis.append("연간 매출 50억원을 달성하여 양호한 성과를 보였습니다.")
        
        # 수익성 분석
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        if profit_margin > 15:
            analysis.append("수익률이 15%를 초과하여 매우 양호한 수준입니다.")
        elif profit_margin > 10:
            analysis.append("수익률이 10-15% 범위로 적정 수준을 유지하고 있습니다.")
        
        return analysis
    
    def _generate_recommendations(self, annual_data: Dict[str, Any]) -> List[str]:
        """개선 제안사항"""
        recommendations = []
        
        revenue_data = annual_data.get('매출', {})
        expense_data = annual_data.get('매입', {})
        
        # 매출 다각화 제안
        total_revenue = sum(revenue_data.values())
        for source, amount in revenue_data.items():
            if amount / total_revenue > 0.5:  # 50% 이상 의존
                recommendations.append(f"{source} 의존도가 높으므로 매출 다각화를 검토해보시기 바랍니다.")
        
        # 비용 최적화 제안
        total_expense = sum(expense_data.values())
        for item, amount in expense_data.items():
            if amount / total_expense > 0.3:  # 30% 이상
                recommendations.append(f"{item} 비중이 높으므로 비용 절감 방안을 검토해보시기 바랍니다.")
        
        return recommendations
    
    def _get_top_revenue_source(self, revenue_data: Dict[str, int]) -> str:
        """최대 매출처 조회"""
        if not revenue_data:
            return ""
        return max(revenue_data.items(), key=lambda x: x[1])[0]
    
    def _get_top_expense_item(self, expense_data: Dict[str, int]) -> str:
        """최대 매입 항목 조회"""
        if not expense_data:
            return ""
        return max(expense_data.items(), key=lambda x: x[1])[0]
    
    def generate_report_text(self, report: Dict[str, Any]) -> str:
        """보고서 텍스트 생성"""
        text_lines = []
        
        # 헤더
        text_lines.append(f"=== {report['company']} {report['period']} 보고서 ===")
        text_lines.append(f"작성부서: {report['department']}")
        text_lines.append(f"작성일시: {datetime.fromisoformat(report['generated_at']).strftime('%Y년 %m월 %d일 %H:%M')}")
        text_lines.append("")
        
        # 요약
        summary = report['summary']
        text_lines.append("■ 요약")
        text_lines.append(f"• 총 매출: {summary['total_revenue']:,}원")
        text_lines.append(f"• 총 매입: {summary['total_expense']:,}원")
        text_lines.append(f"• 순이익: {summary['net_profit']:,}원")
        text_lines.append(f"• 수익률: {summary['profit_margin']:.1f}%")
        text_lines.append("")
        
        # 분석
        if 'analysis' in report:
            text_lines.append("■ 분석")
            for item in report['analysis']:
                text_lines.append(f"• {item}")
            text_lines.append("")
        
        return "\n".join(text_lines)
