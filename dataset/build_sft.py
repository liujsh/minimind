"""生成小规模 SFT 数据集（JSONL 格式）

用法示例：
    python dataset/build_sft.py --num 5000 --out dataset/sft_mini_512.jsonl

生成格式：每行一个 JSON 对象，包含字段 `conversations`，是 role/content 的消息列表。
该脚本会做去重与简单长度过滤。
"""
import json
import random
import argparse
from pathlib import Path

USER_TEMPLATES = {
    'programming': [
        '请用 Python 写一个函数，输入一个整数列表，返回其中出现次数最多的元素（若有并列，返回任意一个）。',
        '修复以下代码的 bug：\n```py\ndef add(a, b):\n    return a - b\n```\n说明错误并给出正确实现。',
        '请用 Python 实现快速幂函数：计算 x 的 n 次幂，要求时间复杂度为 O(log n)。',
        '请写一个正则表达式，匹配符合中国大陆手机号码的字符串（考虑 11 位，三段式）。'
    ],
    'qa': [
        '请简洁解释什么是梯度消失问题，并给出两种常见的缓解方法。',
        '光合作用的基本过程是什么？请用两句话说明。',
        '什么是 ACID 特性（数据库）？每个字母代表什么？',
        '解释一下什么是熵（信息论中的熵），并给出生活中的一个类比。'
    ],
    'instruction': [
        '将下面这段文字压缩为一段不超过 50 字的摘要：\n\n人工智能正在快速发展，应用广泛，需要重视基础与伦理等问题。',
        '把这段中文翻译成英文：我今天学习了深度学习的基础概念。',
        '请把下面内容改写为面向初学者的说明，语气友好且通俗易懂：什么是正则表达式及其用途。'
    ],
    'multi_turn': [
        '我需要写一封邮件向导师请假三天，理由是生病，需要包含具体日期和礼貌措辞。',
        '我在练习算法题时遇到卡壳，如何高效提高算法能力？给出 5 条建议并推荐一本书。'
    ]
}

ASSISTANT_TEMPLATES = {
    'programming': [
        '下面是一个可工作的实现：\n```py\ndef mode_element(arr):\n    from collections import Counter\n    c = Counter(arr)\n    return c.most_common(1)[0][0]\n```\n时间复杂度 O(n)。',
        '错误在于函数做了减法而非加法。正确实现：\n```py\ndef add(a, b):\n    return a + b\n```',
        '快速幂实现：\n```py\ndef fast_pow(x, n):\n    res = 1\n    base = x\n    exp = n\n    while exp > 0:\n        if exp & 1:\n            res *= base\n        base *= base\n        exp >>= 1\n    return res\n```'
    ],
    'qa': [
        '梯度消失是指在深层神经网络中，反向传播时梯度逐层变小，导致前层参数更新缓慢。常见缓解方法：使用 ReLU 激活、初始化方法（如 He 初始化）和残差连接。',
        '光合作用是植物将光能转化为化学能的过程，主要发生在叶绿体，产生 O2 并固定 CO2 为糖类。'
    ],
    'instruction': [
        '摘要示例：人工智能快速发展，应用广泛，需重视基础与伦理（示例 50 字内）。',
        '英文翻译：I studied the basic concepts of deep learning today.'
    ],
    'multi_turn': [
        '尊敬的导师，您好：因近日身体不适，经医生建议需休息三天（2026-04-10 至 2026-04-12），特此请假。期间会安排同学代为处理事务，回来后及时补交工作。敬请批准。\n此致，敬礼。',
        '建议：\n1. 每周坚持刷题并总结模板；\n2. 做题时写出复杂度分析；\n3. 阅读经典书籍《算法导论》或《Algorithms》；\n4. 参加讨论组；\n5. 实战项目驱动练习。'
    ]
}

RANDOM_SUFFIXES = [
    '请给出示例。',
    '请给出时间复杂度分析。',
    '请用中文回答，并保持简洁。',
    '请给出实现细节并包含边界情况处理。',
    '请提供可直接运行的代码示例。'
]


def build_samples(num_samples: int):
    samples = []
    types = list(USER_TEMPLATES.keys())
    for i in range(num_samples):
        t = random.choices(types, weights=[0.4, 0.35, 0.15, 0.1], k=1)[0]
        user = random.choice(USER_TEMPLATES[t])

        # 随机增加后缀以提高多样性
        if random.random() < 0.6:
            user = user + ' ' + random.choice(RANDOM_SUFFIXES)

        # 30% 多轮对话扩展成2-3轮
        if t == 'multi_turn' or (random.random() < 0.3 and t != 'instruction'):
            conv = []
            conv.append({'role': 'user', 'content': user})
            # assistant reply
            a = random.choice(ASSISTANT_TEMPLATES.get(t, ASSISTANT_TEMPLATES['qa']))
            # assistant 可带随机说明
            if random.random() < 0.4:
                a = a + '\n' + random.choice(['提示：请注意边界条件。', '示例输出：...'])
            conv.append({'role': 'assistant', 'content': a})
            # optional follow-up
            if random.random() < 0.4:
                follow = '请再详细一点，包含示例。' if t == 'programming' else '能否给出一步步的说明？'
                conv.append({'role': 'user', 'content': follow})
                conv.append({'role': 'assistant', 'content': random.choice(ASSISTANT_TEMPLATES.get(t, ASSISTANT_TEMPLATES['qa']))})
        else:
            a = random.choice(ASSISTANT_TEMPLATES.get(t, ASSISTANT_TEMPLATES['qa']))
            if random.random() < 0.3:
                a = a + '\n' + random.choice(['补充：考虑时间复杂度。', '补充：考虑边界情况。'])
            conv = [{'role': 'user', 'content': user}, {'role': 'assistant', 'content': a}]

        samples.append({'conversations': conv})

    return samples


def simple_filter(samples, min_chars=10, max_chars=2000):
    out = []
    for s in samples:
        txt = ''.join([m['content'] for m in s['conversations'] if m.get('content')])
        if len(txt) < min_chars:
            continue
        if len(txt) > max_chars:
            continue
        out.append(s)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num', type=int, default=5000)
    parser.add_argument('--out', type=str, default='dataset/sft_mini_512.jsonl')
    args = parser.parse_args()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    print(f'Generating {args.num} raw samples...')
    raw = build_samples(args.num)
    print(f'Raw generated: {len(raw)}')

    filtered = simple_filter(raw)
    print(f'After length filter: {len(filtered)}')

    # 如果去重或过滤后数量不足，允许补采样
    if len(filtered) < args.num:
        need = args.num - len(filtered)
        print(f'补采样 {need} 条')
        extra = build_samples(need * 2)
        extra = simple_filter(extra)
        # append until reach
        i = 0
        while len(filtered) < args.num and i < len(extra):
            filtered.append(extra[i]); i += 1

    final = filtered[:args.num]
    print(f'Final samples: {len(final)}')

    with open(args.out, 'w', encoding='utf-8') as f:
        for s in final:
            f.write(json.dumps(s, ensure_ascii=False) + '\n')

    print('Saved to', args.out)


if __name__ == '__main__':
    main()
