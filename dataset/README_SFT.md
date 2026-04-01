SFT 数据集说明

此目录下的 `build_sft.py` 可用于生成小规模 SFT 数据集（示例约 5k 条），输出为 JSONL，每行包含:

```
{ "conversations": [ {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ... ] }
```

建议：
- 将生成文件保存为 `dataset/sft_mini_512.jsonl`，以便直接供 `trainer/train_full_sft.py` 使用。
- 生成后请用当前环境的 tokenizer 做一次 tokenize 检查，确保 `max_length` 设置合适。

使用示例：
```
python dataset/build_sft.py --num 5000 --out dataset/sft_mini_512.jsonl
```

该脚本仅用于示例和快速复现；线上或正式实验请替换为人工标注或更丰富的数据来源，并做严格的质量抽检。
