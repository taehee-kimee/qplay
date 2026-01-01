"""HiQuiz 문제 추출 스크립트

CSV 파일을 다운로드하여 JSON 형식으로 변환합니다.
"""
import requests
import csv
import json
import time
from typing import List, Dict
from io import StringIO


class HiQuizDownloader:
    def __init__(self):
        self.base_url = "https://hiquiz.co.kr"
        self.games = {
            'kkong': {'name': '꽁꽁', 'url': 'kkong.csv'},
            'ollao': {'name': '올라올라(꼬로록)', 'url': 'questions.csv'},
            'oxxo': {'name': 'OX,XO', 'url': 'oxxo.csv'},
            'garo': {'name': '가로세로', 'url': 'garo.csv'}
        }

    def download_csv(self, game_key: str) -> List[Dict]:
        """특정 게임의 CSV 파일을 다운로드하고 파싱합니다.
        
        Args:
            game_key: 게임 키 ('kkong', 'ollao', 'oxxo', 'garo')
            
        Returns:
            문제 리스트
        """
        game_info = self.games.get(game_key)
        if not game_info:
            print(f"✗ 알 수 없는 게임: {game_key}")
            return []
        
        csv_url = f"{self.base_url}/{game_info['url']}"
        
        try:
            print(f"다운로드 중: {csv_url}")
            response = requests.get(csv_url, timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            # CSV 파싱 - 탭 구분자 시도
            csv_content = StringIO(response.text)
            reader = csv.DictReader(csv_content, delimiter='\t')
            
            questions = []
            for idx, row in enumerate(reader, 1):
                question = row.get('Question', '').strip() if row.get('Question') else ''
                answer = row.get('Answer', '').strip() if row.get('Answer') else ''
                
                if question:  # 문제가 있는 경우만 추가
                    question_data = {
                        'id': idx,
                        'question': question,
                        'answer': answer,
                        'game': game_info['name']
                    }
                    questions.append(question_data)
            
            # 탭 구분자로 파싱 실패 시 공백 기반 파싱 시도
            if not questions:
                lines = response.text.strip().split('\n')
                for idx, line in enumerate(lines, 1):
                    parts = line.rsplit(maxsplit=1)  # 마지막 공백 기준으로 분리
                    if len(parts) == 2:
                        question_data = {
                            'id': idx,
                            'question': parts[0].strip(),
                            'answer': parts[1].strip(),
                            'game': game_info['name']
                        }
                        questions.append(question_data)
            
            print(f"✓ {len(questions)}개 문제 다운로드 완료")
            return questions
            
        except requests.exceptions.RequestException as e:
            print(f"✗ 다운로드 실패: {e}")
            return []
        except Exception as e:
            print(f"✗ 파싱 오류: {e}")
            return []

    def download_all_games(self, output_format: str = 'json') -> Dict[str, List[Dict]]:
        """모든 게임의 문제를 다운로드합니다.
        
        Args:
            output_format: 출력 형식 ('json' 또는 'csv')
            
        Returns:
            게임별 문제 딕셔너리
        """
        all_data = {}
        print("=== HiQuiz 문제 다운로드 시작 ===\n")
        
        for game_key, game_info in self.games.items():
            print(f"[{game_info['name']}] 다운로드 중...")
            questions = self.download_csv(game_key)
            
            if questions:
                all_data[game_key] = questions
                
                # 개별 파일로 저장
                if output_format == 'json':
                    self.save_as_json(questions, f"{game_key}_questions.json", game_info['name'])
                elif output_format == 'csv':
                    self.save_as_csv(questions, f"{game_key}_questions.csv")
            
            # 서버 부담 방지
            time.sleep(0.5)
            print()
        
        return all_data

    def save_as_json(self, questions: List[Dict], filename: str, game_name: str = ""):
        """JSON 형식으로 저장"""
        output_data = {
            'game': game_name,
            'total_questions': len(questions),
            'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'questions': questions
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"  → {filename} 저장 완료")

    def save_all_as_json(self, all_data: Dict[str, List[Dict]], filename: str):
        """모든 게임을 하나의 JSON 파일로 저장"""
        total_count = sum(len(questions) for questions in all_data.values())
        
        output_data = {
            'total_questions': total_count,
            'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'games': all_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== 전체 통합 파일 ===")
        print(f"✓ {filename} 저장 완료 (총 {total_count}개 문제)")

    def save_as_csv(self, questions: List[Dict], filename: str):
        """CSV 형식으로 저장"""
        if not questions:
            return
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['id', 'question', 'answer', 'game']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(questions)
        print(f"  → {filename} 저장 완료")

    def search_question(self, all_data: Dict[str, List[Dict]], keyword: str) -> List[Dict]:
        """키워드로 문제 검색"""
        results = []
        for game_key, questions in all_data.items():
            for q in questions:
                if keyword.lower() in q['question'].lower():
                    results.append(q)
        return results


def main():
    downloader = HiQuizDownloader()
    
    print("=== HiQuiz 문제 다운로드 도구 ===\n")
    print("다운로드 옵션:")
    print("1. 모든 게임 (JSON)")
    print("2. 모든 게임 (CSV)")
    print("3. 특정 게임만")
    print()
    
    choice = input("선택 (1-3): ").strip()
    
    if choice == '1':
        # 모든 게임을 JSON으로 다운로드
        all_data = downloader.download_all_games(output_format='json')
        print("\n다운로드 완료!")
        print(f"총 {sum(len(q) for q in all_data.values())}개 문제")
        
    elif choice == '2':
        # 모든 게임을 CSV로 다운로드
        all_data = downloader.download_all_games(output_format='csv')
        print("\n다운로드 완료!")
        print(f"총 {sum(len(q) for q in all_data.values())}개 문제")
        
    elif choice == '3':
        # 특정 게임만 다운로드
        print("\n게임 선택:")
        for idx, (key, info) in enumerate(downloader.games.items(), 1):
            print(f"{idx}. {info['name']} ({key})")
        
        game_choice = input("\n선택 (1-4): ").strip()
        game_keys = list(downloader.games.keys())
        
        try:
            selected_key = game_keys[int(game_choice) - 1]
            questions = downloader.download_csv(selected_key)
            
            if questions:
                downloader.save_as_json(
                    questions, 
                    f"{selected_key}_questions.json",
                    downloader.games[selected_key]['name']
                )
                print(f"\n✓ {len(questions)}개 문제 저장 완료")
        except (IndexError, ValueError):
            print("잘못된 선택입니다.")
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
