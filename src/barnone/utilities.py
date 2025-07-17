def gradient_color(progress: float, gradient_edge: float = 0.4, gradient_edge2: float = 0.65) -> str:
    """Gradient: soft red → warm gold → deep green (19,154,21)."""
    if progress < gradient_edge:
        t = progress / gradient_edge
        r = round(230 + 10 * t)
        g = round(90 + 110 * t)
        b = round(90 + 10 * t)

    elif progress < gradient_edge2:
        t = (progress - gradient_edge) / (gradient_edge2 - gradient_edge)
        r = round(240 - 120 * t)
        g = round(200 - 20 * t)
        b = round(100 - 20 * t)

    else:
        t = (progress - gradient_edge2) / (1 - gradient_edge2)
        r = round(120 - 101 * t)
        g = round(180 - 26 * t)
        b = round(80 - 59 * t)

    return f"\033[38;2;{r};{g};{b}m"


def format_time(seconds: float) -> str:
    if seconds < 10:  # noqa: PLR2004
        return f"{seconds:.1f}s"
    seconds = round(seconds)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)

    if hours:
        return f"{hours}h {mins}m {secs}s"
    if mins:
        return f"{mins}m {secs}s"
    return f"{secs}s"
