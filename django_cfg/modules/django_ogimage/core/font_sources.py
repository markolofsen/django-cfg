"""Remote font sources for lazy download.

All URLs point to variable-weight TTF files from github.com/google/fonts.
Verified working as of 2026-03.

To update a URL — find the file in https://github.com/google/fonts/tree/main/ofl/
and copy the raw link with URL-encoded brackets: [ → %5B, ] → %5D, , → %2C
"""

_GH = "https://github.com/google/fonts/raw/main/ofl"

SOURCES: dict[str, str] = {
    "Inter-Regular.ttf": f"{_GH}/inter/Inter%5Bopsz%2Cwght%5D.ttf",
    "Inter-Bold.ttf":    f"{_GH}/inter/Inter%5Bopsz%2Cwght%5D.ttf",
    "NotoSansArabic.ttf": f"{_GH}/notosansarabic/NotoSansArabic%5Bwdth%2Cwght%5D.ttf",
    "NotoSansHebrew.ttf": f"{_GH}/notosanshebrew/NotoSansHebrew%5Bwdth%2Cwght%5D.ttf",
    "NotoSansKR.ttf":    f"{_GH}/notosanskr/NotoSansKR%5Bwght%5D.ttf",
    "NotoSansJP.ttf":    f"{_GH}/notosansjp/NotoSansJP%5Bwght%5D.ttf",
    "NotoSansSC.ttf":    f"{_GH}/notosanssc/NotoSansSC%5Bwght%5D.ttf",
}
