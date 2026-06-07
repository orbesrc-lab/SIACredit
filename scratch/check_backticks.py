with open('c:/SIAC/scratch/test.js', 'r', encoding='utf-8') as f:
    content = f.read()
print('Backticks:', content.count('`'))
