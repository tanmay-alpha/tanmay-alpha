import datetime
import os
import re

def update_streak():
    start_date = datetime.date(2026, 5, 7)
    today = datetime.date.today()
    
    # If system date is prior to start_date for some reason, fallback to start_date
    if today < start_date:
        today = start_date

    days_count = (today - start_date).days + 1
    
    # Date string formats
    readme_end_date = f"{today.strftime('%B')} {today.day}, {today.year}"
    svg_end_date = f"{today.strftime('%b')} {today.day}"
    
    # 1. Update README.md
    readme_path = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        new_streak_line = f"Streak Range  : May 7, 2026 – {readme_end_date} ({days_count}-Day Continuous Streak)"
        content = re.sub(r"Streak Range\s*:.*", new_streak_line, content)
        
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated README.md: {new_streak_line}")

    # 2. Update .github/streak.svg
    svg_path = os.path.join(os.path.dirname(__file__), "..", "streak.svg")
    if os.path.exists(svg_path):
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
        
        # Replace current streak & longest streak text values
        # <text class="stat" x="82.5" y="112" text-anchor="middle">102</text>
        # <text class="subtext" x="82.5" y="160" text-anchor="middle">May 7 - Aug 16</text>
        # <text class="stat" x="82.5" y="95" text-anchor="middle">102</text>
        # <text class="subtext" x="82.5" y="155" text-anchor="middle">May 7 - Aug 16</text>
        
        svg_content = re.sub(
            r'(<text class="stat" x="82\.5" y="112" text-anchor="middle">)\d+(</text>)',
            rf'\g<1>{days_count}\g<2>',
            svg_content
        )
        svg_content = re.sub(
            r'(<text class="subtext" x="82\.5" y="160" text-anchor="middle">)May 7 - [^<]+(</text>)',
            rf'\g<1>May 7 - {svg_end_date}\g<2>',
            svg_content
        )
        svg_content = re.sub(
            r'(<text class="stat" x="82\.5" y="95" text-anchor="middle">)\d+(</text>)',
            rf'\g<1>{days_count}\g<2>',
            svg_content
        )
        svg_content = re.sub(
            r'(<text class="subtext" x="82\.5" y="155" text-anchor="middle">)May 7 - [^<]+(</text>)',
            rf'\g<1>May 7 - {svg_end_date}\g<2>',
            svg_content
        )
        
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Updated streak.svg: Streak {days_count}, Date range May 7 - {svg_end_date}")

if __name__ == "__main__":
    update_streak()
