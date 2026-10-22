# silas-skills

由 **zhangyuqian (Silas)** 实战打磨的 [Hermes Agent](https://hermes-agent.nousresearch.com) 技能集。

## 技能

### 🪔 一盏神灯（yizhan-shendeng）— 中文版

把一本书、一份长文档、课程讲稿、采访稿或会议记录**蒸馏成可被 AI 直接调用的技能包**。

产出的不是读书笔记、不是摘要——而是**让一个没读过这本书的人，在遇到具体问题时直接调用、并做成一件事的操作指令**。

工作方式：

- **五路并行提取**：框架 / 原则 / 案例 / 反例 / 术语 五条线分头提取，逐块回执、跨批对账
- **三重验证**：原文支撑 → 预测力 → 非常识（含「公开理论 vs 作者原创判据」的锋线区分与自动纠偏）
- **双层诱饵测试**：同源混淆 + 宿主混淆，防止新技能抢占既有技能触发
- **全自动执行**：闸门检查通过后一路跑到底；长任务可跨会话断点续跑
- 附全套 references（提取器、模板、大书分批实战手册、校验口径）与逐字校验脚本

### 🪔 Book to Skill Distiller（book-to-skill-distiller）— 英文版

**同一套方法的英文实现**，不是另一个方法。指令、12 篇 reference、脚本注释全部英文；工作区路径改为 ASCII（`blocks/` `cand/` `skills/` `state.md`），校验脚本同时认中英两种条目格式（旧的中文工作区仍可校验）。

适合给非中文使用者，或在英文语料上跑。

## 安装（Hermes Agent）

中文版：

```
hermes skills install "https://raw.githubusercontent.com/qianyu6a/silas-skills/main/skills/yizhan-shendeng/SKILL.md"
```

英文版：

```
hermes skills install "https://raw.githubusercontent.com/qianyu6a/silas-skills/main/skills/book-to-skill-distiller/SKILL.md"
```

或手动：把 `skills/<技能名>/` 目录整个复制进你的 Hermes 技能目录。

## 用法

完整操作说明见 **[USAGE.md](USAGE.md)**：触发话术、三道闸门、7 步流水线、产物结构、断点续跑、五个常见坑。

一句话版本：把文件发过去，说「用一盏神灯蒸馏这本书」，闸门过了它一路跑到底，产物在 `技能包/`（英文版是 `skills/`）。

其他支持 SKILL.md 的 agent（Claude Code、Cursor、Codex CLI 等）也能加载。差别在并行度：本方法靠五路子代理并行提取，单线程 agent 上会退化成串行——产物相同，耗时更长。

## 结构

```
skills/
  yizhan-shendeng/          # 中文版
    SKILL.md                # 主流程（8 步流水线）
    references/             # 提取器、模板、实战手册、校验口径
    scripts/                # 候选摘录逐字校验工具
  book-to-skill-distiller/  # 英文版（同一方法的英文实现）
    SKILL.md
    references/
    scripts/
```

## 来源与声明

- **两版是同一套方法的中文与英文实现**，英文版是中文版的翻译加工程化改造，不是两个独立的方法。
- **方法骨架参考自公开资料**（"把长文本蒸馏成可调用技能包"这一思路），未逐字复制任何原文。在此基础上做了实质性重写与扩展：五路并行提取、三重验证（原文支撑 → 预测力 → 非常识）、候选摘录逐字回引校验（含 `verify_candidates.py`）、双层诱饵测试、批量提取执行手册、断点续跑与成本核算——这些机制属本版新增与改造，与原版已有实质差异。
- **原始出处的作者若希望具名**，请在 Issues 里指出，我会补上署名与链接。
- **仓库内只有方法与脚本，不含任何书籍原文、课程讲义或受版权保护的内容**。技能运行时处理的是使用者自己提供的文本；用本方法处理第三方作品所需的授权，由使用者自行取得并承担责任。README 与技能文档中出现的书名（如 *Code Complete*、*Refactoring*）仅用于说明本方法在真实任务中的使用经历，不附带、也不分发任何书籍内容。
- 生成物的版权归属：你用本方法产出的技能包归你，本仓库不对其主张任何权利。

## 许可

[MIT](LICENSE)
