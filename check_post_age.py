"""
check_post_age.py - How old is that LinkedIn post, really?

LinkedIn buries the post timestamp in the activity ID. "3 weeks ago" is vague
and posts get bumped, so decode it before you spend a message on a dead lead.

    https://www.linkedin.com/posts/someone_slug-activity-7485604048881229836-Vn3h
                                                       ^^^^^^^^^^^^^^^^^^^

Usage:
    python check_post_age.py 7485604048881229836
    python check_post_age.py "https://www.linkedin.com/posts/..."
    python check_post_age.py 7485604048881229836 7465427003488354305
"""

import re
import sys
from datetime import datetime, timezone


def activity_id_from(text):
    """Accept a bare ID or a full LinkedIn post URL."""
    text = text.strip()
    if text.isdigit():
        return int(text)
    match = re.search(r"activity[-:](\d{15,25})", text)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d{18,20})", text)
    return int(match.group(1)) if match else None


def posted_at(activity_id):
    """First 41 bits of the ID are a Unix timestamp in milliseconds."""
    return datetime.fromtimestamp((activity_id >> 22) / 1000, tz=timezone.utc)


def verdict(days):
    if days < 1:
        return "HOT", "Under 24h. Message now - first responders win."
    if days < 3:
        return "WARM", "1-3 days. Still worth a message today."
    if days < 7:
        return "COOL", "Under a week. Likely has replies already. Low priority."
    if days < 14:
        return "STALE", "1-2 weeks. Probably filled. Only if it's a perfect fit."
    return "DEAD", "Over 2 weeks. Skip it - spend the time on a fresh lead."


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    now = datetime.now(timezone.utc)

    for raw in args:
        activity_id = activity_id_from(raw)
        if not activity_id:
            print(f"\n  ? Could not find an activity ID in: {raw}")
            continue

        try:
            when = posted_at(activity_id)
        except (ValueError, OSError, OverflowError):
            print(f"\n  ? {activity_id} does not decode to a valid date "
                  f"(is it really a LinkedIn activity ID?)")
            continue

        days = (now - when).total_seconds() / 86400
        if days < 0:
            print(f"\n  ? {activity_id} decodes to a future date - not a valid ID")
            continue

        label, advice = verdict(days)

        if days < 1:
            age = f"{days * 24:.1f} hours"
        else:
            age = f"{days:.1f} days"

        print(f"\n  {label}  posted {when.strftime('%Y-%m-%d %H:%M')} UTC  ({age} ago)")
        print(f"        {advice}")

    print()


if __name__ == "__main__":
    main()
