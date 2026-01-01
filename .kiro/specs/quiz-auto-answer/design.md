# Design Document: Quiz Auto-Answer System

## Overview

The Quiz Auto-Answer System is a desktop application that captures quiz questions from game screens, recognizes text using OCR, and displays answers in real-time through a transparent overlay interface. The system prioritizes speed (<1 second total processing) and accuracy (95%+ OCR recognition) while maintaining minimal resource usage.

The application uses embedded Tesseract OCR for offline text recognition, RapidFuzz for high-performance fuzzy string matching, and PyQt5 for the GUI with transparent overlay capabilities. All components are bundled for standalone deployment without requiring API keys or external services.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Overlay    │  │   Region     │  │   Settings   │      │
│  │   Window     │  │   Selector   │  │   Dialog     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Core Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auto Search  │  │   Hotkey     │  │   Config     │      │
│  │   Manager    │  │   Manager    │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Processing Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Screen       │  │     OCR      │  │   Search     │      │
│  │ Capture      │  │   Engine     │  │   Engine     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Question    │  │  User Added  │  │   Region     │      │
│  │  Database    │  │  Questions   │  │   Config     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Processing Pipeline

```
User Action (Start/Hotkey)
         │
         ▼
┌─────────────────┐
│ Screen Capture  │ ← ROI coordinates from config
│   (mss lib)     │
└────────┬────────┘
         │ Raw image (numpy array)
         ▼
┌─────────────────┐
│ Preprocessing   │ ← Settings: brightness, contrast, threshold
│  (OpenCV/PIL)   │
└────────┬────────┘
         │ Enhanced image
         ▼
┌─────────────────┐
│  OCR Engine     │ ← Tesseract + kor.traineddata
│  (pytesseract)  │
└────────┬────────┘
         │ Extracted text + confidence
         ▼
┌─────────────────┐
│ Text Cleanup    │ ← Remove whitespace, normalize
│                 │
└────────┬────────┘
         │ Cleaned question text
         ▼
┌─────────────────┐
│ Search Engine   │ ← Question database in memory
│  (RapidFuzz)    │
└────────┬────────┘
         │ Answer(s) + match confidence
         ▼
┌─────────────────┐
│ UI Update       │ ← Display in overlay window
│  (PyQt5)        │
└─────────────────┘
```

## Components and Interfaces

### 1. Screen Capture Module (`screen_capture.py`)

**Purpose**: Captures specific screen regions efficiently

**Key Classes**:
- `ScreenCapture`: Handles screen capture operations

**Methods**:
```python
class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()  # Fast screen capture library
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        Captures a specific screen region and returns as numpy array.
        
        Args:
            x, y: Top-left coordinates
            width, height: Region dimensions
            
        Returns:
            numpy array in BGR format (OpenCV compatible)
            
        Performance: ~50-100ms
        """
        pass
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Returns primary monitor dimensions"""
        pass
```

**Technology**: `mss` library (faster than PIL/pyautogui for repeated captures)

**Performance Target**: <100ms per capture

### 2. OCR Engine Module (`ocr_engine.py`)

**Purpose**: Extracts Korean text from images with high accuracy

**Key Classes**:
- `OCREngine`: Manages Tesseract OCR operations
- `ImagePreprocessor`: Applies enhancement techniques

**Methods**:
```python
class ImagePreprocessor:
    @staticmethod
    def preprocess(image: np.ndarray, config: dict) -> np.ndarray:
        """
        Applies preprocessing pipeline to enhance OCR accuracy.
        
        Pipeline:
        1. Grayscale conversion
        2. Noise reduction (Gaussian blur)
        3. Contrast enhancement (CLAHE)
        4. Binarization (Otsu's method or adaptive threshold)
        5. Morphological operations (optional)
        
        Args:
            image: Input image as numpy array
            config: Preprocessing parameters
                - brightness: -100 to 100
                - contrast: 0.5 to 3.0
                - blur_kernel: 1, 3, 5 (odd numbers)
                - threshold_method: 'otsu' or 'adaptive'
                
        Returns:
            Preprocessed image optimized for OCR
            
        Performance: ~100-200ms
        """
        pass

class OCREngine:
    def __init__(self, tesseract_path: str = None):
        """
        Initializes OCR engine with embedded Tesseract.
        
        Args:
            tesseract_path: Path to tesseract.exe (auto-detected if None)
        """
        self.tesseract_path = tesseract_path or self._find_tesseract()
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        self.preprocessor = ImagePreprocessor()
    
    def extract_text(self, image: np.ndarray, 
                    preprocess: bool = True,
                    config: dict = None) -> Tuple[str, float]:
        """
        Extracts text from image using Tesseract OCR.
        
        Args:
            image: Input image as numpy array
            preprocess: Whether to apply preprocessing
            config: Preprocessing configuration
            
        Returns:
            Tuple of (extracted_text, confidence_score)
            confidence_score: 0-100 indicating OCR confidence
            
        Tesseract Config:
            - lang: kor (Korean)
            - psm: 6 (Assume uniform block of text)
            - oem: 3 (Default, based on what is available)
            
        Performance: ~300-500ms
        """
        pass
    
    def _find_tesseract(self) -> str:
        """
        Locates embedded Tesseract executable.
        Search order:
        1. ./tesseract/tesseract.exe (bundled with app)
        2. System PATH
        3. Common installation paths
        """
        pass
```

**Preprocessing Techniques** (based on research):
1. **Grayscale Conversion**: Reduces complexity while preserving text information
2. **Noise Reduction**: Gaussian blur with small kernel (3x3 or 5x5) to remove artifacts
3. **Contrast Enhancement**: CLAHE (Contrast Limited Adaptive Histogram Equalization) for better text visibility
4. **Binarization**: Otsu's method for automatic threshold selection, or adaptive thresholding for varying lighting
5. **Morphological Operations**: Optional closing/opening to connect broken characters

**Technology**: 
- Tesseract OCR 4.x with Korean language data
- OpenCV for preprocessing
- pytesseract Python wrapper

**Performance Target**: <500ms total (including preprocessing)

### 3. Search Engine Module (`search_engine.py`)

**Purpose**: Fast and fuzzy question-answer matching

**Key Classes**:
- `SearchEngine`: Manages question database and search operations
- `QuestionIndex`: Optimized data structure for fast lookups

**Methods**:
```python
class QuestionIndex:
    def __init__(self):
        self.exact_match_dict = {}  # Hash map for O(1) exact matches
        self.questions_list = []    # List for fuzzy matching
        self.game_indices = {}      # Game-specific indices
    
    def add_question(self, question: str, answer: str, game: str):
        """Adds question to index structures"""
        # Normalize: lowercase, remove whitespace/punctuation
        normalized = self._normalize(question)
        self.exact_match_dict[normalized] = {
            'answer': answer,
            'original': question,
            'game': game
        }
        self.questions_list.append({
            'normalized': normalized,
            'answer': answer,
            'original': question,
            'game': game
        })

class SearchEngine:
    def __init__(self, json_files: List[str]):
        """
        Loads question database into memory.
        
        Args:
            json_files: List of JSON file paths to load
            
        Performance: ~1-2 seconds for 10,000 questions
        """
        self.index = QuestionIndex()
        self._load_questions(json_files)
    
    def search(self, query: str, 
              game_filter: str = None,
              threshold: int = 80) -> List[dict]:
        """
        Searches for answers using multi-stage matching.
        
        Matching Strategy:
        1. Exact match (after normalization) - O(1)
        2. Fuzzy match using RapidFuzz - O(n) but optimized
        
        Args:
            query: Question text from OCR
            game_filter: Optional game name to filter results
            threshold: Minimum similarity score (0-100)
            
        Returns:
            List of matches sorted by confidence:
            [
                {
                    'question': 'Original question',
                    'answer': 'Answer text',
                    'confidence': 95,  # Match quality 0-100
                    'game': 'kkong'
                }
            ]
            
        Performance: <100ms for exact match, <200ms for fuzzy match
        """
        normalized_query = self._normalize(query)
        
        # Stage 1: Exact match
        if normalized_query in self.index.exact_match_dict:
            result = self.index.exact_match_dict[normalized_query]
            return [{
                'question': result['original'],
                'answer': result['answer'],
                'confidence': 100,
                'game': result['game']
            }]
        
        # Stage 2: Fuzzy match using RapidFuzz
        candidates = self.index.questions_list
        if game_filter:
            candidates = [q for q in candidates if q['game'] == game_filter]
        
        # Use RapidFuzz for fast fuzzy matching
        matches = process.extract(
            normalized_query,
            [q['normalized'] for q in candidates],
            scorer=fuzz.ratio,
            limit=5
        )
        
        results = []
        for match_text, score, idx in matches:
            if score >= threshold:
                q = candidates[idx]
                results.append({
                    'question': q['original'],
                    'answer': q['answer'],
                    'confidence': score,
                    'game': q['game']
                })
        
        return results
    
    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalizes text for matching.
        - Lowercase
        - Remove whitespace
        - Remove punctuation
        - Strip leading/trailing spaces
        """
        pass
```

**Technology**: 
- RapidFuzz library (faster than python-Levenshtein, O([N/64]M) complexity)
- Hash tables for exact matching
- In-memory database for speed

**Performance Target**: <100ms per search

### 4. Auto Search Manager Module (`auto_search_manager.py`)

**Purpose**: Manages continuous automatic question recognition

**Key Classes**:
- `AutoSearchManager`: Controls the auto-search loop

**Methods**:
```python
class AutoSearchManager(QObject):
    # Qt signals for thread-safe UI updates
    result_ready = pyqtSignal(dict)  # Emits search results
    status_changed = pyqtSignal(str)  # Emits status messages
    
    def __init__(self, screen_capture, ocr_engine, search_engine, config_manager):
        super().__init__()
        self.screen_capture = screen_capture
        self.ocr_engine = ocr_engine
        self.search_engine = search_engine
        self.config = config_manager
        
        self.is_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self._search_cycle)
        
        self.last_question = ""  # Cache for duplicate detection
        self.last_result = None
    
    def start(self):
        """Starts continuous auto-search"""
        if self.is_running:
            return
        
        self.is_running = True
        interval_ms = self.config.get('auto_search_interval', 1.0) * 1000
        self.timer.start(int(interval_ms))
        self.status_changed.emit("Auto-searching...")
    
    def pause(self):
        """Pauses auto-search"""
        self.is_running = False
        self.timer.stop()
        self.status_changed.emit("Paused")
    
    def _search_cycle(self):
        """
        Single search cycle executed at configured interval.
        
        Steps:
        1. Capture screen region
        2. Extract text via OCR
        3. Check if question changed
        4. Search for answer if new question
        5. Emit results to UI
        
        Performance: <1 second total
        """
        try:
            # Get ROI from config
            roi = self.config.get_current_roi()
            if not roi:
                return
            
            # Capture screen
            image = self.screen_capture.capture_region(**roi)
            
            # OCR extraction
            question, ocr_confidence = self.ocr_engine.extract_text(
                image,
                preprocess=self.config.get('ocr_preprocess', True),
                config=self.config.get('ocr_config', {})
            )
            
            # Skip if same question
            if question == self.last_question:
                return
            
            self.last_question = question
            
            # Search for answer
            game_filter = self.config.get('current_game')
            results = self.search_engine.search(
                question,
                game_filter=game_filter,
                threshold=self.config.get('search_threshold', 80)
            )
            
            # Emit results
            self.result_ready.emit({
                'question': question,
                'ocr_confidence': ocr_confidence,
                'results': results,
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            logging.error(f"Auto-search cycle error: {e}")
            # Continue running despite errors
```

**Technology**: 
- QTimer for non-blocking periodic execution
- Qt signals for thread-safe communication
- Exception handling to prevent crashes

**Performance Target**: Configurable interval (0.5-5 seconds), <1 second per cycle

### 5. Region Selector Module (`region_selector.py`)

**Purpose**: Interactive screen region selection

**Key Classes**:
- `RegionSelectorWindow`: Full-screen overlay for region selection

**Methods**:
```python
class RegionSelectorWindow(QWidget):
    region_selected = pyqtSignal(dict)  # Emits {x, y, width, height}
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Capture full screen
        self.screenshot = self._capture_full_screen()
        
        # Selection state
        self.start_pos = None
        self.current_pos = None
        self.is_selecting = False
    
    def showFullScreen(self):
        """Displays full-screen semi-transparent overlay"""
        super().showFullScreen()
    
    def mousePressEvent(self, event):
        """Records selection start point"""
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.is_selecting = True
    
    def mouseMoveEvent(self, event):
        """Updates selection rectangle during drag"""
        if self.is_selecting:
            self.current_pos = event.pos()
            self.update()  # Triggers repaint
    
    def mouseReleaseEvent(self, event):
        """Finalizes selection and emits coordinates"""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            
            # Calculate rectangle
            x1, y1 = self.start_pos.x(), self.start_pos.y()
            x2, y2 = self.current_pos.x(), self.current_pos.y()
            
            x = min(x1, x2)
            y = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            self.region_selected.emit({
                'x': x,
                'y': y,
                'width': width,
                'height': height
            })
            
            self.close()
    
    def paintEvent(self, event):
        """Draws semi-transparent overlay and selection rectangle"""
        painter = QPainter(self)
        
        # Draw screenshot with dark overlay
        painter.drawPixmap(0, 0, self.screenshot)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))
        
        # Draw selection rectangle
        if self.start_pos and self.current_pos:
            rect = QRect(self.start_pos, self.current_pos).normalized()
            
            # Red border
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawRect(rect)
            
            # Clear interior to show original screenshot
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)
```

**Technology**: 
- PyQt5 for GUI
- Custom paint events for visual feedback
- Mouse events for drag selection

### 6. Overlay Window Module (`ui/overlay_window.py`)

**Purpose**: Always-on-top transparent window displaying results

**Key Classes**:
- `OverlayWindow`: Main result display window

**Methods**:
```python
class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Window flags for always-on-top transparent window
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._setup_ui()
        self._opacity = 0.8  # Default 80%
    
    def _setup_ui(self):
        """Creates UI layout"""
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: gray; font-size: 10pt;")
        
        # Question label (small, blue)
        self.question_label = QLabel("")
        self.question_label.setStyleSheet(
            "color: #2196F3; font-size: 11pt; "
            "background: rgba(255,255,255,200); "
            "padding: 5px; border-radius: 3px;"
        )
        self.question_label.setWordWrap(True)
        
        # Answer label (large, green, bold)
        self.answer_label = QLabel("")
        self.answer_label.setStyleSheet(
            "color: #4CAF50; font-size: 18pt; font-weight: bold; "
            "background: rgba(255,255,255,220); "
            "padding: 10px; border-radius: 5px;"
        )
        self.answer_label.setWordWrap(True)
        
        # Confidence labels
        self.confidence_label = QLabel("")
        self.confidence_label.setStyleSheet("color: gray; font-size: 9pt;")
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶ Start")
        self.start_button.setStyleSheet(
            "background: #4CAF50; color: white; "
            "font-weight: bold; padding: 8px;"
        )
        
        self.pause_button = QPushButton("⏸ Pause")
        self.pause_button.setStyleSheet(
            "background: #f44336; color: white; "
            "font-weight: bold; padding: 8px;"
        )
        self.pause_button.setEnabled(False)
        
        self.copy_button = QPushButton("📋 Copy")
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.copy_button)
        
        # Transparency slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.valueChanged.connect(self._update_opacity)
        slider_layout.addWidget(self.opacity_slider)
        
        # Add all to main layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.question_label)
        layout.addWidget(self.answer_label)
        layout.addWidget(self.confidence_label)
        layout.addLayout(button_layout)
        layout.addLayout(slider_layout)
        
        self.setLayout(layout)
        self.setMinimumWidth(400)
    
    def update_result(self, result: dict):
        """
        Updates display with new search result.
        
        Args:
            result: {
                'question': str,
                'ocr_confidence': float,
                'results': List[dict],
                'timestamp': datetime
            }
        """
        self.question_label.setText(f"Q: {result['question']}")
        
        if result['results']:
            # Show all answers separated by " / "
            answers = " / ".join([r['answer'] for r in result['results']])
            self.answer_label.setText(answers)
            
            # Show confidence scores
            ocr_conf = result['ocr_confidence']
            search_conf = result['results'][0]['confidence']
            self.confidence_label.setText(
                f"OCR: {ocr_conf:.0f}% | Match: {search_conf:.0f}% | "
                f"{result['timestamp'].strftime('%H:%M:%S')}"
            )
        else:
            self.answer_label.setText("No match found")
            self.confidence_label.setText(
                f"OCR: {result['ocr_confidence']:.0f}% | "
                f"{result['timestamp'].strftime('%H:%M:%S')}"
            )
    
    def _update_opacity(self, value):
        """Updates window opacity"""
        self._opacity = value / 100.0
        self.setWindowOpacity(self._opacity)
```

**Technology**: 
- PyQt5 with custom styling
- Window flags for always-on-top behavior
- Translucent background with opaque widgets

### 7. Configuration Manager Module (`config_manager.py`)

**Purpose**: Manages application settings and persistence

**Key Classes**:
- `ConfigManager`: Handles configuration loading/saving

**Configuration Structure**:
```json
{
  "current_game": "kkong",
  "games": {
    "kkong": {
      "name": "꽁꽁",
      "roi": {"x": 100, "y": 200, "width": 800, "height": 100}
    },
    "ollao": {
      "name": "올라올라",
      "roi": {"x": 150, "y": 250, "width": 750, "height": 120}
    }
  },
  "ocr_config": {
    "preprocess": true,
    "brightness": 0,
    "contrast": 1.2,
    "blur_kernel": 3,
    "threshold_method": "otsu"
  },
  "auto_search_interval": 1.0,
  "search_threshold": 80,
  "hotkey": "F9",
  "window_opacity": 0.8,
  "window_position": {"x": 100, "y": 100}
}
```

**Methods**:
```python
class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_or_create_default()
    
    def get(self, key: str, default=None):
        """Gets configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Sets configuration value and saves"""
        self.config[key] = value
        self.save()
    
    def get_current_roi(self) -> dict:
        """Gets ROI for currently selected game"""
        game = self.config.get('current_game')
        if game and game in self.config['games']:
            return self.config['games'][game].get('roi')
        return None
    
    def save_roi(self, game: str, roi: dict):
        """Saves ROI for specific game"""
        if game not in self.config['games']:
            self.config['games'][game] = {'name': game}
        self.config['games'][game]['roi'] = roi
        self.save()
    
    def save(self):
        """Persists configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
```

## Data Models

### Question Entry
```python
@dataclass
class QuestionEntry:
    id: int
    question: str
    answer: str
    game: str
    source: str = "main"  # "main" or "user_added"
```

### Search Result
```python
@dataclass
class SearchResult:
    question: str
    answer: str
    confidence: float  # 0-100
    game: str
```

### OCR Result
```python
@dataclass
class OCRResult:
    text: str
    confidence: float  # 0-100
    processing_time: float  # seconds
```

### ROI Configuration
```python
@dataclass
class ROI:
    x: int
    y: int
    width: int
    height: int
    
    def to_dict(self) -> dict:
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies and consolidations:

**Redundancies Eliminated:**
- Properties 11.2 and 11.3 (OCR and search confidence display) are subsumed by Property 5.7 (show both confidence scores)
- Properties 3.4 and 9.4 (question comparison and caching) describe the same behavior - consolidated into one property
- Properties 2.6 and 2.7 (OCR returns confidence + flags low confidence) can be combined into one comprehensive property about OCR output structure

**Properties Combined:**
- Region persistence (1.3, 1.4, 1.5) consolidated into comprehensive ROI management property
- Search strategy (4.3, 4.4) combined into one property about search order
- Error recovery properties (12.1, 12.2, 12.5) consolidated into general error handling property

This reflection ensures each property provides unique validation value without logical redundancy.

### Core Properties

**Property 1: ROI Configuration Persistence**
*For any* game and ROI coordinates, when saved to configuration, switching to that game should load the exact same coordinates, and each game should maintain independent ROI settings.
**Validates: Requirements 1.3, 1.4, 1.5**

**Property 2: OCR Preprocessing Application**
*For any* image and preprocessing configuration, when preprocessing is enabled, the OCR engine should apply the configured brightness, contrast, and threshold values before text extraction.
**Validates: Requirements 2.2, 2.5**

**Property 3: OCR Performance Constraint**
*For any* image input, the OCR text extraction should complete within 500 milliseconds.
**Validates: Requirements 2.4**

**Property 4: OCR Output Structure**
*For any* OCR operation, the result should include both extracted text and a confidence score (0-100), and if confidence is below 70%, the result should be flagged as low confidence.
**Validates: Requirements 2.6, 2.7**

**Property 5: Auto-Search Duplicate Detection**
*For any* two consecutive auto-search cycles, if the recognized question text is identical to the previous question, the search operation should be skipped and no new search should be performed.
**Validates: Requirements 3.4, 3.5, 9.4**

**Property 6: Auto-Search Status Synchronization**
*For any* state change in the auto-search manager (started or paused), the UI should display the corresponding status message ("Auto-searching..." or "Paused") immediately.
**Validates: Requirements 3.6, 11.1**

**Property 7: Search Interval Bounds**
*For any* configured search interval value, if the value is between 0.5 and 5 seconds (inclusive), it should be accepted; otherwise it should be rejected or clamped to the valid range.
**Validates: Requirements 3.7**

**Property 8: Search Performance Constraint**
*For any* search query, the search engine should return results within 100 milliseconds.
**Validates: Requirements 4.2**

**Property 9: Search Strategy Order**
*For any* search query, the search engine should first attempt exact string matching (after normalization), and only if no exact match is found, should it proceed to fuzzy matching using Levenshtein distance.
**Validates: Requirements 4.3, 4.4**

**Property 10: Search Normalization Invariance**
*For any* two strings that differ only in whitespace, special characters, or case, the search engine should treat them as equivalent during matching.
**Validates: Requirements 4.5**

**Property 11: Game Filter Enforcement**
*For any* search query with a game filter specified, all returned results should only include questions from that specific game.
**Validates: Requirements 4.6**

**Property 12: Search Result Completeness**
*For any* search query that matches multiple questions, the search engine should return all matching answers (not just the first match).
**Validates: Requirements 4.7**

**Property 13: Search Confidence Scoring**
*For any* search result, each match should include a confidence score between 0 and 100 indicating match quality.
**Validates: Requirements 4.8**

**Property 14: Search No-Match Handling**
*For any* search query that matches no questions in the database, the search engine should return a result indicating "No match found" rather than an empty result or error.
**Validates: Requirements 4.9**

**Property 15: Overlay Opacity Range**
*For any* opacity value between 10% and 100%, the overlay window should accept and apply that opacity level; values outside this range should be clamped to the nearest valid value.
**Validates: Requirements 5.2**

**Property 16: Overlay Opacity Responsiveness**
*For any* change to the transparency slider value, the overlay window opacity should update immediately without requiring confirmation or restart.
**Validates: Requirements 5.4**

**Property 17: Result Display Completeness**
*For any* search result displayed in the overlay, the window should show both OCR confidence and search match confidence scores, the currently selected game name, and the timestamp of the result.
**Validates: Requirements 5.7, 5.8, 5.9**

**Property 18: Multiple Answer Formatting**
*For any* search result containing multiple answers, the overlay window should display all answers joined with " / " as the separator.
**Validates: Requirements 5.10**

**Property 19: Question Persistence**
*For any* valid question submission (non-empty question and answer fields), the system should save the question to the user_added.json file and make it immediately available for future searches.
**Validates: Requirements 7.2, 7.6**

**Property 20: Settings Persistence**
*For any* configuration change made through the settings interface, the system should save the updated configuration to the config file immediately.
**Validates: Requirements 8.5**

**Property 21: Full Cycle Performance**
*For any* complete recognition cycle (capture → OCR → search → display), the total processing time should not exceed 1 second.
**Validates: Requirements 9.2**

**Property 22: Paused State Inactivity**
*For any* time period while auto-search is in the paused state, the system should not perform any screen captures or OCR operations.
**Validates: Requirements 9.3**

**Property 23: Embedded Resource Location**
*For any* installation directory, the system should successfully locate the embedded Tesseract executable and Korean language data using paths relative to the executable location.
**Validates: Requirements 10.5**

**Property 24: Low Confidence Warning**
*For any* OCR result with confidence below 70%, the overlay window should display a warning indicator alongside the result.
**Validates: Requirements 11.4**

**Property 25: Timestamp Display**
*For any* successful recognition operation, the overlay window should display the timestamp of when the recognition occurred.
**Validates: Requirements 11.6**

**Property 26: Error Recovery Continuity**
*For any* error that occurs during auto-search (screen capture failure, OCR failure, or search failure), the system should log the error and continue with the next search cycle without stopping the auto-search loop.
**Validates: Requirements 12.1, 12.2, 12.5**

**Property 27: Error Logging**
*For any* error that occurs in the system, an entry should be written to the error log file with timestamp, error type, and error message.
**Validates: Requirements 12.6**

## Error Handling

### Error Categories and Recovery Strategies

**1. Screen Capture Errors**
- **Causes**: Invalid ROI coordinates, display disconnected, permission denied
- **Recovery**: Log error, skip current cycle, continue auto-search
- **User Feedback**: Show error message in overlay, suggest ROI reconfiguration

**2. OCR Processing Errors**
- **Causes**: Tesseract not found, corrupted image data, out of memory
- **Recovery**: Log error, return empty result with 0% confidence
- **User Feedback**: Display error message, provide troubleshooting steps

**3. Search Engine Errors**
- **Causes**: Database file missing/corrupted, invalid query format
- **Recovery**: Log error, return "No match found" result
- **User Feedback**: Show error in overlay, prompt to check database files

**4. Configuration Errors**
- **Causes**: Invalid config file, missing required fields, type mismatches
- **Recovery**: Load default configuration, save corrected config
- **User Feedback**: Notify user of config reset, show defaults applied

**5. File I/O Errors**
- **Causes**: Permission denied, disk full, file locked
- **Recovery**: Retry with exponential backoff (3 attempts)
- **User Feedback**: Show specific error message, suggest solutions

### Error Logging Format

```python
{
    "timestamp": "2026-01-01T12:34:56.789",
    "level": "ERROR",
    "component": "OCREngine",
    "error_type": "TesseractNotFound",
    "message": "Tesseract executable not found at expected path",
    "details": {
        "expected_path": "./tesseract/tesseract.exe",
        "search_paths": ["./tesseract", "C:/Program Files/Tesseract-OCR"]
    },
    "stack_trace": "..."
}
```

## Testing Strategy

### Dual Testing Approach

The system will be validated using both unit tests and property-based tests, as they serve complementary purposes:

**Unit Tests**: Verify specific examples, edge cases, and integration points
- Specific UI interactions (button clicks, slider movements)
- Configuration file loading/saving with known data
- Error conditions with specific inputs
- Integration between components

**Property-Based Tests**: Verify universal properties across all inputs
- OCR performance with randomly generated images
- Search matching with random question variations
- Configuration persistence with random settings
- ROI coordinate handling with random screen regions

### Property-Based Testing Configuration

**Framework**: Hypothesis (Python property-based testing library)

**Test Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with feature name and property number
- Tag format: `# Feature: quiz-auto-answer, Property N: [property description]`

**Example Property Test Structure**:
```python
from hypothesis import given, strategies as st
import pytest

@given(
    x=st.integers(min_value=0, max_value=1920),
    y=st.integers(min_value=0, max_value=1080),
    width=st.integers(min_value=100, max_value=800),
    height=st.integers(min_value=50, max_value=400)
)
@pytest.mark.property_test
def test_roi_persistence(x, y, width, height):
    """
    Feature: quiz-auto-answer, Property 1: ROI Configuration Persistence
    
    For any game and ROI coordinates, when saved to configuration,
    switching to that game should load the exact same coordinates.
    """
    config = ConfigManager(temp_config_file)
    game = "test_game"
    roi = {'x': x, 'y': y, 'width': width, 'height': height}
    
    # Save ROI
    config.save_roi(game, roi)
    
    # Switch game and load
    config.set('current_game', game)
    loaded_roi = config.get_current_roi()
    
    # Verify exact match
    assert loaded_roi == roi
```

### Test Coverage Goals

**Component Coverage**:
- Screen Capture: 90%+ code coverage
- OCR Engine: 85%+ (excluding Tesseract internals)
- Search Engine: 95%+ (core logic)
- Auto Search Manager: 90%+
- UI Components: 70%+ (focus on logic, not rendering)

**Property Coverage**:
- All 27 correctness properties must have corresponding property tests
- Each property test must run minimum 100 iterations
- Property tests should use realistic data generators

### Integration Testing

**End-to-End Scenarios**:
1. First-time setup: Region selection → Configuration save → First search
2. Normal operation: Auto-search cycle → Question recognition → Answer display
3. Game switching: Change game → Load ROI → Continue searching
4. Error recovery: Simulate failures → Verify recovery → Check logging
5. Question addition: No match → Add question → Verify searchable

### Performance Testing

**Benchmarks**:
- Screen capture: <100ms (measured with mss library)
- OCR processing: <500ms (measured with various image sizes)
- Search operation: <100ms (measured with 10,000+ question database)
- Full cycle: <1000ms (end-to-end timing)

**Load Testing**:
- Continuous auto-search for 1 hour without memory leaks
- Database with 50,000+ questions without performance degradation
- Rapid game switching (10 switches/second) without crashes

### Manual Testing Checklist

**UI/UX Testing**:
- [ ] Overlay remains on top during game fullscreen
- [ ] Transparency slider provides smooth visual feedback
- [ ] Region selection works across multiple monitors
- [ ] Hotkey works when application is not focused
- [ ] UI remains responsive during OCR processing

**Compatibility Testing**:
- [ ] Windows 10 (various resolutions)
- [ ] Windows 11 (various resolutions)
- [ ] Multiple monitor setups
- [ ] High DPI displays (scaling)
- [ ] Different game window sizes

**OCR Accuracy Testing**:
- [ ] Test with actual game screenshots from each supported game
- [ ] Measure accuracy on 100+ real questions per game
- [ ] Adjust preprocessing parameters for optimal results
- [ ] Document optimal settings for each game

## Deployment Considerations

### Packaging with PyInstaller

**Build Configuration** (`build.spec`):
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        ('tesseract/tesseract.exe', 'tesseract'),
        ('tesseract/tessdata/kor.traineddata', 'tesseract/tessdata')
    ],
    datas=[
        ('data/*.json', 'data'),
        ('config.json', '.')
    ],
    hiddenimports=[
        'pytesseract',
        'rapidfuzz',
        'mss',
        'cv2',
        'PIL'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QuizAutoAnswer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)
```

### Distribution Package Structure

```
QuizAutoAnswer/
├── QuizAutoAnswer.exe          # Main executable
├── data/
│   ├── all_questions.json      # Pre-loaded question database
│   └── user_added.json         # User additions (created on first run)
├── config.json                 # Default configuration
├── README.txt                  # User guide
└── LICENSE.txt                 # License information
```

### First-Run Experience

1. Application detects no configuration file
2. Creates default config.json with sensible defaults
3. Shows welcome dialog explaining region selection
4. Prompts user to select game and configure ROI
5. Performs test capture to verify setup
6. Saves configuration and starts main window

### Update Strategy

**Question Database Updates**:
- Provide downloadable JSON files with new questions
- User places file in `data/` directory
- Application auto-detects and loads on next startup
- Merge with existing user-added questions

**Application Updates**:
- Version checking against remote server (optional)
- Download new executable
- Preserve user configuration and added questions
- Migration scripts for config format changes

## Performance Optimization Strategies

### 1. OCR Optimization
- **ROI Sizing**: Capture only necessary area (smaller = faster)
- **Preprocessing Cache**: Cache preprocessing results for identical images
- **Tesseract PSM**: Use PSM 6 (uniform block) for faster processing
- **Image Downscaling**: Scale large captures to optimal size (20-40px font height)

### 2. Search Optimization
- **Exact Match First**: O(1) hash lookup before expensive fuzzy matching
- **Early Termination**: Stop fuzzy search when 100% match found
- **Game Filtering**: Reduce search space by 75% when game filter active
- **Index Precomputation**: Build normalized index at startup

### 3. Memory Optimization
- **Image Cleanup**: Delete numpy arrays immediately after OCR
- **Result Caching**: Keep only last result, not history
- **Database Lazy Loading**: Load questions on-demand if database exceeds 100MB
- **String Interning**: Reuse common strings (game names, etc.)

### 4. UI Optimization
- **Async Updates**: Use Qt signals for non-blocking UI updates
- **Debouncing**: Limit slider updates to 60fps max
- **Lazy Rendering**: Only redraw changed widgets
- **Double Buffering**: Prevent flicker in overlay window

## Security Considerations

### Data Privacy
- All processing happens locally (no network requests)
- No telemetry or usage tracking
- User-added questions stored locally only
- No personal information collected

### File System Access
- Read-only access to game screen (via screen capture API)
- Write access only to application directory
- Configuration files use JSON (human-readable, no code execution)
- Input validation on all user-provided data

### Dependency Security
- Use pinned versions of all dependencies
- Regular security audits of third-party libraries
- Tesseract OCR: trusted, widely-used open-source project
- RapidFuzz: pure Python, no native code vulnerabilities

## Future Enhancements

### Phase 1 Enhancements (Post-MVP)
- Multi-language support (English, Japanese)
- Cloud sync for user-added questions
- Statistics dashboard (accuracy, speed, usage)
- Custom themes and UI customization

### Phase 2 Enhancements
- Machine learning for OCR error correction
- Automatic game detection (no manual selection)
- Voice output for answers (text-to-speech)
- Mobile companion app for remote control

### Phase 3 Enhancements
- Community question database with voting
- Plugin system for custom games
- Advanced analytics and insights
- Team/multiplayer features

