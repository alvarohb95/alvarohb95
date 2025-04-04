from __future__ import annotations

from typing import Iterable

from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes


class Theme(Base):
    def __init__(
        self,
        *,
        primary_hue: colors.Color | str = colors.lime,
        secondary_hue: colors.Color | str = colors.emerald,
        neutral_hue: colors.Color | str = colors.stone,
        spacing_size: sizes.Size | str = sizes.spacing_lg,
        radius_size: sizes.Size | str = sizes.radius_none,
        text_size: sizes.Size | str = sizes.text_md,
        font: fonts.Font | str | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("Quicksand"),
            "ui-sans-serif",
            "system-ui",
            "sans-serif",
        ),
        font_mono: fonts.Font | str | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("IBM Plex Mono"),
            "ui-monospace",
            "Consolas",
            "monospace",
        ),
    ):
        super().__init__(
            primary_hue=primary_hue,
            secondary_hue=secondary_hue,
            neutral_hue=neutral_hue,
            spacing_size=spacing_size,
            radius_size=radius_size,
            text_size=text_size,
            font=font,
            font_mono=font_mono,
        )
        self.name = "theme"
        super().set(
            # Colors
            slider_color="*neutral_900",
            slider_color_dark="*neutral_500",
            body_text_color="rgb(18,13,5)",
            block_label_text_color="rgb(243, 239, 224)",
            block_title_text_color="rgb(243, 239, 224)",
            body_text_color_subdued="*neutral_400",
            body_background_fill='*primary_800',
            background_fill_primary='*primary_600',
            background_fill_primary_dark='*primary_900',
            background_fill_secondary_dark='*primary_900',
            block_background_fill='rgb(53,66,48)',
            block_background_fill_dark="*neutral_800",
            input_background_fill_dark="*neutral_700",
            # Button Colors
            button_primary_background_fill="rgb(53,66,48)",
            button_primary_background_fill_hover='*primary_200',
            button_primary_text_color='*primary_600',
            button_primary_background_fill_dark="*neutral_600",
            button_primary_background_fill_hover_dark="*neutral_600",
            button_primary_text_color_dark="white",
            button_secondary_background_fill="*button_primary_background_fill",
            button_secondary_background_fill_hover="*button_primary_background_fill_hover",
            button_secondary_text_color="*button_primary_text_color",
            button_cancel_background_fill="*button_primary_background_fill",
            button_cancel_background_fill_hover="*button_primary_background_fill_hover",
            button_cancel_text_color="*button_primary_text_color",
            checkbox_label_background_fill="*button_primary_background_fill",
            checkbox_label_background_fill_hover="*button_primary_background_fill_hover",
            checkbox_label_text_color="*button_primary_text_color",
            checkbox_background_color_selected="*neutral_600",
            checkbox_background_color_dark="*neutral_700",
            checkbox_background_color_selected_dark="*neutral_700",
            checkbox_border_color_selected_dark="*neutral_800",
            # Padding
            checkbox_label_padding="*spacing_md",
            button_large_padding="*spacing_lg",
            button_small_padding="*spacing_sm",
            # Borders
            block_border_width="0px",
            block_border_width_dark="1px",
            shadow_drop_lg="0 1px 4px 0 rgb(0 0 0 / 0.1)",
            block_shadow="*shadow_drop_lg",
            block_shadow_dark="none",
            # Block Labels
            block_title_text_weight="600",
            block_label_text_weight="600",
            block_label_text_size="*text_md",
        )