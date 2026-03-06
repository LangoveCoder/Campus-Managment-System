path = r"E:\The CMS\modules\attendance\views_html.py"
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open("attendance_imports.txt", "w", encoding="utf-8") as out:
    for i, line in enumerate(lines, 1):
        if 'import' in line or '.objects.' in line:
            out.write(f"Line {i}: {repr(line)}\n")
