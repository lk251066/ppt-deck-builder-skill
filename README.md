# PPT Deck Builder Skill

## 中文说明

这是一个可复用的 `ppt-deck-builder` skill 仓库，用来完成“资料整理 -> 页面规划 -> 批量出图 -> 单页返修 -> 打包 PPTX”的整套流程。

仓库实际内容位于 `skills/ppt-deck-builder/`，可以复制到项目级 `skills/` 目录，也可以复制到本机共享 skill 目录中使用。

### 适合做什么

- 把笔记、PDF、Excel、旧 PPT 整理成演示稿结构
- 为每一页生成 page brief 和固定可见文字的出图计划
- 调用可切换图片后端批量生成整套页面
- 只返修问题页，而不是重跑整套
- 把最终图片页面打包为 `.pptx`

这套 skill 更适合“成品图交付型 PPT”，也就是每页直接生成接近成品的页面图，再统一打包进 PowerPoint。

### 默认图片通道

- 默认 provider：`grsai`
- 默认模型：`gpt-image-2`
- 备选 provider：`runninghub_g31`
- 通用扩展 provider：`command`

如果没有显式指定 provider，流程默认走 `grsai + gpt-image-2`。

在 `grsai + gpt-image-2` 下，这套 workflow 已经允许在参考样张稳定后适度放开原有的信息密度限制，例如：

- `title + 6-10 small modules + 1 conclusion strip`
- `title + 3-5 explanation panels with longer sentences`

前提仍然是：每个句子都要绑定到一个明确区域，不能变成漂浮的小碎标签。

### 目录结构

```text
skills/
  ppt-deck-builder/
    SKILL.md
    agents/
    assets/
    references/
    scripts/
```

### 安装方式

方式一：复制到项目级 `skills/` 目录

```bash
git clone https://github.com/lk251066/ppt-deck-builder-openclaw-skill.git ppt-deck-builder-skill
mkdir -p <your-workspace>/skills
cp -R ppt-deck-builder-skill/skills/ppt-deck-builder <your-workspace>/skills/
```

方式二：复制到本机共享 `Codex` skills 目录

```bash
git clone https://github.com/lk251066/ppt-deck-builder-openclaw-skill.git ppt-deck-builder-skill
mkdir -p ~/.codex/skills
cp -R ppt-deck-builder-skill/skills/ppt-deck-builder ~/.codex/skills/
```

说明：

- 远端仓库地址当前仍然是 `ppt-deck-builder-openclaw-skill`
- 本地克隆目录可以直接改成 `ppt-deck-builder-skill`
- skill 内部说明已经去掉了 `OpenClaw-safe` 这类表述，统一改成更中性的可移植写法

### 运行依赖

进入 `skills/ppt-deck-builder/` 后，需要：

- `bash`
- `python3`
- `requests`
- `python-pptx`

安装依赖：

```bash
python3 -m pip install requests python-pptx
```

### 环境变量

默认路径使用 GrsAI：

```bash
export PPT_IMAGE_PROVIDER="grsai"
export GRSAI_API_KEY="your_api_key"
```

如果需要切到 RunningHub：

```bash
export PPT_IMAGE_PROVIDER="runninghub_g31"
export RUNNINGHUB_API_KEY="your_api_key"
```

如果需要接自定义后端：

```bash
export PPT_IMAGE_PROVIDER="command"
export PPT_IMAGE_PROVIDER_COMMAND="python3 scripts/provider_command_template.py"
```

### 快速开始

```bash
cd skills/ppt-deck-builder
bash scripts/check_env.sh
```

建议的执行顺序：

1. 先确认 audience、目标和页序
2. 先锁定整套 `style_preset`
3. 逐页写 page brief 和可见文字
4. 先跑 reference pack
5. 审核通过后再跑 full batch
6. 用 contact sheet 复查整套
7. 只返修问题页
8. 最后打包为 `.pptx`

### 关键文件

- `skills/ppt-deck-builder/SKILL.md`
- `skills/ppt-deck-builder/assets/page_brief_template.md`
- `skills/ppt-deck-builder/assets/slide_plan_template.json`
- `skills/ppt-deck-builder/references/prompt-rules.md`
- `skills/ppt-deck-builder/references/provider-adapters.md`
- `skills/ppt-deck-builder/references/style-presets.md`
- `skills/ppt-deck-builder/scripts/generate_from_plan.py`
- `skills/ppt-deck-builder/scripts/build_pptx_from_images.py`

### 使用原则

- 不要把“计划写完”当成“PPT 已生成完成”
- 不要跳过 sample pack / reference pack
- 不要在没看完整套联系表之前就直接打包
- 如果是 `gpt-image-2` 密集页，先验证结构稳定，再放开文字量
- 如果用户要手绘讲解感但不要白板边框，优先用 `custom` 的无边框手绘风格，而不是硬套 `whiteboard_handdrawn`

## English

This repository contains a reusable `ppt-deck-builder` skill for image-first PPT production:

`source digestion -> slide planning -> batch image generation -> single-page repair -> PPTX packaging`

The actual skill lives under `skills/ppt-deck-builder/`.

### What It Is Good For

- turning notes, PDFs, spreadsheets, and old decks into a presentation structure
- building page briefs and fixed-text slide plans
- running batch generation through replaceable image providers
- repairing weak slides one by one instead of rerunning the whole deck
- packaging approved slide images into a `.pptx`

It is optimized for finished-image delivery decks rather than heavily editable theme-engineered decks.

### Default Image Path

- default provider: `grsai`
- default model: `gpt-image-2`
- alternate built-in provider: `runninghub_g31`
- escape-hatch provider: `command`

If no provider is specified, the workflow defaults to `grsai + gpt-image-2`.

With `grsai + gpt-image-2`, the workflow now allows denser slide experiments after a stable reference pack, including:

- `title + 6-10 small modules + 1 conclusion strip`
- `title + 3-5 explanation panels with longer sentences`

The rule still holds that every sentence must belong to one named region instead of floating as micro-label clutter.

### Install

Option 1: copy into a workspace-level `skills/` directory

```bash
git clone https://github.com/lk251066/ppt-deck-builder-openclaw-skill.git ppt-deck-builder-skill
mkdir -p <your-workspace>/skills
cp -R ppt-deck-builder-skill/skills/ppt-deck-builder <your-workspace>/skills/
```

Option 2: copy into a shared local Codex skills directory

```bash
git clone https://github.com/lk251066/ppt-deck-builder-openclaw-skill.git ppt-deck-builder-skill
mkdir -p ~/.codex/skills
cp -R ppt-deck-builder-skill/skills/ppt-deck-builder ~/.codex/skills/
```

Notes:

- the current remote repository URL still contains `openclaw`
- your local clone directory does not need to
- the skill docs now use neutral portable-path wording instead of `OpenClaw-safe` labels

### Requirements

- `bash`
- `python3`
- `requests`
- `python-pptx`

Install Python dependencies if needed:

```bash
python3 -m pip install requests python-pptx
```

### Environment

Default GrsAI path:

```bash
export PPT_IMAGE_PROVIDER="grsai"
export GRSAI_API_KEY="your_api_key"
```

RunningHub fallback:

```bash
export PPT_IMAGE_PROVIDER="runninghub_g31"
export RUNNINGHUB_API_KEY="your_api_key"
```

Custom adapter mode:

```bash
export PPT_IMAGE_PROVIDER="command"
export PPT_IMAGE_PROVIDER_COMMAND="python3 scripts/provider_command_template.py"
```

### Recommended Workflow

1. define audience, goal, and page sequence
2. lock one deck-level style preset
3. write page briefs and approved text
4. run a reference pack first
5. run the full batch after the sample is stable
6. review the whole deck through contact sheets
7. rerun only failed slides
8. package only after review approval

### Core Files

- `skills/ppt-deck-builder/SKILL.md`
- `skills/ppt-deck-builder/assets/page_brief_template.md`
- `skills/ppt-deck-builder/assets/slide_plan_template.json`
- `skills/ppt-deck-builder/references/prompt-rules.md`
- `skills/ppt-deck-builder/references/provider-adapters.md`
- `skills/ppt-deck-builder/references/style-presets.md`
- `skills/ppt-deck-builder/scripts/generate_from_plan.py`
- `skills/ppt-deck-builder/scripts/build_pptx_from_images.py`

### Guardrails

- do not treat plan writing as deck completion
- do not skip the sample / reference-pack step
- do not package before reviewing the whole image set
- if you use dense `gpt-image-2` pages, prove structure stability before pushing density
- if the user wants hand-drawn explanation without visible whiteboard borders, prefer a borderless `custom` brief over forcing `whiteboard_handdrawn`
