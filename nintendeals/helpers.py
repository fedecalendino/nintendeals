from datetime import datetime


def filter_by_date(
    release_date: datetime = None,
    released_at: datetime = None,
    released_after: datetime = None,
    released_before: datetime = None,
) -> bool:
    if any([released_at, released_after, released_before]) \
            and not release_date:
        return False

    if released_at and release_date != released_at:
        return False

    if released_after and release_date < released_after:
        return False

    if released_before and release_date > released_before:
        return False

    return True
