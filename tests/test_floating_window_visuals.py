import pytest

app = pytest.importorskip("app")


def test_visual_state_mapping():
    assert app._resolve_visual_state("record") == "record"
    assert app._resolve_visual_state("recording") == "record"
    assert app._resolve_visual_state("processing") == "processing"
    assert app._resolve_visual_state("transcribing") == "processing"
    assert app._resolve_visual_state("done") == "done"
    assert app._resolve_visual_state("complete") == "done"
    assert app._resolve_visual_state("idle") == "idle"
    assert app._resolve_visual_state("unknown") == "idle"


def test_theme_and_motion_fallbacks():
    theme = app._resolve_theme("not-a-theme")
    motion = app._resolve_motion_profile("not-a-profile")
    assert theme == app._FLOATING_THEME_PRESETS["professional_minimal"]
    assert motion == app._MOTION_PROFILE_PRESETS["expressive"]


def test_compute_bar_target_stays_in_bounds():
    amplitudes = [0.0, 0.2, 0.6, 1.0, 1.2]
    motion = app._resolve_motion_profile("expressive")
    for mode in ("record", "processing", "done", "idle", "unknown"):
        for idx in range(len(amplitudes)):
            value = app._compute_bar_target(
                mode=mode,
                bar_idx=idx,
                bar_count=len(amplitudes),
                amplitudes=amplitudes,
                level_peak=0.18,
                expressive_level=0.84,
                now=123.456,
                motion=motion,
            )
            assert 0.0 <= value <= 1.0


def test_env_float_clamps_invalid_values(monkeypatch):
    monkeypatch.setenv("FLOATING_TEST_FLOAT", "invalid")
    assert app._env_float("FLOATING_TEST_FLOAT", 0.75, 0.0, 1.0) == 0.75

    monkeypatch.setenv("FLOATING_TEST_FLOAT", "9.0")
    assert app._env_float("FLOATING_TEST_FLOAT", 0.75, 0.0, 1.0) == 1.0

    monkeypatch.setenv("FLOATING_TEST_FLOAT", "-3")
    assert app._env_float("FLOATING_TEST_FLOAT", 0.75, 0.0, 1.0) == 0.0


def test_build_waveform_points_geometry_is_wide_and_bounded():
    points = app._build_waveform_points(
        current_heights=[0.05, 0.22, 0.64, 0.36, 0.12],
        bar_count=5,
        mid_x=72.0,
        mid_y=18.0,
        icon_w=54.0,
        icon_h=14.0,
        now=123.456,
        is_recording=True,
    )
    assert len(points) == 33

    xs = [x for x, _ in points]
    ys = [y for _, y in points]

    assert all(xs[i] < xs[i + 1] for i in range(len(xs) - 1))
    assert (xs[-1] - xs[0]) == pytest.approx(54.0 * 0.92, rel=1e-6)

    min_y = 18.0 - (14.0 * 0.46)
    max_y = 18.0 + (14.0 * 0.46)
    assert all(min_y <= y <= max_y for y in ys)
    assert all(app.np.isfinite(x) and app.np.isfinite(y) for x, y in points)


def test_build_waveform_points_stays_visible_at_low_levels():
    low_points = app._build_waveform_points(
        current_heights=[0.0, 0.0, 0.0, 0.0, 0.0],
        bar_count=5,
        mid_x=48.0,
        mid_y=16.0,
        icon_w=46.0,
        icon_h=12.0,
        now=42.0,
        is_recording=False,
    )
    high_points = app._build_waveform_points(
        current_heights=[0.9, 0.95, 1.0, 0.95, 0.9],
        bar_count=5,
        mid_x=48.0,
        mid_y=16.0,
        icon_w=46.0,
        icon_h=12.0,
        now=42.0,
        is_recording=False,
    )

    low_span = max(y for _, y in low_points) - min(y for _, y in low_points)
    high_span = max(y for _, y in high_points) - min(y for _, y in high_points)

    assert low_span > 1.2
    assert high_span >= low_span


def test_build_waveform_points_handles_mismatched_bar_lengths():
    points = app._build_waveform_points(
        current_heights=[0.25, 0.4],
        bar_count=5,
        mid_x=64.0,
        mid_y=16.0,
        icon_w=50.0,
        icon_h=12.0,
        now=19.0,
        is_recording=True,
    )
    assert len(points) == 33
    assert all(points[i][0] < points[i + 1][0] for i in range(len(points) - 1))
    assert all(app.np.isfinite(x) and app.np.isfinite(y) for x, y in points)
