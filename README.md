# silas-skills

由 **zhangyuqian (Silas)** 实战打磨的 [Hermes Agent](https://hermes-agent.nousresearch.com) 技能集。

## 技能

### 🪔 一盏神灯（yizhan-shendeng）

把一本书、一份长文档、课程讲稿、采访稿或会议记录**蒸馏成可被 AI 直接调用的技能包**。

产出的不是读书笔记、不是摘要——而是**让一个没读过这本书的人，在遇到具体问题时直接调用、并做成一件事的操作指令**。

工作方式：

- **五路并行提取**：框架 / 原则 / 案例 / 反例 / 术语 五条线分头提取，逐块回执、跨批对账
- **三重验证**：原文支撑 → 预测力 → 非常识（含「公开理论 vs 作者原创判据」的锋线区分与自动纠偏）
- **双层诱饵测试**：同源混淆 + 宿主混淆，防止新技能抢占既有技能触发
- **全自动执行**：闸门检查通过后一路跑到底；长任务可跨会话断点续跑
- 附全套 references（提取器、模板、大书分批实战手册、校验口径）与逐字校验脚本

## 安装（Hermes Agent）

从本仓库直装：

```
hermes skills install "https://raw.githubusercontent.com/qianyu6a/silas-skills/main/skills/yizhan-shendeng/SKILL.md"
```

或手动：把 `skills/<技能名>/` 目录复制进你的 Hermes 技能目录。

## 结构

```
skills/
  yizhan-shendeng/     # 一盏神灯：长文本 → 可调用技能包
    SKILL.md           # 主流程（9 步流水线）
    references/        # 提取器、模板、实战手册、校验口径
    scripts/           # 候选摘录逐字校验工具
```

## 许可

[MIT](LICENSE)
