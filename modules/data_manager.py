import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class DataManager:
    def __init__(self, data_file="data/rtb_data.json"):
        self.data_file = data_file
        self.ensure_data_directory()
        self.data = self.load_data()
    
    def ensure_data_directory(self):
        """데이터 디렉토리가 없으면 생성"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def load_data(self) -> Dict[str, Any]:
        """JSON 파일에서 데이터 로드"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"데이터 로드 오류: {e}")
            return {}
    
    def save_data(self):
        """데이터를 JSON 파일에 저장"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"데이터 저장 오류: {e}")
    
    def save_month_data(self, month_key: str, data: Dict[str, Any]):
        """특정 월의 데이터 저장"""
        self.data[month_key] = data
        self.save_data()
    
    def get_month_data(self, month_key: str) -> Dict[str, Any]:
        """특정 월의 데이터 조회"""
        return self.data.get(month_key, {})
    
    def get_all_data(self) -> Dict[str, Any]:
        """모든 데이터 조회"""
        return self.data
    
    def delete_month_data(self, month_key: str):
        """특정 월의 데이터 삭제"""
        if month_key in self.data:
            del self.data[month_key]
            self.save_data()
    
    def aggregate_period_data(self, period_data: Dict[str, Any]) -> Dict[str, Any]:
        """기간별 데이터 집계"""
        aggregated = {
            '매출': {},
            '매입': {}
        }
        
        # 매출처별 집계 (전자세금계산서매출 + 영세매출 + 기타)
        electronic_tax_sources = ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR"]
        zero_rated_sources = ["Everllence LEO", "Mitsui"]
        other_sources = ["기타"]
        revenue_sources = electronic_tax_sources + [s for s in zero_rated_sources if s not in electronic_tax_sources] + other_sources
        for source in revenue_sources:
            total = 0
            for month_data in period_data.values():
                total += month_data.get('매출', {}).get(source, 0)
            aggregated['매출'][source] = total
        
        # 매입 항목별 집계
        expense_items = ["급여", "수당", "법인카드 사용액", "전자세금계산서", "세금", "이자", "퇴직금", "기타"]
        for item in expense_items:
            total = 0
            for month_data in period_data.values():
                total += month_data.get('매입', {}).get(item, 0)
            aggregated['매입'][item] = total
        
        return aggregated
    
    def get_year_data(self, year: int) -> Dict[str, Any]:
        """특정 연도의 모든 데이터 조회"""
        year_data = {}
        for month_key, data in self.data.items():
            if month_key.startswith(str(year)):
                year_data[month_key] = data
        return year_data
    
    def get_period_data(self, year: int, start_month: int, end_month: int) -> Dict[str, Any]:
        """특정 기간의 데이터 조회"""
        period_data = {}
        for month in range(start_month, end_month + 1):
            month_key = f"{year}-{month:02d}"
            if month_key in self.data:
                period_data[month_key] = self.data[month_key]
        return period_data
    
    def backup_data(self) -> str:
        """데이터 백업 파일 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"data/rtb_backup_{timestamp}.json"
        
        try:
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return backup_filename
        except Exception as e:
            print(f"백업 오류: {e}")
            return ""
    
    def restore_data(self, backup_data: Dict[str, Any]):
        """백업 데이터로 복원"""
        self.data = backup_data
        self.save_data()
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """데이터 유효성 검증"""
        required_keys = ['매출', '매입']
        
        for key in required_keys:
            if key not in data:
                return False
        
        # 매출처 검증 (전자세금계산서매출 + 영세매출 + 기타)
        electronic_tax_sources = ["Everllence Prime", "SUNJIN & FMD", "USNS", "RENK", "Vine Plant", "종합해사", "Jodiac", "BCKR"]
        zero_rated_sources = ["Everllence LEO", "Mitsui"]
        other_sources = ["기타"]
        required_revenue_sources = electronic_tax_sources + [s for s in zero_rated_sources if s not in electronic_tax_sources] + other_sources
        for source in required_revenue_sources:
            if source not in data.get('매출', {}):
                data['매출'][source] = 0
        
        # 매입 항목 검증
        required_expense_items = ["급여", "수당", "법인카드 사용액", "전자세금계산서", "세금", "이자", "퇴직금", "기타"]
        for item in required_expense_items:
            if item not in data.get('매입', {}):
                data['매입'][item] = 0
        
        return True
    
    def get_monthly_comparison(self, year: int, month: int) -> Dict[str, Any]:
        """전월 대비 분석"""
        current_key = f"{year}-{month:02d}"
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_key = f"{prev_year}-{prev_month:02d}"
        
        current_data = self.get_month_data(current_key)
        prev_data = self.get_month_data(prev_key)
        
        if not current_data or not prev_data:
            return {}
        
        comparison = {
            '현재월': current_data,
            '전월': prev_data,
            '증감': {
                '매출': {},
                '매입': {}
            }
        }
        
        # 매출 증감 계산
        for source in current_data.get('매출', {}):
            current_amount = current_data.get('매출', {}).get(source, 0)
            prev_amount = prev_data.get('매출', {}).get(source, 0)
            comparison['증감']['매출'][source] = current_amount - prev_amount
        
        # 매입 증감 계산
        for item in current_data.get('매입', {}):
            current_amount = current_data.get('매입', {}).get(item, 0)
            prev_amount = prev_data.get('매입', {}).get(item, 0)
            comparison['증감']['매입'][item] = current_amount - prev_amount
        
        return comparison
