with open(r"c:\SIAC\static\landing.css", "r", encoding="utf-8", errors="ignore") as f:
    print("--- landing.css Root Variables ---")
    for i in range(35):
        print(f.readline().strip())

with open(r"c:\SIAC\static\styles.css", "r", encoding="utf-8", errors="ignore") as f:
    print("\n--- styles.css Root Variables ---")
    for i in range(25):
        print(f.readline().strip())
