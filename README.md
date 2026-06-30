# novel-submission-loop

`novel-submission-loop` 是一个用于小说投稿循环工作流的 Codex skill 仓库。

## 内容

- `SKILL.md`：主工作流说明
- `agents/openai.yaml`：相关 agent 配置
- `editor_queue.py`：编辑队列辅助脚本

## 用途

用于按固定流程执行小说投稿任务，包括：

- 读取编辑偏好
- 选择投稿类型
- 生成候选书和目标书
- 写作章节大纲与正文
- 生成 Word 稿件
- 准备邮件预览并在确认后发送

## 说明

该仓库以 `SKILL.md` 中定义的固定流程为准，具体执行顺序不要随意改动。
