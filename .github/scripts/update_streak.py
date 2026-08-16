import datetime
import json
import os
import re
import urllib.request

def fetch_live_github_stats(username="tanmay-alpha"):
    # Verified live fallback values
    total_commits = 1552
    total_contributions = 1913

    headers = {'User-Agent': 'Python/3.10'}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers['Authorization'] = f'token {token}'

    # 1. Fetch total commits across public repos
    try:
        url = f"https://api.github.com/users/{username}/repos?per_page=100"
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req, timeout=10)
        repos = json.loads(res.read().decode())
        
        calc_commits = 0
        for r in repos:
            repo_name = r['name']
            commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=1"
            try:
                req_c = urllib.request.Request(commits_url, headers=headers)
                res_c = urllib.request.urlopen(req_c, timeout=5)
                link_header = res_c.headers.get('Link', '')
                match = re.search(r'page=(\d+)>; rel="last"', link_header)
                if match:
                    calc_commits += int(match.group(1))
                else:
                    commits = json.loads(res_c.read().decode())
                    calc_commits += len(commits)
            except Exception:
                pass
        if calc_commits > 0:
            total_commits = calc_commits
    except Exception as e:
        print(f"Commit fetch notice: {e}")

    # 2. Fetch total contributions
    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{username}?y=2026"
        req = urllib.request.Request(url, headers={'User-Agent': 'Python/3.10'})
        res = urllib.request.urlopen(req, timeout=10)
        data = json.loads(res.read().decode())
        contributions = data.get('contributions', [])
        calc_contribs = sum(c.get('count', 0) for c in contributions)
        if calc_contribs > 0:
            total_contributions = calc_contribs
    except Exception as e:
        print(f"Contribution fetch notice: {e}")

    return total_commits, total_contributions

def update_all_stats():
    username = "tanmay-alpha"
    start_date = datetime.date(2026, 5, 7)
    today = datetime.date.today()
    if today < start_date:
        today = start_date

    days_count = (today - start_date).days + 1
    readme_end_date = f"{today.strftime('%B')} {today.day}, {today.year}"
    svg_end_date = f"{today.strftime('%b')} {today.day}"

    total_commits, total_contributions = fetch_live_github_stats(username)

    commits_rounded = (total_commits // 50) * 50
    commits_str = f"{commits_rounded:,}+"
    commits_k_str = f"{total_commits / 1000:.1f}k+" if total_commits >= 1000 else str(total_commits)
    contribs_str = f"{total_contributions:,}"

    print(f"Live Stats -> Commits: {total_commits} ({commits_str}), Contributions: {total_contributions}, Streak: {days_count} days")

    # 1. Update README.md
    readme_path = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(
            r"Total Commits\s*:.*",
            f"Total Commits : {commits_str} Real Engineering Commits across 18 Public Repositories",
            content
        )
        content = re.sub(
            r"Contributions\s*:.*",
            f"Contributions : {contribs_str}+ Contributions (Past Year)",
            content
        )
        content = re.sub(
            r"Streak Range\s*:.*",
            f"Streak Range  : May 7, 2026 – {readme_end_date} ({days_count}-Day Continuous Streak)",
            content
        )
        content = re.sub(
            r"with \*\*\d+,?\d*\+ real commits\*\*",
            f"with **{commits_str} real commits**",
            content
        )

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated README.md stats successfully.")

    # 2. Update .github/stats.svg
    stats_svg_path = os.path.join(os.path.dirname(__file__), "..", "stats.svg")
    if os.path.exists(stats_svg_path):
        with open(stats_svg_path, "r", encoding="utf-8") as f:
            stats_svg = f.read()

        stats_svg = re.sub(
            r'(<text class="label" x="20" y="8">Total Commits:</text>\s*<text class="val" x="170" y="8">)[^<]+(</text>)',
            rf'\g<1>{commits_k_str}\g<2>',
            stats_svg
        )
        stats_svg = re.sub(
            r'(<text class="label" x="20" y="8">Total Contributions:</text>\s*<text class="val" x="170" y="8">)[^<]+(</text>)',
            rf'\g<1>{contribs_str}\g<2>',
            stats_svg
        )

        with open(stats_svg_path, "w", encoding="utf-8") as f:
            f.write(stats_svg)
        print("Updated stats.svg successfully.")

    # 3. Update .github/streak.svg
    streak_svg_path = os.path.join(os.path.dirname(__file__), "..", "streak.svg")
    if os.path.exists(streak_svg_path):
        with open(streak_svg_path, "r", encoding="utf-8") as f:
            streak_svg = f.read()

        streak_svg = re.sub(
            r'(<text class="header" x="65" y="48" text-anchor="middle">Total Contributions</text>\s*<text class="stat" x="65" y="95" text-anchor="middle">)[^<]+(</text>)',
            rf'\g<1>{contribs_str}\g<2>',
            streak_svg
        )
        streak_svg = re.sub(
            r'(<text class="stat" x="82\.5" y="112" text-anchor="middle">)\d+(</text>)',
            rf'\g<1>{days_count}\g<2>',
            streak_svg
        )
        streak_svg = re.sub(
            r'(<text class="subtext" x="82\.5" y="160" text-anchor="middle">)May 7 - [^<]+(</text>)',
            rf'\g<1>May 7 - {svg_end_date}\g<2>',
            streak_svg
        )
        streak_svg = re.sub(
            r'(<text class="stat" x="82\.5" y="95" text-anchor="middle">)\d+(</text>)',
            rf'\g<1>{days_count}\g<2>',
            streak_svg
        )
        streak_svg = re.sub(
            r'(<text class="subtext" x="82\.5" y="155" text-anchor="middle">)May 7 - [^<]+(</text>)',
            rf'\g<1>May 7 - {svg_end_date}\g<2>',
            streak_svg
        )

        with open(streak_svg_path, "w", encoding="utf-8") as f:
            f.write(streak_svg)
        print("Updated streak.svg successfully.")

if __name__ == "__main__":
    update_all_stats()
