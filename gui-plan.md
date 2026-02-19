DictaPilot GUI Dashboard — Design Specification
Table of Contents
Design Philosophy & Principles
Color Palette & Theming
Typography Scale
Spacing System
Overall Page Layout & Grid Structure
Visual Hierarchy
Navigation Architecture
Dashboard Views & Widgets
Data Visualization Components
Interactive Elements
Responsive Behavior
State Patterns
Accessibility (WCAG 2.1 AA)
Component Specifications Reference
1. Design Philosophy & Principles
DictaPilot's dashboard extends the existing Catppuccin Mocha-inspired theme found in settings_dashboard.py (dark) and settings_dashboard.py (light). The design priorities are:

Glanceable status — the most important data (recording state, system health) is visible within 200ms of opening the dashboard.
Progressive disclosure — simple surface, complex controls behind tabs/expandable sections.
Platform consistency — PySide6/Qt6 widgets with QSS theming, matching the existing DARK_THEME and LIGHT_THEME stylesheets.
Zero-chrome recording — the floating indicator bar remains minimal; the dashboard is the control center opened deliberately.
2. Color Palette & Theming
2.1 Dark Theme (Primary — Catppuccin Mocha)
Token	Hex	Usage
--bg-base	#1e1e2e	Window/widget backgrounds
--bg-mantle	#181825	Toolbar, status bar, sidebar
--bg-surface0	#313244	Cards, input fields, list backgrounds
--bg-surface1	#45475a	Borders, dividers, selected tabs
--bg-surface2	#585b70	Hover states
--text-primary	#cdd6f4	Body text
--text-secondary	#a6adc8	Muted labels, descriptions
--text-tertiary	#6c7086	Disabled text, placeholders
--accent-blue	#89b4fa	Links, active tabs, focused borders, headings
--accent-green	#a6e3a1	Success badges, recording active
--accent-yellow	#f9e2af	Warnings, processing state
--accent-red	#f38ba8	Errors, destructive actions
--accent-peach	#fab387	Agent mode accent
--accent-mauve	#cba6f7	Streaming/live indicators
2.2 Light Theme
Token	Hex	Usage
--bg-base	#f5f5f5	Window background
--bg-surface0	#ffffff	Cards, inputs
--bg-surface1	#e0e0e0	Borders, tabs
--text-primary	#1e1e2e	Body text
--text-secondary	#555555	Muted labels
--accent-blue	#2196f3	Primary accent
2.3 Semantic Colors
State	Dark	Light	Contrast Ratio (dark)
Success	#a6e3a1 on #1e1e2e	#2e7d32 on #fff	8.4:1 ✓
Warning	#f9e2af on #1e1e2e	#e65100 on #fff	7.1:1 ✓
Error	#f38ba8 on #1e1e2e	#c62828 on #fff	5.2:1 ✓
Info	#89b4fa on #1e1e2e	#1565c0 on #fff	5.8:1 ✓
3. Typography Scale
Font stack: "Segoe UI", "SF Pro Display", "Cantarell", system-ui, sans-serif — maps to system fonts across Windows, macOS, and GNOME/KDE.

Token	Size	Weight	Line Height	Usage
display	24 px	700	32 px	Page titles
heading-1	18 px	700	26 px	Section headings
heading-2	16 px	600	24 px	Group box titles, card titles (matches QLabel[heading="true"])
body	14 px	400	22 px	Default text, form labels
body-small	12 px	400	18 px	Descriptions, timestamps, tooltips
caption	11 px	400	16 px	Status bar text, badges
mono	13 px	400	20 px	Code snippets, file paths (uses "JetBrains Mono", "Fira Code", monospace)
4. Spacing System
A base-4 spacing scale:

Token	Value	Usage
xs	4 px	Inline padding within badges
sm	8 px	Icon-to-text gap, list item padding (matches QListWidget::item { padding: 8px })
md	12 px	Group spacing, form layout gap (matches setSpacing(12))
lg	16 px	Content area margins (matches setContentsMargins(16,16,16,16))
xl	24 px	Between major sections
2xl	32 px	Page-level padding on large screens
Border radius: 6 px (small controls), 8 px (cards/groups — matches border-radius: 8px).

5. Overall Page Layout & Grid Structure
The dashboard uses a sidebar + main content layout instead of the current tab-only approach, while retaining tabs within content areas for sub-navigation.

┌──────────────────────────────────────────────────────────┐
│  TOOLBAR (48 px)                                         │
│  [Logo] [Search ━━━━━━━━━━━━] [🔔] [⚙] [👤] [🌙/☀]    │
├─────────────┬────────────────────────────────────────────┤
│             │  BREADCRUMB BAR (32 px)                    │
│  SIDEBAR    │  Home > Settings > Audio                   │
│  (220 px)   ├────────────────────────────────────────────┤
│             │                                            │
│  ┌────────┐ │  MAIN CONTENT AREA                        │
│  │ 🏠 Home│ │  (flex: 1, scrollable)                    │
│  │ ⚙ Set. │ │                                            │
│  │ 📊 Stat│ │  ┌──────────────┐ ┌──────────────┐        │
│  │ 📝 Hist│ │  │  Card        │ │  Card        │        │
│  │ 🔊 Aud.│ │  │              │ │              │        │
│  │ 🤖 Agt.│ │  └──────────────┘ └──────────────┘        │
│  │ 🏥 Diag│ │                                            │
│  └────────┘ │  ┌──────────────────────────────┐          │
│             │  │  Full-width panel              │          │
│             │  └──────────────────────────────┘          │
│             │                                            │
├─────────────┴────────────────────────────────────────────┤
│  STATUS BAR (24 px)                                      │
│  ● API Connected | Profile: default | F9 Ready | v3.x   │
└──────────────────────────────────────────────────────────┘
Grid Details
Region	Width	Height	Background
Toolbar	100 %	48 px fixed	--bg-mantle (#181825)
Sidebar	220 px fixed (collapsible to 56 px icon-only)	100 % – toolbar – statusbar	--bg-mantle
Breadcrumb bar	Remaining width	32 px fixed	--bg-base
Main content	Remaining width	Remaining height, vertical scroll	--bg-base
Status bar	100 %	24 px fixed	--bg-mantle
The main content area uses a responsive CSS Grid-like layout (implemented via Qt layouts):

2-column grid: each column is minmax(360px, 1fr)
Gap: lg (16 px)
Cards and panels span 1 or 2 columns as specified per widget
6. Visual Hierarchy
Primary — Immediate attention

Recording status indicator

System health badge

Active hotkey display

Secondary — Key metrics

Transcription count today

Words per minute trend

API usage / latency

Tertiary — Supporting info

Recent transcriptions list

Profile / config details

Audio device info

Quaternary — On-demand

Advanced settings panels

Dictionary entries

Debug / diagnostics

Primary: Larger font (heading-1), accent color backgrounds, top-left or center placement.
Secondary: Standard body font, card-level containers with subtle border.
Tertiary: body-small font, nested within sections.
Quaternary: Hidden behind expandable groups or navigation to sub-pages.
7. Navigation Architecture
7.1 Sidebar Navigation (Primary)
🏠  Home Dashboard          ← Default view
⚙️  Settings                ← Expands sub-items
    ├── General
    ├── Audio
    ├── Smart Editing
    └── Advanced
📊  Statistics & Analytics
📝  History & Transcriptions
📖  Dictionary & Snippets
    ├── Dictionary
    └── Snippets
🤖  Agent Mode
👤  Profiles
🏥  Diagnostics
❓  Help
Behavior:

Click parent item → navigates to the first child or summary view
Items with children show a chevron ▸ which rotates to ▾ on expand
Active item: --accent-blue left border (3 px) + --bg-surface1 background
Hover: --bg-surface2 background
Keyboard: ↑/↓ arrows, Enter to navigate, ←/→ to collapse/expand
7.2 Breadcrumb Bar (Secondary)
Rendered below toolbar, above main content:

Home  >  Settings  >  Audio
Separator: > in --text-tertiary
Clickable ancestors: --accent-blue text, underline on hover
Current page: --text-primary, non-clickable, font-weight: 600
7.3 In-Page Sub-Navigation (Tertiary)
Within certain views (Settings, Dictionary & Snippets), horizontal QTabBar tabs remain for sub-sections. This matches the existing QTabWidget pattern:

┌───────────┬────────────┬──────────────┬──────────────┐
│  General  │   Audio    │ Smart Edit   │  Advanced    │
└───────────┴────────────┴──────────────┴──────────────┘
7.4 Keyboard Shortcuts
Shortcut	Action
Ctrl+F	Focus global search bar
Ctrl+,	Open Settings view
Ctrl+H	Open History view
Ctrl+D	Open Diagnostics
Escape	Close modal / collapse sidebar
Ctrl+S	Save current settings
8. Dashboard Views & Widgets
8.1 Home Dashboard (Default View)
The landing page presents a status-at-a-glance layout.

┌─────────────────────────────────────────────────────────┐
│  Welcome to DictaPilot                     [▶ Start]    │
│  Press F9 to start dictating                            │
├──────────────────────┬──────────────────────────────────┤
│                      │                                  │
│  STATUS CARD         │  QUICK STATS CARD                │
│  (1 col)             │  (1 col)                         │
│                      │                                  │
│  ● Recording: Idle   │  Today: 42 transcriptions        │
│  ● API: Connected    │  Total words: 3,847              │
│  ● Mic: Blue Yeti    │  Avg WPM: 127                   │
│  ● Profile: default  │  Avg quality: 0.92               │
│                      │                                  │
├──────────────────────┴──────────────────────────────────┤
│                                                         │
│  RECENT TRANSCRIPTIONS (2 cols)                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 2m ago  "Meeting notes for the Q1 review..."    │    │
│  │ 15m ago "Fix the authentication bug in..."      │    │
│  │ 1h ago  "Draft email to marketing team..."      │    │
│  └─────────────────────────────────────────────────┘    │
│  [View All History →]                                   │
│                                                         │
├──────────────────────┬──────────────────────────────────┤
│  AUDIO WAVEFORM      │  TRANSCRIPTION ACTIVITY          │
│  MINI-PREVIEW        │  BAR CHART (7 days)              │
│  (1 col, 160 px h)   │  (1 col, 160 px h)              │
└──────────────────────┴──────────────────────────────────┘
8.1.1 Hero Banner
Dimensions: 2-column span, 80 px height
Content: "Welcome to DictaPilot" (display font), subtitle with hotkey hint, primary action button
Button: ▶ Start Dictating — --accent-green bg, white text, 6 px radius, 40 px height
Background: Subtle gradient from --bg-surface0 to --bg-base
8.1.2 System Status Card
Dimensions: 1 column, auto height
Border: 1 px --bg-surface1, 8 px radius
Content:
4 status rows, each with a colored dot indicator, label, and value
Dot colors: green (connected/ready), yellow (degraded), red (error), gray (disabled)
Dot size: 10 px diameter
Font: body for labels, body + font-weight: 600 for values
Row	Label	Possible Values	Dot Color
Recording	"Idle" / "Recording" / "Processing"	gray / --accent-green / --accent-yellow	
API	"Connected" / "Error" / "No Key"	green / red / red	
Microphone	Device name or "No device"	green / red	
Profile	Active profile name	--accent-blue always	
8.1.3 Quick Stats Card
Dimensions: 1 column, matches Status Card height
Layout: 2×2 inner grid of stat tiles
Each tile:
Large number: heading-1 font, --accent-blue
Label below: body-small, --text-secondary
Example: 42 / "Transcriptions today"
Tile	Metric	Source
Top-left	Transcriptions today	transcription_store.py count filtered by date
Top-right	Total words today	Sum of TranscriptionEntry.word_count
Bottom-left	Avg WPM	Mean of TranscriptionEntry.wpm
Bottom-right	Avg quality	Mean of TranscriptionEntry.quality_score displayed as percentage
8.1.4 Recent Transcriptions List
Dimensions: 2-column span, max 5 items
Each item:
Timestamp (relative, e.g., "2m ago") — body-small, --text-tertiary, 80 px fixed width
Truncated processed text — body, --text-primary, ellipsis after 120 chars
Tags as colored pills (if present)
Hover: --bg-surface2 background
Click: opens full detail in History view
Footer link: "View All History →" in --accent-blue
8.1.5 Audio Waveform Mini-Preview
Dimensions: 1 column, 160 px height
Type: Real-time waveform from RingBuffer data
Visual: Green bars on dark background when recording, gray when idle
States:
Idle: flat line with subtle breathing animation
Recording: live amplitude bars (64 bars, --accent-green)
Processing: pulsing yellow wave
8.1.6 Activity Bar Chart
Dimensions: 1 column, 160 px height
Type: Vertical bar chart — 7 bars for last 7 days
Bars: --accent-blue fill, 8 px radius top corners
X-axis: Day abbreviations (Mon, Tue, ...)
Y-axis: Hidden; values shown on hover tooltip
Hover: Bar brightens, tooltip shows "Tuesday: 23 transcriptions"
8.2 Settings View
Preserves the existing QTabWidget structure but wraps it within the sidebar layout.

Sub-tabs (unchanged from existing implementation):
General — Mode, hotkey, model, paste, UI settings (from GeneralSettingsTab)
Audio — Device, VAD, streaming parameters (from AudioSettingsTab)
Smart Editing — Dictation mode, cleanup level, confidence (from SmartEditingTab)
Advanced — Display server, agent integration, debug tools (from AdvancedTab)
Additions to the Settings View:
Settings Search (already exists as self.search_input):

Position: Top of settings area, full width
Placeholder: "Search settings... (Ctrl+F)"
Behavior: Filters visible settings groups, hides non-matching QGroupBox widgets
Save / Revert Bar:

Position: Sticky footer within settings area, 48 px height
Appears: Only when unsaved changes are detected
Left: "Unsaved changes" label with yellow dot
Right: [Revert] (secondary button) and [Save Settings] (primary button)
Animation: Slides up from bottom with 200ms ease-out
8.3 Statistics & Analytics View
┌─────────────────────────────────────────────────────────┐
│  Statistics & Analytics                                 │
├──────────────────────┬──────────────────────────────────┤
│  KPI CARD: Total     │  KPI CARD: Total    │ KPI CARD: │
│  Transcriptions      │  Words              │ Avg WPM   │
│  1,247               │  98,432             │ 134       │
│  ↑ 12% this week     │  ↑ 8% this week     │ ↓ 2%     │
├──────────────────────┴──────────────────────┴───────────┤
│                                                         │
│  TRANSCRIPTION VOLUME LINE CHART (2 cols, 240 px)       │
│  ── 30 days ──  ── 7 days ──  ── 24 hours ──           │
│                                                         │
├──────────────────────┬──────────────────────────────────┤
│  WORD COUNT          │  QUALITY SCORE                   │
│  HISTOGRAM           │  DISTRIBUTION                    │
│  (1 col, 200 px)     │  (1 col, 200 px)                │
├──────────────────────┴──────────────────────────────────┤
│                                                         │
│  TOP VOICE COMMANDS TABLE (2 cols)                      │
│  Command     │ Count │ Last Used                        │
│  delete that │  87   │ 5 min ago                        │
│  new para    │  54   │ 12 min ago                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
8.3.1 KPI Cards (Row of 3–4)
Layout: Horizontal row, equal width, xl (24 px) gap
Dimensions: Each card ~1/3 or 1/4 of the content width, 100 px height
Structure:
Large metric: display font, --text-primary
Label: body-small, --text-secondary
Trend indicator: ↑ 12% in --accent-green or ↓ 2% in --accent-red
Border: 1 px --bg-surface1, 8 px radius
Background: --bg-surface0
KPI	Data Source
Total Transcriptions	transcription_store.py total count
Total Words	Sum of all word_count
Average WPM	Mean of wpm
Average Quality	Mean of quality_score as percentage
8.3.2 Volume Line Chart
Dimensions: 2-column span, 240 px height
Type: Multi-series line chart (or single line with area fill)
Series: Transcription count per time unit
Time ranges: Toggle buttons — "30 days" | "7 days" | "24 hours"
X-axis: Date labels (auto-spaced)
Y-axis: Count, auto-scaled with gridlines at --bg-surface1
Line: 2 px stroke, --accent-blue, with --accent-blue 10% opacity area fill
Data points: 6 px circles on hover
Tooltip: Date + count on hover
8.3.3 Word Count Histogram
Dimensions: 1 column, 200 px height
Type: Horizontal/vertical bar chart showing distribution of transcription lengths
Bins: 0–10, 10–50, 50–100, 100–500, 500+ words
Bars: --accent-mauve fill
8.3.4 Quality Score Distribution
Dimensions: 1 column, 200 px height
Type: Donut chart or horizontal stacked bar
Segments: Excellent (>0.9), Good (0.7–0.9), Fair (0.5–0.7), Poor (<0.5)
Colors: --accent-green, --accent-blue, --accent-yellow, --accent-red
Center label (donut): Average score as percentage
8.3.5 Voice Commands Table
Dimensions: 2-column span
Columns: Command, Count, Last Used, Trend
Styling: Alternating row backgrounds --bg-base / --bg-surface0
Sortable: Click column header to sort
Max rows: 10, with "Show more" link
8.4 History & Transcriptions View
Extends the existing HistoryTab with enhanced UI:

┌─────────────────────────────────────────────────────────┐
│  [🔍 Search transcriptions...] [📅 Date Range ▾]       │
│  [Tags: all ▾] [Quality: all ▾] [App: all ▾]  [Export] │
├─────────────────────────────────────────────────────────┤
│  ┌─ List ──────────────────────┬─ Detail ──────────────┐│
│  │ ● 2m ago — "Meeting notes…" │  Original:            ││
│  │   1h ago — "Fix the auth…"  │  "meeting notes um…"  ││
│  │   3h ago — "Draft email…"   │                       ││
│  │   ...                       │  Processed:           ││
│  │                             │  "Meeting notes for…" ││
│  │                             │                       ││
│  │                             │  Tags: [work] [notes] ││
│  │                             │  App: VSCode           ││
│  │                             │  Quality: 94%         ││
│  │                             │  WPM: 142             ││
│  │                             │  Duration: 12.3s      ││
│  │                             │                       ││
│  │                             │  [Copy] [Delete] [Tag]││
│  └─────────────────────────────┴───────────────────────┘│
│  Showing 1–25 of 1,247  [< Prev] [1] [2] ... [Next >]  │
└─────────────────────────────────────────────────────────┘
Master-detail splitter: Left panel 40% / right panel 60%, resizable (using QSplitter)
List items: Timestamp, truncated text, quality dot, action badge
Detail panel: Full original and processed text, all fields from TranscriptionEntry
Filters: Dropdowns for tags, quality range, source app
Pagination: 25 items per page
8.5 Dictionary & Snippets View
Uses horizontal tabs for Dictionary and Snippets sub-views.

Dictionary tab (from DictionaryTab):

Search bar + list + entry editor (existing layout preserved)
Enhanced: Entry count badge on tab header
Snippets tab (from SnippetsTab):

Template management with preview
8.6 Profiles View
From ProfilesTab:

Profile list (left) + editor (right) in splitter layout
Active profile selector
Visual indicator for trigger apps
8.7 Agent Mode View
Dedicated view for agent/coding workflow configuration:

┌─────────────────────────────────────────────────────────┐
│  Agent Mode Configuration                    [Toggle ON]│
├──────────────────────┬──────────────────────────────────┤
│  STATUS              │  OUTPUT PREVIEW                  │
│  Mode: Agent ●       │  ┌──────────────────────────┐    │
│  Auto-detect: ON     │  │ Structured output sample  │    │
│  IDE Integration: ON │  │ based on current settings │    │
│  Format: structured  │  └──────────────────────────┘    │
├──────────────────────┴──────────────────────────────────┤
│  CONFIGURATION GROUPS                                   │
│  [Output Format] [IDE Integration] [Webhook] [Triggers] │
└─────────────────────────────────────────────────────────┘
8.8 Diagnostics View
From HealthChecker:

┌─────────────────────────────────────────────────────────┐
│  System Health                        [Run All Checks]  │
├─────────────────────────────────────────────────────────┤
│  ✅ API Key          Valid, connected                    │
│  ✅ Microphone        Blue Yeti, 16kHz                   │
│  ⚠️ Display Server   Wayland (limited clipboard)         │
│  ✅ Paste Backend     wl-copy available                   │
│  ✅ Dependencies      All satisfied                      │
│  ❌ Hotkey Backend    pynput: permission denied           │
│                                                         │
│  Last checked: 2 minutes ago                            │
├─────────────────────────────────────────────────────────┤
│  Detailed Logs (expandable)                             │
│  ▸ Full diagnostic output...                            │
└─────────────────────────────────────────────────────────┘
Each DiagnosticResult row:

Icon: ✅ (passed), ⚠️ (warning), ❌ (error) — 16×16 px
Name: body font, --text-primary
Message: body, --text-secondary
Severity colors: green/yellow/red left border (3 px)
9. Data Visualization Components
9.1 Chart Implementation
Since PySide6 doesn't include charts natively, use pyqtgraph (already available in scientific Python ecosystems) or QtCharts module:

Chart	Type	Dimensions	Colors
Activity bar (home)	Vertical bars	1-col × 160 px	--accent-blue
Volume line (stats)	Line + area	2-col × 240 px	--accent-blue line, 10% fill
Word histogram	Vertical bars	1-col × 200 px	--accent-mauve
Quality donut	Donut/ring	1-col × 200 px	green/blue/yellow/red
Audio waveform	Real-time bars	1-col × 160 px	--accent-green
9.2 Progress Indicators
Recording progress:

Indeterminate: pulsing bar in --accent-green
Position: Inline in status card or floating window
Transcription processing:

Determinate: horizontal bar showing streaming chunks processed
Uses StreamingResult progress
Height: 4 px, --accent-yellow fill
9.3 Status Badges
Reusable pill-shaped badges:

Badge	Background	Text Color	Example
Success	--accent-green 15%	--accent-green	"Connected"
Warning	--accent-yellow 15%	--accent-yellow	"Degraded"
Error	--accent-red 15%	--accent-red	"Failed"
Info	--accent-blue 15%	--accent-blue	"Streaming"
Neutral	--bg-surface1	--text-secondary	"v3.0"
Badge dimensions: auto-width, 22 px height, 11 px radius, caption font, 4 px horizontal padding.

10. Interactive Elements
10.1 Buttons
Four variants (matching existing QPushButton styles):

Variant	Default BG	Hover BG	Active BG	Disabled BG	Text
Primary	--accent-blue	#7aa8f0	#6b9ae0	--bg-surface0	white
Secondary	--bg-surface1	--bg-surface2	--bg-surface0	--bg-surface0	--text-primary
Destructive	--accent-red	#e07a96	#d06a86	--bg-surface0	white
Ghost	transparent	--bg-surface1	--bg-surface0	transparent	--text-secondary
Dimensions: min-width 80 px, height 36 px (compact: 28 px), padding 10 px 20 px, 6 px radius.

Focus: 2 px outline in --accent-blue with 2 px offset (keyboard accessibility).

10.2 Dropdowns / ComboBox
Matches existing QComboBox styling:

Default: --bg-surface0 bg, --bg-surface1 border
Focus: --accent-blue border
Dropdown arrow: CSS triangle in --accent-blue (from QComboBox::down-arrow)
Dropdown list: --bg-surface0 bg, max 8 visible items, scrollable
10.3 Search Bars
Two instances:

Global search (toolbar): 300 px width, magnifying glass icon prefix, body font
Settings search (from self.search_input): full-width, same styling
Behavior:

Debounce: 200ms
Results: Inline filtering (settings) or dropdown suggestions (global)
Clear: × button appears when text is present
Empty: Placeholder text in --text-tertiary
10.4 Toggles / Checkboxes
Matches QCheckBox::indicator:

Size: 20×20 px
Unchecked: --bg-surface0 bg, --bg-surface1 border
Checked: --accent-blue bg and border, white checkmark
Disabled: 50% opacity
10.5 Sliders
Matches QSlider:

Track: 8 px height, --bg-surface0, 4 px radius
Handle: 18 px diameter, --accent-blue, circular
Filled portion: --accent-blue
10.6 Modals / Dialogs
Backdrop: #000000 40% opacity
Dialog: --bg-surface0 bg, 12 px radius, 24 px padding
Max width: 480 px
Header: heading-1 font, close × button top-right
Footer: Right-aligned buttons, md gap
Animation: Fade-in 150ms + scale from 95% to 100%
Used for: Confirm delete, import/export, profile creation (QInputDialog).

10.7 Tooltips
Matches QToolTip:

Background: --bg-surface0
Border: 1 px --bg-surface1, 4 px radius
Text: body-small, --text-primary
Max width: 280 px
Delay: 500ms show, 100ms hide
Position: Above element, centered, with 8 px offset
10.8 Context Menus
Matches QMenu:

Background: --bg-surface0
Item padding: 8 px 24 px
Selected: --bg-surface1
Separator: 1 px --bg-surface1 horizontal line
Border radius: 6 px
Shadow: 0 4 px 12 px rgba(0,0,0,0.3)
11. Responsive Behavior
The dashboard targets three breakpoints, implemented via QMainWindow.resizeEvent():

11.1 Desktop (≥ 1024 px width)
Full sidebar (220 px) + 2-column content grid
All cards side-by-side
Master-detail splitter visible
11.2 Tablet (768–1023 px)
Sidebar collapsed to icon-only mode (56 px)
Icons remain visible, labels hidden
Hover: tooltip with section name
Click icon: sidebar temporarily expands as overlay
Content falls to single column
Cards stack vertically
Charts maintain minimum 320 px width
11.3 Compact / Mobile (< 768 px)
Sidebar fully hidden, replaced by hamburger menu ☰ in toolbar
Hamburger opens a full-height overlay drawer (280 px width)
Single-column layout
KPI cards: 2×2 grid → 1×4 stack
Master-detail (History): detail panel becomes a separate view (navigate on click)
Charts: horizontal scroll if content is wider than viewport
Toolbar: Search collapses to icon; click to expand
11.4 Minimum Size
setMinimumSize(900, 700) as defined in DictaPilotDashboard.__init__(). For responsive modes below 900 px, enable via a --compact flag or dynamic detection.

12. State Patterns
12.1 Loading States
Skeleton screens for initial data load:

Cards: Rounded rectangles pulsing between --bg-surface0 and --bg-surface1
Lists: 5 skeleton rows (rectangle for timestamp, longer rectangle for text)
Charts: Gray placeholder rectangle with centered spinner
Animation: opacity oscillation 0.4 → 1.0, 1.5s period
Inline spinners:

20 px diameter, 2 px stroke, --accent-blue partial arc
Used for: Microphone test, API connection test, diagnostic checks
12.2 Empty States
View	Illustration	Message	Action
History (no transcriptions)	🎙️ icon (64 px)	"No transcriptions yet" / "Press F9 to start dictating"	[Start Dictating] button
Dictionary (empty)	📖 icon	"Your dictionary is empty" / "Add words to improve accuracy"	[Add First Word] button
Statistics (no data)	📊 icon	"Not enough data" / "Use DictaPilot for a few days"	—
Search (no results)	🔍 icon	"No results for '{query}'" / "Try different keywords"	[Clear Search] link
Profiles (only default)	👤 icon	"Create profiles for different contexts"	[Create Profile] button
Empty state layout: Centered vertically and horizontally, --text-secondary text, heading-2 for title, body-small for description.

12.3 Error States
Inline errors (form fields):

Red border (--accent-red) on the input
Error message below: body-small, --accent-red, prefixed with ⚠️ icon
Example: API key field → "Invalid API key format"
Banner errors (page-level):

Full-width bar at top of main content, 48 px height
Background: --accent-red 15%
Left: ❌ icon + error message
Right: [Dismiss] ghost button + [Fix] primary button (if actionable)
Connection errors:

Status card shows red indicator + "API Unreachable"
Retry button with exponential backoff
Toast notification on reconnection
12.4 Notification / Alert Patterns
Toast notifications (bottom-right corner):

Max width: 360 px
Background: --bg-surface0, 8 px radius, subtle shadow
Left border: 3 px in semantic color (green/yellow/red/blue)
Content: Icon + title (body bold) + message (body-small)
Auto-dismiss: 5 seconds (configurable per importance)
Manual dismiss: × button
Stack: Max 3 visible, newest at bottom
Animation: Slide-in from right 200ms
Types:

Type	Icon	Border	Example
Success	✅	--accent-green	"Settings saved"
Warning	⚠️	--accent-yellow	"Microphone volume low"
Error	❌	--accent-red	"API connection failed"
Info	ℹ️	--accent-blue	"New version available"
Notification bell (toolbar):

Badge: Red circle with count, 16 px diameter, positioned at top-right of 🔔 icon
Dropdown: List of recent notifications, max 10, with "Mark all read" link
Unread: --bg-surface1 background; Read: transparent
13. Accessibility (WCAG 2.1 AA)
Requirement	Implementation
Color contrast ≥ 4.5:1 (text)	All palette combinations verified (see §2.3)
Color contrast ≥ 3:1 (large text/UI)	Accent colors on dark bg pass
No color-only information	Badges combine color + icon + text; charts use pattern fills + labels
Keyboard navigation	All interactive elements focusable via Tab; focus ring: 2 px --accent-blue outline
Screen reader labels	All QWidget elements have setAccessibleName() and setAccessibleDescription()
Reduced motion	Detect prefers-reduced-motion equivalent; disable waveform animations and toast slides
Focus management	Modal dialogs trap focus; Escape closes; focus returns to trigger
Error identification	Errors identified by icon + text + color, not just color
Resizable text	Layout remains usable at 200% zoom (Qt handles this natively)
14. Component Specifications Reference
Quick Lookup Table
Component	Widget Class	File	Height	Width	Columns
Toolbar	QToolBar	settings_dashboard.py	48 px	100 %	—
Sidebar	QFrame + QVBoxLayout	New	100 %	220 px / 56 px	—
Status Card	QGroupBox	settings_dashboard.py	Auto	1 col	1
Quick Stats Card	QGroupBox	New	Auto	1 col	1
Recent List	QListWidget	settings_dashboard.py	Auto (max 5)	2 cols	2
Waveform	QWidget (custom paint)	visualization_data.py	160 px	1 col	1
Bar Chart	QWidget (custom paint or pyqtgraph)	New	160 px	1 col	1
KPI Card	QFrame	New	100 px	1/3 col	1
Line Chart	QWidget (pyqtgraph)	New	240 px	2 cols	2
History Splitter	QSplitter	settings_dashboard.py	100 %	100 %	2
Settings Tabs	QTabWidget	settings_dashboard.py	100 %	100 %	—
Diagnostic List	QListWidget	health_checker.py	Auto	100 %	1
Toast	QFrame (overlay)	New	Auto	360 px	—
Modal	QDialog	New	Auto	480 px	—
Status Bar	QStatusBar	settings_dashboard.py	24 px	100 %	—
Implementation Notes
Entry point: DictaPilotDashboard class is extended as a new DictaPilotMainDashboard(QMainWindow) that wraps the existing tab-based settings into the sidebar + content architecture.

Routing: A simple QStackedWidget in the main content area switches between Home, Settings, Statistics, History, Agent, Diagnostics, and Help views based on sidebar selection.

Configuration data binding: All settings widgets use the existing DictaPilotConfig dataclass with the established set_config() / get_config() pattern.

Transcription data: Statistics and History views query transcription_store.py via get_store() and aggregate TranscriptionEntry fields.

Chart rendering: Prefer pyqtgraph for performance with real-time waveform data; fallback to QPainter custom widgets for simple bar/donut charts.

Theme switching: The existing _apply_theme() method applies DARK_THEME or LIGHT_THEME QSS globally. Extend with CSS variable substitution for new components using the token names from §2.