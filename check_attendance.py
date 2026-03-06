path = r"E:\The CMS\modules\attendance\views_html.py"
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if 'import' in line or '.objects.' in line:
        print(f"Line {i}: {repr(line)}")
