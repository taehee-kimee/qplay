# Requirements Document

## Introduction

This document specifies the requirements for a desktop application that automatically recognizes quiz questions displayed on game screens in real-time and instantly provides answers. The system must achieve high accuracy (95%+) and fast response times (<1 second) while maintaining a non-intrusive user experience through a transparent overlay interface.

The application targets Korean quiz games (꽁꽁, 올라올라, OX, 가로세로) and must operate standalone without requiring API keys or external services.

## Glossary

- **OCR_Engine**: The optical character recognition component that extracts text from screen captures
- **Search_Engine**: The component that matches recognized questions to answers in the database
- **Overlay_Window**: The transparent, always-on-top window that displays results
- **Region_Selector**: The UI component for defining screen capture areas
- **Auto_Search_Manager**: The component managing continuous automatic question recognition
- **Question_Database**: JSON file containing quiz questions and answers
- **ROI**: Region of Interest - the specific screen area containing quiz questions
- **Preprocessing**: Image enhancement operations applied before OCR
- **Fuzzy_Matching**: Approximate string matching algorithm tolerating OCR errors

## Requirements

### Requirement 1: Screen Capture and Region Selection

**User Story:** As a user, I want to define which area of my screen contains quiz questions, so that the system only captures relevant content.

#### Acceptance Criteria

1. WHEN a user clicks the region selection button, THE Region_Selector SHALL display a semi-transparent overlay covering the entire screen
2. WHEN a user drags the mouse on the overlay, THE Region_Selector SHALL draw a red rectangle showing the selected area
3. WHEN a user confirms the selection, THE Region_Selector SHALL save the coordinates (X, Y, Width, Height) to the configuration file
4. WHERE multiple games are configured, THE Region_Selector SHALL store separate ROI coordinates for each game
5. WHEN a user switches games, THE System SHALL automatically load the corresponding ROI coordinates
6. THE Region_Selector SHALL provide manual adjustment controls for fine-tuning coordinates
7. WHEN a user clicks the test button, THE System SHALL capture the current ROI and display the preview image

### Requirement 2: OCR Text Recognition

**User Story:** As a user, I want the system to accurately recognize Korean text from game screens, so that questions are correctly identified.

#### Acceptance Criteria

1. THE OCR_Engine SHALL use Tesseract OCR with Korean language data (kor.traineddata) embedded in the application
2. WHEN capturing a screen region, THE OCR_Engine SHALL apply preprocessing operations (contrast adjustment, noise reduction, binarization) before text extraction
3. THE OCR_Engine SHALL extract text from captured images with 95% accuracy on clean game screens
4. THE OCR_Engine SHALL complete text extraction within 500 milliseconds
5. WHEN preprocessing is enabled, THE OCR_Engine SHALL adjust brightness, contrast, and threshold values based on configuration settings
6. THE OCR_Engine SHALL return both the extracted text and a confidence score
7. IF the confidence score is below 70%, THEN THE OCR_Engine SHALL flag the result as low confidence

### Requirement 3: Automatic Search Mode

**User Story:** As a user, I want the system to continuously monitor the game screen and automatically display answers, so that I don't need to manually trigger recognition for each question.

#### Acceptance Criteria

1. WHEN a user clicks the Start button, THE Auto_Search_Manager SHALL begin continuous monitoring at the configured interval (default 1 second)
2. WHILE auto-search is active, THE Auto_Search_Manager SHALL repeatedly capture the ROI, extract text, and search for answers
3. WHEN a user clicks the Pause button, THE Auto_Search_Manager SHALL stop the monitoring loop
4. THE Auto_Search_Manager SHALL compare each recognized question with the previous question
5. IF the current question matches the previous question, THEN THE Auto_Search_Manager SHALL skip the search operation
6. THE Auto_Search_Manager SHALL update the UI with the current status ("Auto-searching..." or "Paused")
7. THE System SHALL allow users to configure the search interval between 0.5 and 5 seconds
8. WHILE auto-search is running, THE System SHALL continue operating in the background without blocking user interaction

### Requirement 4: Answer Search and Matching

**User Story:** As a user, I want the system to quickly find correct answers from the database, so that I can respond to quiz questions in time.

#### Acceptance Criteria

1. WHEN the application starts, THE Search_Engine SHALL load all questions from JSON files into memory
2. THE Search_Engine SHALL complete answer searches within 100 milliseconds
3. WHEN searching for an answer, THE Search_Engine SHALL first attempt exact string matching
4. IF exact matching fails, THEN THE Search_Engine SHALL apply fuzzy matching using Levenshtein distance
5. THE Search_Engine SHALL ignore whitespace and special characters during matching
6. WHERE a game filter is selected, THE Search_Engine SHALL limit searches to questions from that game
7. WHEN multiple answers match the question, THE Search_Engine SHALL return all matching answers
8. THE Search_Engine SHALL return a confidence score indicating match quality (0-100%)
9. IF no answer is found, THEN THE Search_Engine SHALL return a "No match found" result

### Requirement 5: Transparent Overlay Interface

**User Story:** As a user, I want a transparent window that displays answers without blocking my view of the game, so that I can play while seeing the answers.

#### Acceptance Criteria

1. THE Overlay_Window SHALL remain always-on-top of all other windows
2. THE Overlay_Window SHALL support transparency adjustment from 10% to 100%
3. THE Overlay_Window SHALL default to 80% opacity
4. WHEN a user adjusts the transparency slider, THE Overlay_Window SHALL update opacity in real-time
5. THE Overlay_Window SHALL display the recognized question in blue text with small font
6. THE Overlay_Window SHALL display the answer in green text with large bold font
7. THE Overlay_Window SHALL show confidence scores for both OCR and search matching
8. THE Overlay_Window SHALL display the currently selected game name
9. THE Overlay_Window SHALL show the last update timestamp
10. WHEN multiple answers exist, THE Overlay_Window SHALL display all answers separated by " / "

### Requirement 6: Manual Search Trigger

**User Story:** As a user, I want to trigger a single search using a hotkey, so that I can get answers on-demand without continuous monitoring.

#### Acceptance Criteria

1. WHEN a user presses the configured hotkey (default F9), THE System SHALL capture the ROI once
2. WHEN the hotkey is triggered, THE System SHALL extract text using OCR
3. WHEN the hotkey is triggered, THE System SHALL search for the answer and update the display
4. THE System SHALL allow users to customize the hotkey in settings
5. THE System SHALL register the hotkey globally to work even when the application is not focused

### Requirement 7: Question Database Management

**User Story:** As a user, I want to add new questions and answers to the database, so that the system can recognize questions not in the original dataset.

#### Acceptance Criteria

1. WHEN a user clicks the add question button, THE System SHALL display a form with fields for question text, answer, and game category
2. WHEN a user submits the form, THE System SHALL save the new question to the user_added.json file
3. WHEN the application starts, THE Search_Engine SHALL load questions from both the main database and user-added file
4. WHEN no answer is found for a recognized question, THE System SHALL display an "Add this question" button
5. WHEN a user clicks the add button, THE System SHALL pre-fill the question field with the recognized text
6. THE System SHALL validate that question and answer fields are not empty before saving

### Requirement 8: Configuration and Settings

**User Story:** As a user, I want to configure OCR parameters and application behavior, so that I can optimize performance for my specific game and screen setup.

#### Acceptance Criteria

1. THE System SHALL provide a settings interface for selecting the active game
2. THE System SHALL allow users to adjust OCR preprocessing parameters (brightness, contrast, threshold)
3. THE System SHALL allow users to configure the auto-search interval
4. THE System SHALL allow users to customize the hotkey for manual search
5. WHEN a user changes settings, THE System SHALL save the configuration to a file
6. WHEN the application starts, THE System SHALL load and apply saved settings
7. THE System SHALL provide default values for all configuration options

### Requirement 9: Performance and Resource Management

**User Story:** As a system administrator, I want the application to use minimal resources, so that it doesn't impact game performance.

#### Acceptance Criteria

1. THE System SHALL use less than 100MB of memory during normal operation
2. THE System SHALL complete the full cycle (capture → OCR → search → display) within 1 second
3. WHILE auto-search is paused, THE System SHALL not perform any screen captures or OCR operations
4. THE System SHALL cache the previous question to avoid redundant processing
5. THE System SHALL release captured images from memory after processing

### Requirement 10: Standalone Deployment

**User Story:** As a user, I want to run the application without installing additional software or configuring API keys, so that I can start using it immediately.

#### Acceptance Criteria

1. THE System SHALL include Tesseract OCR executable and Korean language data in the application package
2. THE System SHALL not require external API keys or internet connectivity for core functionality
3. THE System SHALL bundle all required dependencies in the executable
4. WHEN distributed as an executable, THE System SHALL run on Windows without requiring Python installation
5. THE System SHALL locate embedded Tesseract resources relative to the executable path

### Requirement 11: User Feedback and Status Display

**User Story:** As a user, I want to see the system's current status and operation results, so that I know whether it's working correctly.

#### Acceptance Criteria

1. THE Overlay_Window SHALL display the current auto-search status ("Auto-searching..." or "Paused")
2. THE Overlay_Window SHALL show OCR confidence scores as a percentage
3. THE Overlay_Window SHALL show search match confidence as a percentage
4. WHEN OCR confidence is below 70%, THE System SHALL display a warning indicator
5. WHEN no answer is found, THE System SHALL display "No match found" message
6. THE Overlay_Window SHALL show the timestamp of the last successful recognition
7. THE System SHALL provide a copy button to copy the answer to clipboard
8. WHEN the copy button is clicked, THE System SHALL copy the answer text and show a confirmation message

### Requirement 12: Error Handling and Recovery

**User Story:** As a user, I want the system to handle errors gracefully, so that temporary issues don't crash the application.

#### Acceptance Criteria

1. IF screen capture fails, THEN THE System SHALL log the error and continue operation
2. IF OCR processing fails, THEN THE System SHALL display an error message and allow retry
3. IF the question database file is missing, THEN THE System SHALL display an error and prompt for file location
4. IF Tesseract is not found, THEN THE System SHALL display a clear error message with troubleshooting steps
5. WHEN an error occurs during auto-search, THE System SHALL log the error and continue with the next cycle
6. THE System SHALL maintain a log file of errors for debugging purposes

### Requirement 13: Region Testing and Validation

**User Story:** As a user, I want to test my configured screen region, so that I can verify it captures the correct area before starting auto-search.

#### Acceptance Criteria

1. WHEN a user clicks the test region button, THE System SHALL capture the current ROI
2. WHEN testing the region, THE System SHALL display the captured image in a preview window
3. WHEN testing the region, THE System SHALL perform OCR on the captured image
4. WHEN testing the region, THE System SHALL display the extracted text
5. THE System SHALL show the OCR confidence score for the test capture
6. THE System SHALL allow users to adjust preprocessing parameters and re-test immediately
