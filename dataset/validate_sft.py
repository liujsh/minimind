import json
from pathlib import Path

def main(path='dataset/sft_mini_512.jsonl', n=5):
    p = Path(path)
    assert p.exists(), f'File not found: {path}'
    total = 0
    max_chars = 0
    min_chars = 10**9
    examples = []
    with p.open('r', encoding='utf-8') as f:
        for line in f:
            total += 1
            s = json.loads(line)
            txt = ''.join([m.get('content','') for m in s.get('conversations',[])])
            l = len(txt)
            max_chars = max(max_chars, l)
            min_chars = min(min_chars, l)
            if len(examples) < n:
                examples.append(s)

    print('Total samples:', total)
    print('Min chars:', min_chars, 'Max chars:', max_chars)
    print('\nExamples:')
    for i, e in enumerate(examples):
        print('--- sample', i+1, '---')
        for m in e['conversations']:
            role = m.get('role')
            content = m.get('content')
            print(f'[{role}]', content)
        print()

if __name__ == '__main__':
    main()
