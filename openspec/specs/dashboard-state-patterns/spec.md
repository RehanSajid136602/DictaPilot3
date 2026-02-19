## ADDED Requirements

### Requirement: Loading states with skeleton screens
The system SHALL display skeleton screens during initial data load for cards, lists, and charts.

#### Scenario: Card skeleton
- **WHEN** card data is loading
- **THEN** skeleton shows pulsing rounded rectangles matching card layout

#### Scenario: List skeleton
- **WHEN** list data is loading
- **THEN** skeleton shows 5 pulsing rows with rectangles for text

#### Scenario: Chart skeleton
- **WHEN** chart data is loading
- **THEN** skeleton shows gray placeholder rectangle with centered spinner

#### Scenario: Skeleton animation
- **WHEN** skeleton is displayed
- **THEN** opacity oscillates between 0.4 and 1.0 with 1.5s period

### Requirement: Inline loading spinners
The system SHALL provide inline spinners for operations like API tests and diagnostic checks.

#### Scenario: Display spinner
- **WHEN** an operation is in progress
- **THEN** 20px diameter spinner with accent-blue color is displayed

#### Scenario: Replace with result
- **WHEN** operation completes
- **THEN** spinner is replaced with success/error indicator

### Requirement: Empty states
The system SHALL display empty states with icon, message, and action button when no data exists.

#### Scenario: Empty history state
- **WHEN** no transcriptions exist
- **THEN** empty state shows microphone icon, "No transcriptions yet" message, and "Start Dictating" button

#### Scenario: Empty search results
- **WHEN** search returns no results
- **THEN** empty state shows search icon, "No results for '{query}'" message, and "Clear Search" link

#### Scenario: Empty statistics state
- **WHEN** insufficient data for statistics
- **THEN** empty state shows chart icon and "Not enough data" message

### Requirement: Error states
The system SHALL display error states with clear messaging and recovery actions.

#### Scenario: Inline field error
- **WHEN** form field has validation error
- **THEN** field shows red border and error message below in red text

#### Scenario: Page-level error banner
- **WHEN** page-level error occurs
- **THEN** banner appears at top with error icon, message, and action buttons

#### Scenario: Connection error
- **WHEN** API connection fails
- **THEN** status card shows red indicator and retry button appears

### Requirement: Toast notifications
The system SHALL display toast notifications in bottom-right corner with auto-dismiss.

#### Scenario: Success toast
- **WHEN** operation succeeds
- **THEN** green-bordered toast appears with checkmark icon and success message

#### Scenario: Warning toast
- **WHEN** warning occurs
- **THEN** yellow-bordered toast appears with warning icon and message

#### Scenario: Error toast
- **WHEN** error occurs
- **THEN** red-bordered toast appears with X icon and error message

#### Scenario: Info toast
- **WHEN** informational message is shown
- **THEN** blue-bordered toast appears with info icon and message

#### Scenario: Auto-dismiss toast
- **WHEN** toast is displayed
- **THEN** it automatically dismisses after 5 seconds

#### Scenario: Manual dismiss toast
- **WHEN** user clicks X button on toast
- **THEN** toast immediately dismisses

#### Scenario: Stack multiple toasts
- **WHEN** multiple toasts are shown
- **THEN** maximum 3 toasts are visible with newest at bottom

### Requirement: Notification bell
The system SHALL provide a notification bell in toolbar with badge count.

#### Scenario: Display unread count
- **WHEN** unread notifications exist
- **THEN** red badge with count appears on bell icon

#### Scenario: Show notification dropdown
- **WHEN** user clicks bell icon
- **THEN** dropdown shows list of recent notifications

#### Scenario: Mark all read
- **WHEN** user clicks "Mark all read" in dropdown
- **THEN** all notifications are marked read and badge disappears
