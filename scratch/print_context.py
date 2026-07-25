with open('c:/SIAC/scratch/extracted.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Show the lines around the stack numbers
indices = [22, 26, 49]
for idx in indices:
    print(f"\n--- Line {idx} ---")
    start = max(0, idx - 3)
    end = min(len(lines), idx + 4)
    for i in range(start, end):
        prefix = "-> " if i + 1 == idx else "   "
        print(f"{prefix}{i+1}: {lines[i]}", end="")
