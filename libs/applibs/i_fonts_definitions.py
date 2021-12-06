import os
from kivy.core.text import LabelBase


font_styles = {
    "H1": ["SpectralLight", 96, False, -1.5],
    "H2": ["SpectralLight", 60, False, -0.5],
    "H3": ["Spectral", 48, False, 0],
    "H4": ["Spectral", 34, False, 0.25],
    "H5": ["Spectral", 24, False, 0],
    "H6": ["SpectralLight", 20, False, 0.15],
    "Subtitle1": ["SpectralLight", 16, False, 0.15],
    "Subtitle2": ["SpectralLight", 14, False, 0.1],
    "Body1": ["Spectral", 16, False, 0.5],
    "Body2": ["Spectral", 14, False, 0.25],
    "Button": ["SpectralSemiBold", 14, True, 1.25],
    "Caption": ["Spectral", 12, False, 0.4],
    "Overline": ["Spectral", 10, True, 1.5],
    "Icon": ["Icons", 24, False, 0],
}


def register_fonts():
    fonts_path = os.path.join(os.environ["root_dir"], "assets", "fonts")
    spectral_fonts = [
        {
            "name": "Spectral",
            "fn_regular": fonts_path + f"{os.sep}spectral{os.sep}Spectral-Regular.ttf",
            "fn_bold": fonts_path + f"{os.sep}spectral{os.sep}Spectral-Bold.ttf",
            "fn_italic": fonts_path + f"{os.sep}spectral{os.sep}Spectral-Italic.ttf",
            "fn_bolditalic": fonts_path + f"{os.sep}spectral{os.sep}Spectral-BoldItalic.ttf",
        },
        {
            "name": "SpectralExtraLight",
            "fn_regular": fonts_path + f"{os.sep}spectral{os.sep}Spectral-ExtraLight.ttf",
            "fn_italic": fonts_path + f"{os.sep}spectral{os.sep}Spectral-ExtraLightItalic.ttf",
        },
        {
            "name": "SpectralLight",
            "fn_regular": fonts_path + f"{os.sep}spectral{os.sep}Spectral-Light.ttf",
            "fn_italic": fonts_path + f"{os.sep}spectral{os.sep}Spectral-LightItalic.ttf",
        },
        {
            "name": "SpectralSemiBold",
            "fn_regular": fonts_path + f"{os.sep}spectral{os.sep}Spectral-SemiBold.ttf",
            "fn_italic": fonts_path + f"{os.sep}spectral{os.sep}Spectral-SemiBoldItalic.ttf",
        },
        {
            "name": "SpectralExtraBold",
            "fn_regular": fonts_path + f"{os.sep}spectral{os.sep}Spectral-ExtraBold.ttf",
            "fn_italic": fonts_path + f"{os.sep}spectral{os.sep}Spectral-ExtraBoldItalic.ttf",
        },
        {
            "name": "Icons",
            "fn_regular": fonts_path + f"{os.sep}materialdesignicons-webfont.ttf",
        },
    ]
    for font in spectral_fonts:
        LabelBase.register(**font)
