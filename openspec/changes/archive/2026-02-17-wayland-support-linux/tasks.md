## 1. Display Server Detection

- [x] 1.1 Create display_server.py module with detection functions
- [x] 1.2 Implement detect_display_server() using XDG_SESSION_TYPE
- [x] 1.3 Add fallback detection using WAYLAND_DISPLAY and DISPLAY
- [x] 1.4 Add manual override via DISPLAY_SERVER env var
- [x] 1.5 Add unit tests for detection logic
- [ ] 1.6 Test detection on X11 and Wayland systems

## 2. Wayland Backend Implementation

- [x] 2.1 Create wayland_backend.py module
- [x] 2.2 Implement WaylandHotkeyBackend class
- [x] 2.3 Add XDG portal integration using PyGObject (optional)
- [x] 2.4 Implement portal hotkey registration
- [x] 2.5 Add pynput fallback for hotkey backend
- [x] 2.6 Implement WaylandPasteBackend class
- [x] 2.7 Add wl-clipboard integration (wl-copy)
- [x] 2.8 Add keyboard simulation using wtype or pynput
- [x] 2.9 Implement paste timing and delays
- [x] 2.10 Add fallback chain for paste backend

## 3. Backend Selection Logic

- [x] 3.1 Modify app.py to detect display server at startup
- [x] 3.2 Implement backend selection based on display server
- [x] 3.3 Add has_portal() check for XDG portal availability
- [x] 3.4 Add has_wl_clipboard() check for wl-clipboard
- [x] 3.5 Implement select_backend() function with fallback logic
- [x] 3.6 Add logging for backend selection decisions

## 4. Configuration Updates

- [x] 4.1 Add DISPLAY_SERVER config option to config.py
- [x] 4.2 Add WAYLAND_COMPOSITOR config option
- [x] 4.3 Update HOTKEY_BACKEND to support "wayland" option
- [x] 4.4 Update PASTE_BACKEND to support "wayland" option
- [x] 4.5 Add configuration validation for Wayland options

## 5. Permission Handling

- [x] 5.1 Implement permission request handling in WaylandHotkeyBackend
- [x] 5.2 Add console message when permission dialog appears
- [x] 5.3 Handle permission granted response
- [x] 5.4 Handle permission denied response with fallback
- [x] 5.5 Add logging for permission events
- [x] 5.6 Implement permission re-request mechanism

## 6. Integration

- [x] 6.1 Integrate display server detection into app.py startup
- [x] 6.2 Update paste_utils.py to use Wayland backend
- [x] 6.3 Add Wayland backend to hotkey manager
- [x] 6.4 Ensure X11 backend still works (backward compatibility)
- [x] 6.5 Add error handling for backend initialization failures
- [ ] 6.6 Test backend switching between X11 and Wayland

## 7. Dependencies

- [x] 7.1 Add PyGObject to requirements-dev.txt (optional)
- [x] 7.2 Document wl-clipboard system package requirement
- [x] 7.3 Document wtype system package requirement (optional)
- [x] 7.4 Add dependency checks at startup
- [x] 7.5 Show installation instructions for missing dependencies

## 8. Testing

- [ ] 8.1 Test on GNOME (Wayland) - Ubuntu 22.04+
- [ ] 8.2 Test on KDE Plasma (Wayland) - Fedora 35+
- [ ] 8.3 Test on Sway (tiling Wayland compositor)
- [ ] 8.4 Test X11 fallback on Wayland systems
- [ ] 8.5 Test pure X11 systems (ensure no regression)
- [ ] 8.6 Test permission dialog flow
- [ ] 8.7 Test with wl-clipboard installed
- [ ] 8.8 Test without wl-clipboard (fallback)
- [ ] 8.9 Test with PyGObject installed
- [ ] 8.10 Test without PyGObject (fallback)
- [ ] 8.11 Test hotkey registration and triggering
- [ ] 8.12 Test text pasting functionality
- [ ] 8.13 Test backend selection logic
- [ ] 8.14 Test manual backend override

## 9. Documentation

- [x] 9.1 Update docs/platform-guides/linux.md with Wayland section
- [x] 9.2 Add Wayland setup instructions
- [x] 9.3 Document wl-clipboard installation per distro
- [x] 9.4 Document PyGObject installation (optional)
- [x] 9.5 Add Wayland troubleshooting section
- [x] 9.6 Document permission dialog handling
- [x] 9.7 Add compositor-specific notes (GNOME, KDE, Sway)
- [x] 9.8 Update README.md with Wayland support mention
- [x] 9.9 Update FAQ with Wayland questions

## 10. Performance and Optimization

- [x] 10.1 Measure paste performance on Wayland vs X11
- [x] 10.2 Optimize subprocess calls (wl-copy, wtype)
- [x] 10.3 Add caching for display server detection
- [x] 10.4 Profile hotkey latency on Wayland
- [x] 10.5 Optimize backend selection logic

## 11. Error Handling

- [x] 11.1 Add error handling for portal connection failures
- [x] 11.2 Add error handling for wl-clipboard failures
- [x] 11.3 Add error handling for keyboard simulation failures
- [x] 11.4 Provide clear error messages for common issues
- [x] 11.5 Add troubleshooting hints in error messages

## 12. Final Polish

- [x] 12.1 Code review for Wayland backend implementation
- [x] 12.2 Ensure consistent error handling across backends
- [x] 12.3 Verify logging is appropriate (not too verbose)
- [x] 12.4 Update CHANGELOG.md with Wayland support
- [ ] 12.5 Create announcement for Wayland support
