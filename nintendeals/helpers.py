from datetime import datetime


def search_filter(
    game: "Game",
    title: str = None,
    released_at: datetime = None,
    released_after: datetime = None,
    released_before: datetime = None,
) -> bool:
    if title and title not in game.title:
        return False

    release_date = game.release_date

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
