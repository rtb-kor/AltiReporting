import os
import pandas as pd
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import Dict, Any
import tempfile

class ExportManager:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self._register_fonts()
    
    def _register_fonts(self):
        """한글 폰트 등록 (시스템에 있는 기본 폰트 사용)"""
        try:
            # 시스템 기본 폰트 경로들
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/System/Library/Fonts/Arial.ttf',
                '/Windows/Fonts/arial.ttf'
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Korean', font_path))
                    break
            else:
                # 폰트를 찾을 수 없는 경우 기본 폰트 사용
                print("한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
        except Exception as e:
            print(f"폰트 등록 오류: {e}")
    
    def generate_pdf_report(self, report_data: Dict[str, Any], filename: str) -> str:
        """PDF 보고서 생성"""
        filepath = os.path.join(self.temp_dir, f"{filename}.pdf")
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # 스타일 설정
        styles = getSampleStyleSheet()
        
        # 한글 지원 스타일
        try:
            title_style = ParagraphStyle(
                'KoreanTitle',
                parent=styles['Heading1'],
                fontName='Korean',
                fontSize=18,
                alignment=1,  # 중앙 정렬
                spaceAfter=30
            )
            
            heading_style = ParagraphStyle(
                'KoreanHeading',
                parent=styles['Heading2'],
                fontName='Korean',
                fontSize=14,
                spaceAfter=12
            )
            
            normal_style = ParagraphStyle(
                'KoreanNormal',
                parent=styles['Normal'],
                fontName='Korean',
                fontSize=10
            )
        except:
            # 한글 폰트가 없는 경우 기본 스타일 사용
            title_style = styles['Heading1']
            heading_style = styles['Heading2']
            normal_style = styles['Normal']
        
        story = []
        
        # 제목
        if isinstance(report_data, dict) and 'period' in report_data:
            title = f"RTB {report_data['period']} 보고서"
        else:
            title = f"RTB 보고서"
        
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # 기본 정보
        info_data = [
            ['작성일시', datetime.now().strftime('%Y년 %m월 %d일 %H:%M')],
            ['작성부서', 'RTB 회계팀'],
            ['보고기간', report_data.get('period', '') if isinstance(report_data, dict) else '']
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # 데이터 처리
        if isinstance(report_data, dict):
            self._add_report_content(story, report_data, heading_style, normal_style)
        else:
            # 단순 데이터인 경우
            self._add_simple_data_content(story, report_data, heading_style, normal_style)
        
        doc.build(story)
        return filepath
    
    def _add_report_content(self, story, report_data: Dict[str, Any], heading_style, normal_style):
        """보고서 내용 추가"""
        
        # 요약 정보
        if 'summary' in report_data:
            story.append(Paragraph("■ 요약", heading_style))
            
            summary = report_data['summary']
            summary_data = [
                ['항목', '금액'],
                ['총 매출', f"{summary.get('total_revenue', 0):,}원"],
                ['총 매입', f"{summary.get('total_expense', 0):,}원"],
                ['순이익', f"{summary.get('net_profit', 0):,}원"],
                ['수익률', f"{summary.get('profit_margin', 0):.1f}%"]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
        
        # 상세 데이터
        if 'data' in report_data:
            data = report_data['data']
            
            # 매출 데이터
            if '매출' in data:
                story.append(Paragraph("■ 매출 현황", heading_style))
                
                revenue_data = [['매출처', '금액']]
                for source, amount in data['매출'].items():
                    revenue_data.append([source, f"{amount:,}원"])
                
                revenue_table = Table(revenue_data, colWidths=[2.5*inch, 2.5*inch])
                revenue_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
                ]))
                
                story.append(revenue_table)
                story.append(Spacer(1, 15))
            
            # 매입 데이터
            if '매입' in data:
                story.append(Paragraph("■ 매입 현황", heading_style))
                
                expense_data = [['항목', '금액']]
                for item, amount in data['매입'].items():
                    expense_data.append([item, f"{amount:,}원"])
                
                expense_table = Table(expense_data, colWidths=[2.5*inch, 2.5*inch])
                expense_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
                ]))
                
                story.append(expense_table)
    
    def _add_simple_data_content(self, story, data, heading_style, normal_style):
        """단순 데이터 내용 추가"""
        if isinstance(data, dict):
            for key, value in data.items():
                story.append(Paragraph(f"■ {key}", heading_style))
                story.append(Paragraph(str(value), normal_style))
                story.append(Spacer(1, 12))
    
    def generate_excel_report(self, data: Dict[str, Any], filename: str) -> str:
        """Excel 보고서 생성"""
        filepath = os.path.join(self.temp_dir, f"{filename}.xlsx")
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # 요약 시트
            if isinstance(data, dict):
                # 매출 데이터
                if '매출' in data:
                    revenue_df = pd.DataFrame(list(data['매출'].items()), columns=['매출처', '금액'])
                    revenue_df.to_excel(writer, sheet_name='매출현황', index=False)
                
                # 매입 데이터
                if '매입' in data:
                    expense_df = pd.DataFrame(list(data['매입'].items()), columns=['항목', '금액'])
                    expense_df.to_excel(writer, sheet_name='매입현황', index=False)
                
                # 요약 정보
                total_revenue = sum(data.get('매출', {}).values())
                total_expense = sum(data.get('매입', {}).values())
                net_profit = total_revenue - total_expense
                
                summary_data = {
                    '구분': ['총 매출', '총 매입', '순이익', '수익률'],
                    '금액': [
                        total_revenue,
                        total_expense,
                        net_profit,
                        f"{(net_profit/total_revenue*100):.1f}%" if total_revenue > 0 else "0.0%"
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='요약', index=False)
        
        return filepath
    
    def generate_comparison_excel(self, period_data: Dict[str, Any], filename: str) -> str:
        """기간별 비교 Excel 생성"""
        filepath = os.path.join(self.temp_dir, f"{filename}.xlsx")
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # 월별 매출 현황
            months = sorted(period_data.keys())
            revenue_sources = ["Everllence LEO", "Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Mitsui", "Jodiac", "BCKR", "기타"]
            
            revenue_comparison = {'월': []}
            for source in revenue_sources:
                revenue_comparison[source] = []
            
            for month in months:
                month_label = f"{month.split('-')[0]}년 {int(month.split('-')[1])}월"
                revenue_comparison['월'].append(month_label)
                
                for source in revenue_sources:
                    amount = period_data[month].get('매출', {}).get(source, 0)
                    revenue_comparison[source].append(amount)
            
            revenue_df = pd.DataFrame(revenue_comparison)
            revenue_df.to_excel(writer, sheet_name='월별매출비교', index=False)
            
            # 월별 매입 현황
            expense_items = ["급여", "수당", "법인카드 사용액", "전자세금계산서", "세금", "이자", "퇴직금", "기타"]
            
            expense_comparison = {'월': []}
            for item in expense_items:
                expense_comparison[item] = []
            
            for month in months:
                month_label = f"{month.split('-')[0]}년 {int(month.split('-')[1])}월"
                expense_comparison['월'].append(month_label)
                
                for item in expense_items:
                    amount = period_data[month].get('매입', {}).get(item, 0)
                    expense_comparison[item].append(amount)
            
            expense_df = pd.DataFrame(expense_comparison)
            expense_df.to_excel(writer, sheet_name='월별매입비교', index=False)
            
            # 월별 요약
            monthly_summary = {
                '월': [],
                '총매출': [],
                '총매입': [],
                '순이익': [],
                '수익률(%)': []
            }
            
            for month in months:
                month_label = f"{month.split('-')[0]}년 {int(month.split('-')[1])}월"
                data = period_data[month]
                
                total_revenue = sum(data.get('매출', {}).values())
                total_expense = sum(data.get('매입', {}).values())
                net_profit = total_revenue - total_expense
                profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
                
                monthly_summary['월'].append(month_label)
                monthly_summary['총매출'].append(total_revenue)
                monthly_summary['총매입'].append(total_expense)
                monthly_summary['순이익'].append(net_profit)
                monthly_summary['수익률(%)'].append(round(profit_margin, 1))
            
            summary_df = pd.DataFrame(monthly_summary)
            summary_df.to_excel(writer, sheet_name='월별요약', index=False)
        
        return filepath
    
    def export_backup_data(self, all_data: Dict[str, Any], filename: str) -> str:
        """전체 데이터 백업 Excel 생성"""
        filepath = os.path.join(self.temp_dir, f"{filename}.xlsx")
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # 전체 데이터를 하나의 시트에 정리
            export_data = []
            
            for month_key, month_data in sorted(all_data.items()):
                year, month = month_key.split('-')
                
                # 매출 데이터
                for source, amount in month_data.get('매출', {}).items():
                    export_data.append({
                        '년도': int(year),
                        '월': int(month),
                        '구분': '매출',
                        '항목': source,
                        '금액': amount
                    })
                
                # 매입 데이터
                for item, amount in month_data.get('매입', {}).items():
                    export_data.append({
                        '년도': int(year),
                        '월': int(month),
                        '구분': '매입',
                        '항목': item,
                        '금액': amount
                    })
            
            df = pd.DataFrame(export_data)
            df.to_excel(writer, sheet_name='전체데이터', index=False)
            
            # 월별 요약 시트
            monthly_summaries = []
            for month_key, month_data in sorted(all_data.items()):
                year, month = month_key.split('-')
                
                total_revenue = sum(month_data.get('매출', {}).values())
                total_expense = sum(month_data.get('매입', {}).values())
                net_profit = total_revenue - total_expense
                
                monthly_summaries.append({
                    '년도': int(year),
                    '월': int(month),
                    '총매출': total_revenue,
                    '총매입': total_expense,
                    '순이익': net_profit,
                    '수익률(%)': round((net_profit / total_revenue * 100) if total_revenue > 0 else 0, 1)
                })
            
            summary_df = pd.DataFrame(monthly_summaries)
            summary_df.to_excel(writer, sheet_name='월별요약', index=False)
        
        return filepath
