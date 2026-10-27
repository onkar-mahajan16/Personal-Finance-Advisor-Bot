from datetime import date, datetime


def current_month() -> str:
    return date.today().strftime("%Y-%m")


def valid_month(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m")
        return True
    except (TypeError, ValueError):
        return False


def month_bounds(month: str):
    """Return (first day, first day of next month) for a 'YYYY-MM' string."""
    year, mon = map(int, month.split("-"))
    start = date(year, mon, 1)
    end = date(year + 1, 1, 1) if mon == 12 else date(year, mon + 1, 1)
    return start, end


def shift_month(month: str, delta: int) -> str:
    year, mon = map(int, month.split("-"))
    idx = year * 12 + (mon - 1) + delta
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def parse_date(value):
    if not value:
        return date.today()
    return datetime.strptime(value, "%Y-%m-%d").date()
