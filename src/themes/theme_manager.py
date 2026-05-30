import ttkbootstrap as ttk


class ThemeManager:
    """Centralized helper for managing ttkbootstrap themes across the app."""

    _style: ttk.Style | None = None

    @staticmethod
    def get_themes():
        """
        Return a list of available ttkbootstrap themes.

        Falls back to a fixed list if theme names cannot be retrieved.
        """
        try:
            # Prefer the existing style instance if already created
            if ThemeManager._style is None:
                tmp_style = ttk.Style()
            else:
                tmp_style = ThemeManager._style
            names = list(tmp_style.theme_names())
            # Ensure a stable ordering
            names.sort()
            return names
        except Exception:
            # Reasonable default set of popular ttkbootstrap themes
            return [
                "cosmo",
                "flatly",
                "journal",
                "litera",
                "minty",
                "pulse",
                "sandstone",
                "united",
                "yeti",
                "darkly",
                "cyborg",
                "solar",
                "superhero",
            ]

    @staticmethod
    def apply_theme(root, theme_name: str | None = None):
        """
        Initialize or switch the global ttkbootstrap.Style theme.

        Returns the Style instance in use.
        """
        # If a style already exists and no specific theme is requested, keep the existing one.
        if ThemeManager._style is not None and not theme_name:
            return ThemeManager._style

        theme = theme_name or "cosmo"

        # First-time initialization
        if ThemeManager._style is None:
            ThemeManager._style = ttk.Style(theme=theme)
        else:
            # Ensure the style is bound to the current root
            try:
                # Newer ttkbootstrap exposes `.master`; older versions may ignore this
                ThemeManager._style.master = root  # type: ignore[attr-defined]
            except Exception:
                pass

            try:
                ThemeManager._style.theme_use(theme)
            except Exception:
                # If theme is invalid, silently ignore and keep current
                pass

        return ThemeManager._style

