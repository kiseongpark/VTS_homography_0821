import csv

WORLD_CSV = "world_points.csv"  # 여기에 정확한 경로
with open(WORLD_CSV, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    print("필드명:", reader.fieldnames)
    for row in reader:
        print(row["id"], row["X"], row["Y"])
