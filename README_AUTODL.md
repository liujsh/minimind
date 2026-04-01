在 Autodl（支持 Docker）上运行 SFT 的最小化说明

目标：用尽量少的资源完成对 `dataset/sft_mini_512.jsonl` 的微调。优先使用 LoRA 模式以节省显存和时间。

推荐资源（成本/时间折中）：
- 优先：1 x A100-40GB 或 1 x RTX4090 (24GB) —— 可直接跑 Full SFT 或 LoRA。 
- 更省钱：1 x V100 (16GB) 或 1 x RTX3080 (10-12GB) —— 建议只跑 LoRA 或把 `--batch_size` 减小并使用梯度累积。

步骤概览：
1. 在 Autodl 上创建任务并选择支持 GPU 的 Docker 运行环境。上传整个仓库到作业工作目录。
2. 构建镜像（推荐）或直接在基镜像上运行。

构建镜像（在 Autodl 的构建步骤中执行）：
```
docker build -t minimind:autodl .
```

运行容器并执行训练（示例：使用 LoRA，GPU 0）：
```
docker run --gpus all -it --rm -v $(pwd):/workspace/minimind -w /workspace/minimind minimind:autodl bash -c "./run_sft.sh lora 0"
```

如果集群使用 SLURM 或任务脚本，请在提交脚本里调用上面的 `docker run` 命令。

节省成本的小技巧：
- 使用 LoRA（`run_sft.sh` 默认）代替 full fine-tune，可大幅降低显存与训练时间。 
- 将 `--epochs` 和 `--batch_size` 设置为较小值做试验，确认无误后再放大。 
- 使用 `--use_wandb` 时注意网络与 API key，或临时关闭以减少外部依赖。

上传数据：保证 `dataset/sft_mini_512.jsonl` 随仓库一并上传，或在容器内从云盘/对象存储拉取到 `dataset/`。

运行后检视：训练脚本会把模型保存在 `--save_dir` 指定目录（默认 `../out`），请在容器运行结束前把权重拷贝到外部卷或云存储。
