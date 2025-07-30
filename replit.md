# RTB 회계 통합 보고서 시스템

## Overview

RTB 회계 통합 보고서 시스템은 Streamlit 기반의 웹 애플리케이션으로, 회계 데이터 관리 및 다양한 기간별 보고서 생성을 위한 종합적인 솔루션입니다. 이 시스템은 월말, 반기, 연말 보고서를 자동 생성하고, 데이터 시각화 및 PDF 내보내기 기능을 제공합니다.

## User Preferences

Preferred communication style: Simple, everyday language.
매출처 설정: 
- 전자세금계산서매출: Everllence Prime, SUNJIN & FMD, USNS, RENK, Vine Plant, 종합해사, Jodiac, BCKR
- 영세매출: Everllence LEO, Mitsui
- 기타매출: 기타 (동적 추가 가능)

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit을 사용한 웹 애플리케이션
- **UI Components**: 사이드바 메뉴, 대시보드, 데이터 입력 폼
- **Layout**: Wide layout with expandable sidebar for navigation
- **Session Management**: Streamlit session state를 활용한 컴포넌트 인스턴스 관리

### Backend Architecture
- **Modular Design**: 기능별로 분리된 모듈 구조
  - `data_manager.py`: 데이터 저장 및 관리
  - `report_generator.py`: 보고서 생성 로직
  - `visualization.py`: 차트 및 그래프 생성
  - `export_utils.py`: PDF 내보내기 기능

### Data Storage Solutions
- **Primary Storage**: JSON 파일 기반 로컬 저장소
- **File Structure**: `data/rtb_data.json`에 월별 데이터 저장
- **Data Format**: 계층적 JSON 구조로 매출/매입 데이터 관리

## Key Components

### 1. DataManager
- **Purpose**: 회계 데이터의 CRUD 작업 담당
- **Features**: 
  - JSON 파일 기반 데이터 저장/로드
  - 월별 데이터 관리
  - 자동 디렉토리 생성

### 2. ReportGenerator
- **Purpose**: 다양한 기간별 보고서 생성
- **Report Types**:
  - 월말 보고서: 단일 월 데이터 분석
  - 반기 보고서: 6개월 집계 및 트렌드 분석
  - 연말 보고서: 연간 종합 분석

### 3. VisualizationManager
- **Purpose**: 데이터 시각화 차트 생성
- **Library**: Plotly를 사용한 인터랙티브 차트
- **Chart Types**: 파이차트, 막대그래프, 트렌드 분석 차트

### 4. ExportManager
- **Purpose**: PDF 보고서 내보내기
- **Library**: ReportLab을 사용한 PDF 생성
- **Features**: 한글 폰트 지원, 표 및 차트 포함

## Data Flow

### 1. Data Input Flow
1. 사용자가 웹 인터페이스를 통해 매출/매입 데이터 입력
2. DataManager가 입력된 데이터를 JSON 형식으로 저장
3. 데이터 유효성 검사 및 자동 백업

### 2. Report Generation Flow
1. 사용자가 보고서 유형 및 기간 선택
2. ReportGenerator가 해당 기간 데이터 수집
3. 데이터 분석 및 요약 정보 생성
4. VisualizationManager가 차트 생성
5. 최종 보고서 화면 표시

### 3. Export Flow
1. 생성된 보고서 데이터를 ExportManager로 전달
2. PDF 형식으로 보고서 변환
3. 임시 파일 생성 및 다운로드 제공

## External Dependencies

### Core Libraries
- **streamlit**: 웹 애플리케이션 프레임워크
- **pandas**: 데이터 조작 및 분석
- **plotly**: 인터랙티브 데이터 시각화
- **reportlab**: PDF 생성 및 문서 처리

### System Dependencies
- **Python 3.7+**: 기본 런타임 환경
- **OS Module**: 파일 시스템 접근
- **JSON**: 데이터 직렬화
- **DateTime**: 날짜 및 시간 처리

### Font Dependencies
- 시스템 폰트 경로를 통한 한글 폰트 지원
- DejaVu, Arial 등 크로스 플랫폼 폰트 사용

## Deployment Strategy

### Local Development
- **Environment**: Python 가상환경 권장
- **Command**: `streamlit run app.py`
- **Port**: 기본 8501 포트 사용

### Production Considerations
- **File Storage**: JSON 파일 기반이므로 데이터 백업 전략 필요
- **Scalability**: 대용량 데이터 처리 시 데이터베이스 마이그레이션 고려
- **Security**: 회계 데이터 보안을 위한 인증 시스템 추가 필요

### Configuration
- **Data Directory**: `data/` 폴더 자동 생성
- **Temp Files**: 시스템 임시 디렉토리 사용
- **Session State**: Streamlit 내장 세션 관리 활용

### Performance Optimization
- 모듈별 인스턴스를 session state에 캐싱
- JSON 파일 크기 최적화를 위한 데이터 구조 설계
- 필요시 데이터베이스 마이그레이션 경로 확보