---
name: ai-learning-review
description: Turn AI-assisted study and project sessions into a small, searchable review queue and Anki-importable cards. Use for robotics theory, university courses, and project decisions/workflows. Do not use for language learning or the separate anki-context-card-maker media workflow.
---

# AI Learning Review

把一次 AI 学习对话压缩成可长期恢复的知识，而不是转储聊天记录。

## 适用范围

默认接入：机器人理论、课程（AI、操作系统、JavaEE、数据库、软件工程）以及项目（LinguaLoop、JinDian）。

明确排除：英语、日语和其他语言学习；视频/音频语言卡；Fushi 风格媒体卡。语言学习继续调用 `anki-context-card-maker` 或用户现有语言工作流。

## 输入与模式

根据来源自动选择一个模式，也接受用户显式指定：

- `theory`：稳定概念、因果、边界、对比、反例
- `course`：课程重点、章节关系、考试理解点
- `project`：决策、取舍、踩坑、验证、下次先检查什么
- `workflow`：可复用流程、排错顺序、前置条件和风险

如果来源不明确，先询问一句“这是理论、课程、项目还是流程？”；不要猜测项目归属。

## 整理协议

1. 阅读本轮对话或用户指定材料，只使用有证据的内容。
2. 提取：新理解、纠正的误解、可复用方法、未解决问题。
3. 删除一次性路径、临时参数、重复内容、未经验证的推断和语言学习内容。
4. 最多输出 3-7 个候选；学习很短时可以输出 0 个。
5. 每个候选都要给出 `memory`、`reference`、`practice` 三个布尔判断及理由。
6. 只有稳定、可跨场景、忘掉代价高的内容才推荐 `memory=true`。
7. 复杂流程必须拆成情境题或多个决策点，不制作“背完整教程”卡。
8. 项目只保存可复用决策与经验；具体代码、路径和版本差异进 reference。
9. 对每张 `memory=true` 卡，必须给出 `context` 和 `explanation`；`context` 说明真实任务场景但不泄露答案，`explanation` 说明因果或关键区分。高风险或易混淆内容再给出 `pitfall`。

## 输出格式

先给用户简短摘要，再输出如下 JSON。JSON 必须是有效 UTF-8，字符串中的换行使用 `\\n`：

```json
{
  "source": {"title": "", "kind": "theory|course|project|workflow", "domain": "", "path_or_url": "", "date": "YYYY-MM-DD"},
  "summary": "本轮真正学会了什么",
  "candidates": [
    {
      "id": "stable-slug",
      "type": "concept|decision|scenario|error-pattern",
      "context": "1-3 句：当时在做什么、目标是什么、为什么此刻需要这个判断；不能泄露答案",
      "front": "一个需要主动回忆的问题；十秒内可理解",
      "back": "先给准确、短、可核对的答案；必要时含验证点",
      "explanation": "为什么这个答案成立，或它与相近概念的关键区别",
      "pitfall": "一个常见误区、失败后果或适用边界；没有则为空字符串",
      "tags": ["domain::robotics", "type::concept"],
      "memory": true,
      "reference": true,
      "practice": false,
      "reason": "为什么值得占用复习时间",
      "source_ref": "文件路径、URL或对话标题"
    }
  ],
  "reference_note": "适合搜索的 Runbook/摘要；没有则为空",
  "practice_prompt": "最多一条 3 分钟情境练习；没有则为空"
}
```

## Anki 规则

- 目标牌组固定为 `AI Learning Review`，不创建按领域拆分的牌组。
- 使用标签区分领域和类型，例如 `domain::course-os`、`domain::project-lingualoop`、`type::scenario`。
- 每日新卡建议 3-5 张，复习上限 30 张；以 12 分钟为硬上限，达到即停止。
- 正面按“场景 → 问题”呈现，背面按“答案 → 为什么 → 注意”呈现。答案本身应能在约 10 秒内核对；场景与解释用于恢复上下文，不应变成长教程。
- 不追赶积压；未完成的卡片顺延。

## 文件写入

在用户指定的目录中保存：

- `learning-review/reviews/YYYY-MM-DD-<slug>.json`：上述完整 JSON
- `learning-review/reviews/YYYY-MM-DD-<slug>.md`：人类可读摘要
- `learning-review/anki/AI-Learning-Review.tsv`：追加新卡，字段为 `Front<TAB>Back<TAB>Tags<TAB>Source`
- Runbook 默认写入 `learning-review/runbooks/<slug>.md`；若用户配置 `runbooks_root`，写入其指定的知识库目录（例如 Obsidian Vault）

用户可以一次配置 Runbook 位置：

```powershell
python .\scripts\review_pack.py --root .\learning-review --configure-runbooks-root "D:\Path\To\Obsidian\Runbooks"
```

之后可在单次导出中用 `--runbooks-root` 临时覆盖。不要替用户猜测或写入外部知识库路径，必须由用户明确指定。

不要覆盖同一 `id`；重复整理应更新对应记录或跳过，并在摘要中说明。

## 每日复习报告

当用户请求“今天复习”或“检查复习”时：

1. 读取 `learning-review/anki/review-log.json`（不存在则从空开始）。
2. 给出不超过 12 分钟的 Anki 任务和一条 3 分钟情境题。
3. 记录完成、跳过、困难卡和建议暂停项。
4. 不声称存在系统级提醒；该 Skill 只维护本地状态。

## 质量门槛

不要为了凑数生成卡片。优先少而稳定、能促进迁移的卡片；把易变细节交给可搜索参考资料，把能力验证交给真实练习。
