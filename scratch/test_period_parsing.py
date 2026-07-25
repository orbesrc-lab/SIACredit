import re

def get_period_options_html(active_program_period):
    period_options_html = ''
    if active_program_period:
        years = re.findall(r'\b\d{4}\b', active_program_period)
        if years:
            if len(years) >= 2:
                start_year = min(int(years[0]), int(years[1]))
                end_year = max(int(years[0]), int(years[1]))
            else:
                start_year = int(years[0])
                end_year = start_year
            
            for y in range(end_year, start_year - 1, -1):
                period_options_html += f'<option value="{y}-2">{y}-2</option>\n'
                period_options_html += f'<option value="{y}-1">{y}-1</option>\n'
                
    if not period_options_html:
        period_options_html = """
            <option value="2025-1">2025-1</option>
            <option value="2024-2">2024-2</option>
            <option value="2024-1">2024-1</option>
            <option value="2023-2">2023-2</option>
            <option value="2023-1">2023-1</option>
        """
    return period_options_html

# Test cases
test_cases = [
    "2019-2026",
    "2019 - 2026",
    "2019",
    "",
    None,
    "rango invalido sin numeros",
    "2026 a 2019"
]

for i, tc in enumerate(test_cases):
    print(f"--- Test Case {i + 1}: \"{tc}\" ---")
    print(get_period_options_html(tc))
