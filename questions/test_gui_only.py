"""
GUI 전용 테스트 (OCR 없이)
수동으로 문제를 입력하여 검색 기능만 테스트
"""
import sys
from PyQt5.QtWidgets import QApplication
from search_engine import SearchEngine
from ui.main_window import MainWindow

class DummyOCR:
    """OCR 없이 테스트하기 위한 더미 클래스"""
    def capture_and_extract(self, region=None, preprocess=True):
        return "테스트 문제", None

def main():
    print("=" * 60)
    print("GUI 전용 테스트 (OCR 없이)")
    print("=" * 60)
    
    # JSON 파일 목록
    json_files = [
        'garo_questions.json',
        'kkong_questions.json',
        'olla_questions.json',
        'oxxo_questions.json'
    ]
    
    print("\n검색 엔진 초기화 중...")
    search_engine = SearchEngine(json_files)
    print(f"✓ {len(search_engine.questions):,}개 문제 로드 완료!\n")
    
    # 더미 OCR 엔진 (실제로는 사용 안 함)
    dummy_ocr = DummyOCR()
    
    # PyQt 애플리케이션 시작
    app = QApplication(sys.argv)
    
    # 메인 윈도우 생성
    window = MainWindow(dummy_ocr, search_engine)
    window.show()
    
    print("=" * 60)
    print("✓ GUI 준비 완료!")
    print("=" * 60)
    print("\n사용 방법:")
    print("1. GUI 창에서 직접 문제를 입력하세요")
    print("2. 검색 버튼을 클릭하거나 Enter 키를 누르세요")
    print("3. F9 키는 OCR이 없어서 작동하지 않습니다")
    print("\n테스트 문제 예시:")
    print("- 일반 대중을 상대로 한 흥미 위주의 잡지")
    print("- 고래는 포유류다")
    print("- 대한민국의 수도는?")
    print()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
