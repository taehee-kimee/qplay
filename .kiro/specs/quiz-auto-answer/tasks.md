# Implementation Plan: Quiz Auto-Answer System

## Overview

This implementation plan breaks down the Quiz Auto-Answer System into incremental, testable tasks. The approach prioritizes core functionality first (screen capture, OCR, search), then builds the UI layer, and finally adds convenience features. Each task builds on previous work, with checkpoints to ensure stability before proceeding.

## Tasks

- [ ] 1. Project Setup and Dependencies
  - Create project structure with directories: `ui/`, `data/`, `tesseract/`
  - Create `requirements.txt` with dependencies: PyQt5, pytesseract, opencv-python, mss, rapidfuzz, hypothesis, pytest
  - Set up basic `main.py` entry point
  - Create `config.json` with default configuration structure
  - _Requirements: 8.7, 10.3_

- [ ] 2. Configuration Manager
  - [ ] 2.1 Implement ConfigManager class
    - Create `config_manager.py` with ConfigManager class
    - Implement `load_or_create_default()` method with default values
    - Implement `get()`, `set()`, and `save()` methods
    - Implement `get_current_roi()` and `save_roi()` methods for game-specific ROI management
    - _Requirements: 1.4, 1.5, 8.5, 8.6, 8.7_

  - [ ]* 2.2 Write property test for configuration persistence
    - **Property 20: Settings Persistence**
    - **Validates: Requirements 8.5**

  - [ ]* 2.3 Write property test for ROI persistence
    - **Property 1: ROI Configuration Persistence**
    - **Validates: Requirements 1.3, 1.4, 1.5**

- [ ] 3. Screen Capture Module
  - [ ] 3.1 Implement ScreenCapture class
    - Create `screen_capture.py` with ScreenCapture class
    - Implement `capture_region()` using mss library
    - Implement `get_screen_size()` method
    - Return images as numpy arrays in BGR format (OpenCV compatible)
    - _Requirements: 1.7, 3.2_

  - [ ]* 3.2 Write unit tests for screen capture
    - Test capture with valid ROI coordinates
    - Test capture with invalid coordinates (edge case)
    - Test performance (<100ms target)
    - _Requirements: 1.7_

- [ ] 4. OCR Engine with Preprocessing
  - [ ] 4.1 Implement ImagePreprocessor class
    - Create `ocr_engine.py` with ImagePreprocessor class
    - Implement `preprocess()` method with pipeline:
      - Grayscale conversion
      - Gaussian blur for noise reduction
      - CLAHE for contrast enhancement
      - Binarization (Otsu's method and adaptive threshold)
    - Accept configuration parameters (brightness, contrast, blur_kernel, threshold_method)
    - _Requirements: 2.2, 2.5_

  - [ ] 4.2 Implement OCREngine class
    - Implement `__init__()` with Tesseract path detection
    - Implement `_find_tesseract()` to locate embedded executable
    - Implement `extract_text()` method with preprocessing option
    - Configure Tesseract for Korean (lang=kor, psm=6, oem=3)
    - Return tuple of (text, confidence_score)
    - _Requirements: 2.1, 2.2, 2.6_

  - [ ]* 4.3 Write property test for OCR preprocessing application
    - **Property 2: OCR Preprocessing Application**
    - **Validates: Requirements 2.2, 2.5**

  - [ ]* 4.4 Write property test for OCR output structure
    - **Property 4: OCR Output Structure**
    - **Validates: Requirements 2.6, 2.7**

  - [ ]* 4.5 Write property test for OCR performance
    - **Property 3: OCR Performance Constraint**
    - **Validates: Requirements 2.4**

  - [ ]* 4.6 Write property test for low confidence flagging
    - Test that results with confidence < 70% are flagged
    - _Requirements: 2.7_

- [ ] 5. Checkpoint - Core Capture and OCR
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Search Engine with Fuzzy Matching
  - [ ] 6.1 Implement QuestionIndex class
    - Create `search_engine.py` with QuestionIndex class
    - Implement `add_question()` method with normalization
    - Create exact match dictionary (hash map) for O(1) lookups
    - Create questions list for fuzzy matching
    - Implement game-specific indices
    - _Requirements: 4.1, 4.6_

  - [ ] 6.2 Implement SearchEngine class
    - Implement `__init__()` to load JSON files into memory
    - Implement `_load_questions()` to parse JSON and populate index
    - Implement `_normalize()` for text normalization (lowercase, remove whitespace/punctuation)
    - _Requirements: 4.1, 7.3_

  - [ ] 6.3 Implement search() method with multi-stage matching
    - Stage 1: Exact match using hash lookup
    - Stage 2: Fuzzy match using RapidFuzz with configurable threshold
    - Apply game filter if specified
    - Return list of matches with confidence scores
    - Handle no-match case with appropriate result
    - _Requirements: 4.2, 4.3, 4.4, 4.6, 4.7, 4.8, 4.9_

  - [ ]* 6.4 Write property test for search strategy order
    - **Property 9: Search Strategy Order**
    - **Validates: Requirements 4.3, 4.4**

  - [ ]* 6.5 Write property test for search normalization
    - **Property 10: Search Normalization Invariance**
    - **Validates: Requirements 4.5**

  - [ ]* 6.6 Write property test for game filter enforcement
    - **Property 11: Game Filter Enforcement**
    - **Validates: Requirements 4.6**

  - [ ]* 6.7 Write property test for result completeness
    - **Property 12: Search Result Completeness**
    - **Validates: Requirements 4.7**

  - [ ]* 6.8 Write property test for confidence scoring
    - **Property 13: Search Confidence Scoring**
    - **Validates: Requirements 4.8**

  - [ ]* 6.9 Write property test for no-match handling
    - **Property 14: Search No-Match Handling**
    - **Validates: Requirements 4.9**

  - [ ]* 6.10 Write property test for search performance
    - **Property 8: Search Performance Constraint**
    - **Validates: Requirements 4.2**

- [ ] 7. Checkpoint - Search Engine Validation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Region Selector UI
  - [ ] 8.1 Implement RegionSelectorWindow class
    - Create `region_selector.py` with RegionSelectorWindow class
    - Set window flags (WindowStaysOnTopHint, FramelessWindowHint, Tool)
    - Implement `_capture_full_screen()` for background screenshot
    - Implement mouse event handlers (press, move, release)
    - Implement `paintEvent()` to draw semi-transparent overlay and selection rectangle
    - Emit `region_selected` signal with coordinates on completion
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ]* 8.2 Write unit tests for region selector
    - Test mouse drag creates valid rectangle
    - Test coordinates are correctly calculated
    - Test signal emission with correct data
    - _Requirements: 1.1, 1.2, 1.3_

- [ ] 9. Overlay Window UI
  - [ ] 9.1 Implement OverlayWindow class
    - Create `ui/overlay_window.py` with OverlayWindow class
    - Set window flags for always-on-top transparent window
    - Create UI layout with labels for status, question, answer, confidence
    - Style question label (blue, small font)
    - Style answer label (green, large bold font)
    - Add Start, Pause, and Copy buttons
    - Add transparency slider (10-100%, default 80%)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 11.7_

  - [ ] 9.2 Implement update_result() method
    - Display question text in question label
    - Display answer(s) in answer label (join multiple with " / ")
    - Show OCR and search confidence scores
    - Show current game name
    - Show timestamp
    - Handle no-match case with appropriate message
    - _Requirements: 5.7, 5.8, 5.9, 5.10, 11.2, 11.3, 11.5, 11.6_

  - [ ] 9.3 Implement opacity control
    - Connect slider to `_update_opacity()` method
    - Update window opacity in real-time
    - _Requirements: 5.2, 5.3, 5.4_

  - [ ] 9.4 Implement copy to clipboard functionality
    - Connect copy button to clipboard operation
    - Show confirmation message after copy
    - _Requirements: 11.7, 11.8_

  - [ ]* 9.5 Write property test for opacity range
    - **Property 15: Overlay Opacity Range**
    - **Validates: Requirements 5.2**

  - [ ]* 9.6 Write property test for opacity responsiveness
    - **Property 16: Overlay Opacity Responsiveness**
    - **Validates: Requirements 5.4**

  - [ ]* 9.7 Write property test for result display completeness
    - **Property 17: Result Display Completeness**
    - **Validates: Requirements 5.7, 5.8, 5.9**

  - [ ]* 9.8 Write property test for multiple answer formatting
    - **Property 18: Multiple Answer Formatting**
    - **Validates: Requirements 5.10**

  - [ ]* 9.9 Write property test for low confidence warning
    - **Property 24: Low Confidence Warning**
    - **Validates: Requirements 11.4**

- [ ] 10. Auto Search Manager
  - [ ] 10.1 Implement AutoSearchManager class
    - Create `auto_search_manager.py` with AutoSearchManager class (inherits QObject)
    - Define Qt signals: `result_ready`, `status_changed`
    - Implement `__init__()` with dependencies (screen_capture, ocr_engine, search_engine, config)
    - Set up QTimer for periodic execution
    - Initialize state variables (is_running, last_question, last_result)
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ] 10.2 Implement start() and pause() methods
    - Implement `start()` to begin timer with configured interval
    - Implement `pause()` to stop timer
    - Emit status_changed signals
    - _Requirements: 3.1, 3.3, 3.6_

  - [ ] 10.3 Implement _search_cycle() method
    - Get ROI from config
    - Capture screen region
    - Extract text via OCR with preprocessing
    - Compare with last_question (skip if duplicate)
    - Search for answer with game filter
    - Emit result_ready signal with complete result data
    - Handle errors gracefully (log and continue)
    - _Requirements: 3.2, 3.4, 3.5, 9.3, 12.5_

  - [ ]* 10.4 Write property test for duplicate detection
    - **Property 5: Auto-Search Duplicate Detection**
    - **Validates: Requirements 3.4, 3.5, 9.4**

  - [ ]* 10.5 Write property test for status synchronization
    - **Property 6: Auto-Search Status Synchronization**
    - **Validates: Requirements 3.6, 11.1**

  - [ ]* 10.6 Write property test for search interval bounds
    - **Property 7: Search Interval Bounds**
    - **Validates: Requirements 3.7**

  - [ ]* 10.7 Write property test for paused state inactivity
    - **Property 22: Paused State Inactivity**
    - **Validates: Requirements 9.3**

  - [ ]* 10.8 Write property test for full cycle performance
    - **Property 21: Full Cycle Performance**
    - **Validates: Requirements 9.2**

- [ ] 11. Checkpoint - Auto Search Functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Hotkey Manager
  - [ ] 12.1 Implement HotkeyManager class
    - Create `hotkey_manager.py` with HotkeyManager class
    - Use `keyboard` library for global hotkey registration
    - Implement `register_hotkey()` method
    - Implement `unregister_hotkey()` method
    - Emit signal when hotkey is pressed
    - Handle hotkey conflicts gracefully
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 12.2 Write unit tests for hotkey functionality
    - Test hotkey registration
    - Test signal emission on hotkey press
    - Test hotkey customization
    - _Requirements: 6.1, 6.4_

- [ ] 13. Main Window Integration
  - [ ] 13.1 Create MainWindow class
    - Create `ui/main_window.py` with MainWindow class
    - Instantiate all components (screen_capture, ocr_engine, search_engine, auto_search_manager, hotkey_manager)
    - Create OverlayWindow instance
    - Connect signals between components
    - Implement menu bar with Settings and Region Selection options
    - _Requirements: 1.1, 3.1, 6.1_

  - [ ] 13.2 Wire auto-search to UI
    - Connect Start button to auto_search_manager.start()
    - Connect Pause button to auto_search_manager.pause()
    - Connect result_ready signal to overlay.update_result()
    - Connect status_changed signal to overlay status label
    - _Requirements: 3.1, 3.3, 3.6_

  - [ ] 13.3 Wire hotkey to single search
    - Connect hotkey signal to single search method
    - Implement single search (capture → OCR → search → display)
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ] 13.4 Wire region selector
    - Connect region selection menu to RegionSelectorWindow
    - Connect region_selected signal to config.save_roi()
    - Update UI after region selection
    - _Requirements: 1.1, 1.2, 1.3_

- [ ] 14. Settings Dialog
  - [ ] 14.1 Implement SettingsDialog class
    - Create `ui/settings_dialog.py` with SettingsDialog class
    - Add game selection dropdown
    - Add OCR preprocessing parameter controls (brightness, contrast, threshold)
    - Add auto-search interval spinbox (0.5-5 seconds)
    - Add hotkey customization field
    - Add search threshold slider (0-100%)
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ] 14.2 Connect settings to configuration
    - Load current settings from ConfigManager on dialog open
    - Save settings to ConfigManager on dialog accept
    - Apply settings immediately (no restart required)
    - _Requirements: 8.5, 8.6_

  - [ ]* 14.3 Write unit tests for settings persistence
    - Test settings save on change
    - Test settings load on startup
    - _Requirements: 8.5, 8.6_

- [ ] 15. Question Management Features
  - [ ] 15.1 Implement add question dialog
    - Create `ui/add_question_dialog.py` with AddQuestionDialog class
    - Add form fields: question text, answer text, game category
    - Implement validation (non-empty fields)
    - _Requirements: 7.1, 7.6_

  - [ ] 15.2 Implement question persistence
    - Create method to save question to `user_added.json`
    - Reload search engine after adding question
    - _Requirements: 7.2, 7.3_

  - [ ] 15.3 Add "Add this question" button to overlay
    - Show button when no match is found
    - Pre-fill question field with recognized text
    - _Requirements: 7.4, 7.5_

  - [ ]* 15.4 Write property test for question persistence
    - **Property 19: Question Persistence**
    - **Validates: Requirements 7.2, 7.6**

- [ ] 16. Region Testing Feature
  - [ ] 16.1 Implement region test dialog
    - Create `ui/region_test_dialog.py` with RegionTestDialog class
    - Add "Test Region" button to main window
    - Capture current ROI and display preview image
    - Perform OCR on captured image
    - Display extracted text and confidence score
    - Allow preprocessing parameter adjustment and re-test
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_

  - [ ]* 16.2 Write unit tests for region testing
    - Test capture and preview display
    - Test OCR execution
    - Test parameter adjustment and re-test
    - _Requirements: 13.1, 13.3, 13.6_

- [ ] 17. Error Handling and Logging
  - [ ] 17.1 Implement error logging system
    - Create `logger.py` with logging configuration
    - Set up file handler for error log
    - Define log format with timestamp, level, component, message
    - _Requirements: 12.6_

  - [ ] 17.2 Add error handling to all components
    - Wrap screen capture in try-except, log errors, continue operation
    - Wrap OCR processing in try-except, display error message
    - Handle missing database file with error dialog
    - Handle missing Tesseract with clear error message
    - Wrap auto-search cycle in try-except, log and continue
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

  - [ ]* 17.3 Write property test for error recovery
    - **Property 26: Error Recovery Continuity**
    - **Validates: Requirements 12.1, 12.2, 12.5**

  - [ ]* 17.4 Write property test for error logging
    - **Property 27: Error Logging**
    - **Validates: Requirements 12.6**

- [ ] 18. Checkpoint - Complete Feature Set
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 19. Tesseract Embedding
  - [ ] 19.1 Download and embed Tesseract
    - Download Tesseract 4.x for Windows
    - Place `tesseract.exe` in `tesseract/` directory
    - Download `kor.traineddata` and place in `tesseract/tessdata/`
    - Update OCREngine to use relative paths
    - _Requirements: 2.1, 10.1, 10.5_

  - [ ]* 19.2 Write property test for embedded resource location
    - **Property 23: Embedded Resource Location**
    - **Validates: Requirements 10.5**

- [ ] 20. Sample Question Database
  - [ ] 20.1 Prepare sample database
    - Check if existing JSON files in `questions/` directory are usable
    - If yes, copy to `data/` directory
    - If no, create sample `all_questions.json` with test data
    - Ensure JSON format matches SearchEngine expectations
    - _Requirements: 4.1_

- [ ] 21. PyInstaller Build Configuration
  - [ ] 21.1 Create build.spec file
    - Create `build.spec` with PyInstaller configuration
    - Include Tesseract binaries and data files
    - Include question database files
    - Include config.json
    - Set up hidden imports for all dependencies
    - Configure for no-console mode
    - _Requirements: 10.1, 10.3, 10.4_

  - [ ] 21.2 Test executable build
    - Run PyInstaller with build.spec
    - Test executable on clean Windows system (no Python)
    - Verify all resources are accessible
    - Verify Tesseract is found and functional
    - _Requirements: 10.2, 10.4_

- [ ] 22. Documentation and Polish
  - [ ] 22.1 Create user documentation
    - Write README.txt with setup instructions
    - Document first-time region selection process
    - Document hotkey usage and auto-search mode
    - Document settings and customization options
    - Add troubleshooting section

  - [ ] 22.2 Add application icon
    - Create or source application icon
    - Add to PyInstaller build configuration
    - Set window icons in UI

  - [ ]* 22.3 Write integration tests
    - Test end-to-end: region selection → auto-search → answer display
    - Test game switching workflow
    - Test question addition workflow
    - _Requirements: 1.1, 3.1, 7.1_

- [ ] 23. Final Checkpoint - Production Ready
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Focus on getting core functionality working first, then add polish
- The existing `questions/` directory files should be evaluated and potentially used as the question database
