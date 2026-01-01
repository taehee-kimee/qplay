# HiQuiz 문제 다운로드 도구

HiQuiz 웹사이트(https://hiquiz.co.kr)에서 게임 문제를 다운로드하여 JSON 또는 CSV 형식으로 저장하는 Python 스크립트입니다.

## 지원 게임

- 꽁꽁 (kkong)
- 올라올라(꼬로록) (ollao)
- OX (ox)
- 가로세로 (crossword)

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

```bash
python hiquiz_downloader.py
```

실행 후 다음 옵션 중 선택:
1. 모든 게임 (JSON) - 모든 게임의 문제를 JSON 형식으로 다운로드
2. 모든 게임 (CSV) - 모든 게임의 문제를 CSV 형식으로 다운로드
3. 특정 게임만 - 원하는 게임 하나만 선택하여 다운로드

## 출력 파일 형식

### JSON (개별 파일)
```json
{
  "game": "꽁꽁",
  "total_questions": 1500,
  "downloaded_at": "2026-01-01 12:00:00",
  "questions": [
    {
      "id": 1,
      "question": "문제 내용",
      "answer": "정답",
      "game": "꽁꽁"
    }
  ]
}
```

### JSON (통합 파일 - all_questions.json)
```json
{
  "total_questions": 5000,
  "downloaded_at": "2026-01-01 12:00:00",
  "games": {
    "kkong": [...],
    "ollao": [...],
    "ox": [...],
    "crossword": [...]
  }
}
```

## 생성되는 파일

- `kkong_questions.json` - 꽁꽁 게임 문제
- `ollao_questions.json` - 올라올라 게임 문제
- `ox_questions.json` - OX 게임 문제
- `crossword_questions.json` - 가로세로 게임 문제
- `all_questions.json` - 모든 게임 통합 파일
