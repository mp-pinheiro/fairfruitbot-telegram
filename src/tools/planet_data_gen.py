import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

from modules import AstroModule

astro = AstroModule()
years = [2024, 2025, 2026, 2027, 2028]


def process_date(d):
    print(f"Processing {d}...")
    date_iso = f"{d}T00:00:00"
    return (d, astro.get_astro_for_signs(date_iso))


def main():
    results = {}

    with ThreadPoolExecutor() as executor:
        futures = []
        for year in years:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)

            current_date = start_date
            while current_date <= end_date:
                d = current_date.strftime("%Y-%m-%d")
                futures.append(executor.submit(process_date, d))
                current_date += timedelta(days=1)

        for future in as_completed(futures):
            d, astro_data = future.result()
            results[d] = astro_data

    with open("data/planet_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
