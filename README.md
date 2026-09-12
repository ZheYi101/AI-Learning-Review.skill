# ai-learning-review

这是一个用来实验“AI 辅助学习之后，能不能不靠手工整理笔记，也让重要知识真正留下来”的 Codex skill。

它不是另一个知识管理软件，也不试图把每段 AI 对话都存起来。它是交给 agent 的一份工作说明：一次学习、项目讨论或排错结束后，agent 应该分辨哪些东西值得进入长期记忆、哪些只该留作可搜索参考、哪些需要以后再做一次情境练习。

目标是让学习成果逐渐变成可恢复的能力，而不是不断堆积一套最终不想打开的 Anki 卡。

## 为什么做这个

很多 AI 学习体验有一个断点：当下可以随时问、随时解释、随时带着做，但几个月后回到同一领域，仍然像从零开始。传统笔记能缓解这个问题，却经常因为整理成本高而中断。

这个 skill 的假设是：agent 可以把整理成本压到足够低，但它必须做**筛选和压缩**，而不是把聊天记录机械转成卡片。

它采用三层记忆：

- Anki 保存稳定、跨场景、忘掉代价高的概念与决策线索。
- Markdown Runbook 保存会变化的参数、完整步骤、版本差异和风险提示。
- 一个短情境题检验能否应用，而不是只认得答案。

## 适合谁

更适合：

- 平时经常借助 AI 学理论、课程、项目或技术工作流的人。
- 已经会用 Anki，愿意每天投入不超过约 15 分钟的人。
- 希望保留项目决策、排错经验和课程骨架，但不想维护复杂笔记系统的人。

当前不太适合：

- 主要目标是背诵大量事实、词汇或标准化题库的人。
- 希望自动存档全部对话、资料和代码上下文的人。
- 需要多人实时协作一套共享知识库的人。

语言学习、有媒体语境的词汇卡不在这里处理；请使用独立的语言学习或制卡 workflow。

## 这份 Skill 会做什么

每次整理会根据来源选择一种模式：

- `theory`：概念、因果、边界、对比和反例。
- `course`：课程重点、章节关系和考试理解点。
- `project`：决策、取舍、踩坑、验证和下次先检查什么。
- `workflow`：可复用流程、排错顺序、前置条件与风险。

它输出最多 3-7 个候选。每个候选明确标记：

- `memory`：是否值得进 Anki。
- `reference`：是否应进入可搜索的 Runbook 或项目档案。
- `practice`：是否应带一条情境练习。

这条上限是有意的。少量高价值卡比自动生成大量卡片更容易长期使用。

## 最小使用方式

学习或项目对话结束后，直接说：

```text
Use ai-learning-review to organize this session.

Source type: course
Domain: course-os
Keep only high-value, reusable items. Return at most 3-7 candidates.
```

Skill 返回 JSON 后，将内容保存为 `review.json` 并运行：

```powershell
python .\scripts\review_pack.py .\review.json --root .\learning-review
```

脚本会写入：

```text
learning-review/
|-- anki/
|   `-- AI-Learning-Review.tsv
`-- reviews/
    |-- YYYY-MM-DD-topic.json
    `-- YYYY-MM-DD-topic.md
`-- runbooks/
    `-- topic.md
```

将 `learning-review/anki/AI-Learning-Review.tsv` 导入 Anki，选择 Tab 分隔，字段映射为 `Front`、`Back`、`Tags`、`Source`。使用一个牌组 `AI Learning Review`，按标签而不是拆分牌组组织领域。

## 每日体验

这套 workflow 有一个硬上限：

- Anki 到期卡最多 12 分钟。
- 一条情境题或困难卡处理最多 3 分钟。
- 不追赶积压；到时即停，余下内容顺延。

建议每日新卡 3-5 张、复习上限 30 张。连续失败的卡应重写、拆分、暂停或删除，而不是反复硬背。

详细决策标准见 [review policy](references/review-policy.md)。

## 已验证，不等于已完全证明

当前已验证：

- `review_pack.py` 会校验候选数量、卡片字段和类型。
- 合法 JSON 可以生成可读记录、Anki TSV 和 Runbook。
- 相同卡片 ID 重复导出时不会重复追加 Anki 行。

当前尚未充分证明：

- 任何领域的 AI 自动筛选都能稳定挑出最值得长期记忆的内容。
- 3-7 个候选和 15 分钟预算适合每一个学习者。
- Anki 卡片本身足以让人迁移到复杂的新问题；因此保留了情境练习和 Runbook。

把它当作一个可试运行、可删卡、可调整的个人学习系统，而不是“永远不忘”的承诺。

## 外部依据

这个项目不实现新的记忆算法。它使用 Anki 或既有调度器，并将结构建立在主动提取、间隔复习和应用迁移之间的区别上：

- [Roediger & Karpicke, 2006](https://pubmed.ncbi.nlm.nih.gov/16507066/): 主动提取可改善延迟保持。
- [Cepeda et al., 2006](https://pubmed.ncbi.nlm.nih.gov/16719566/): 分布式练习对长期保持有效，具体间隔应随目标保留期变化。
- [Anki: Leeches](https://docs.ankiweb.net/leeches.html): 反复失败的卡片需要重写、拆分、暂停或删除。

这些证据支持“值得做少量的间隔检索”，不代表自动制卡或记住命令就会自动获得真实任务的迁移能力。

## 安装

将仓库克隆或复制到 Codex 的个人 Skill 目录：

```powershell
git clone https://github.com/ZheYi101/AI-Learning-Review.skill "$env:USERPROFILE\.agents\skills\ai-learning-review"
```

需要 Python 3.10+ 运行导出脚本；Anki 本身负责手机端与桌面端的复习同步。

## 仓库结构

```text
ai-learning-review/
|-- SKILL.md
|-- README.md
|-- LICENSE
|-- agents/
|   `-- openai.yaml
|-- references/
|   `-- review-policy.md
`-- scripts/
    `-- review_pack.py
```

## 反馈与迭代

欢迎通过 Issue 提交：卡片变成负担的案例、遗漏了关键经验的案例，以及更好的场景题设计。PR 也欢迎，但应保持这个项目的基本取向：减少复习负担、保留真实来源、避免将整段对话或一次性细节写进长期记忆。
