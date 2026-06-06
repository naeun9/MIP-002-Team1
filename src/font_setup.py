"""matplotlib 한글 폰트 + 다크 테마 크로스 플랫폼 설정"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

_NANUM_PATHS = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    str(Path(__file__).parent.parent / "assets" / "NanumGothic.ttf"),
    str(Path.home() / "AppData/Local/Microsoft/Windows/Fonts/NanumGothicRegular.ttf"),
    str(Path.home() / "AppData/Local/Microsoft/Windows/Fonts/NanumGothic.ttf"),
    "C:/Windows/Fonts/NanumGothic.ttf",
]
_FALLBACK = ["NanumSquare", "NanumGothic", "Malgun Gothic", "AppleGothic", "sans-serif"]


def setup():
    """한글 폰트 + 다크 테마 rcParams를 설정한다."""
    # ── 폰트 선택 ──────────────────────────────────────────
    for fp in _NANUM_PATHS:
        if Path(fp).exists():
            fm.fontManager.addfont(fp)
            plt.rcParams["font.family"] = "NanumGothic"
            break
    else:
        available = {f.name for f in fm.fontManager.ttflist}
        for family in _FALLBACK:
            if family in available:
                plt.rcParams["font.family"] = family
                break

    # ── 다크 테마 ──────────────────────────────────────────
    DARK_BG  = "#13172b"
    AXES_BG  = "#1a2035"
    GRID_COL = "#2a3050"
    TEXT_COL = "#cbd5e1"
    TICK_COL = "#94a3b8"
    EDGE_COL = "#2e3a54"

    plt.rcParams.update({
        "axes.unicode_minus":   False,
        "figure.facecolor":     DARK_BG,
        "figure.edgecolor":     "none",
        "axes.facecolor":       AXES_BG,
        "axes.edgecolor":       EDGE_COL,
        "axes.labelcolor":      TEXT_COL,
        "axes.spines.top":      False,
        "axes.spines.right":    False,
        "xtick.color":          TICK_COL,
        "ytick.color":          TICK_COL,
        "text.color":           TEXT_COL,
        "grid.color":           GRID_COL,
        "grid.linestyle":       "--",
        "grid.linewidth":       0.6,
        "legend.facecolor":     "#1e2540",
        "legend.edgecolor":     EDGE_COL,
        "legend.labelcolor":    TEXT_COL,
        "legend.framealpha":    0.85,
        "savefig.facecolor":    DARK_BG,
        "savefig.edgecolor":    "none",
        "figure.dpi":           120,
    })
