# Generic PPT Generation Skills

## 中文说明

通用的 PPT 生成 skills 仓库。

这个仓库的实际技能内容位于 `skills/` 目录下，适合接入 OpenClaw，也适合其他支持本地 skills 目录的工作流使用。

### 这个 skill 能做什么

`ppt-deck-builder` 适合处理这类任务：

- 把笔记、PDF、表格、旧 PPT 整理成演示逻辑
- 生成每一页的 page brief 和固定文字出图提示词
- 调用可替换的图片生成后端批量出图
- 单页返修，而不是整套重跑
- 将最终页面图片打包成 `.pptx`

它更适合“成品交付型 PPT”流程，也就是每页先生成成品图，再统一打包进 PowerPoint。

### 仓库结构

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
git clone https://github.com/lk251066/ppt-deck-builder-openclaw-skill.git
mkdir -p <your-workspace>/skills
cp -R ppt-deck-builder-openclaw-skill/skills/ppt-deck-builder <your-workspace>/skills/
```

方式二：复制到本地共享 `skills/` 目录

```bash
git clone https://github.com/lk251066/ppt-deck-builder-openclaw-skill.git
mkdir -p ~/.openclaw/skills
cp -R ppt-deck-builder-openclaw-skill/skills/ppt-deck-builder ~/.openclaw/skills/
```

### 运行依赖

进入 `skills/ppt-deck-builder/` 后，这套流程默认需要：

- `bash`
- `python3`
- `requests`
- `python-pptx`

安装 Python 依赖：

```bash
python3 -m pip install requests python-pptx
```

### 图片生成后端

这套流程不是绑定单一图片平台，而是支持可替换后端。

内置两种 provider：

- `runninghub_g31`：默认可直接使用的 RunningHub 文生图后端
- `command`：通用适配模式，适合接入自定义图片服务

开始执行前，建议先确认用户是否已经有 RunningHub 的 API Key。
如果用户没有特别指定 provider，也要先说明默认模型是 RunningHub 3.1 flash，对应本仓库里的模型 ID `rhart-image-n-g31-flash`。

provider 选择顺序：

1. 页级 `image_provider`
2. CLI `--provider`
3. 计划文件级 `image_provider`
4. 环境变量 `PPT_IMAGE_PROVIDER`
5. 默认 `runninghub_g31`

### 快速开始

进入 skill 目录：

```bash
cd skills/ppt-deck-builder
```

检查环境：

```bash
bash scripts/check_env.sh
```

开始执行前先确认两件事：

1. 用户是否已经有 `RUNNINGHUB_API_KEY`
2. 如果没有特别指定 provider，默认会使用 RunningHub 3.1 flash，也就是 `rhart-image-n-g31-flash`

RunningHub 示例：

```bash
export PPT_IMAGE_PROVIDER="runninghub_g31"
export RUNNINGHUB_API_KEY="your_api_key"
bash scripts/run_image_batch.sh plan.json output_dir
```

自定义 provider 示例：

```bash
export PPT_IMAGE_PROVIDER="command"
export PPT_IMAGE_PROVIDER_COMMAND="python3 scripts/provider_command_template.py"
bash scripts/run_image_batch.sh plan.json output_dir
```

### 标准流程

1. 明确 audience、目标和页序
2. 为每页编写 page brief
3. 将 brief 整理为 slide plan JSON
4. 先做小样测试
5. 再跑全量出图
6. 对问题页单独返修
7. 做整套 QA
8. 打包为 `.pptx`

### 关键文件

- `skills/ppt-deck-builder/SKILL.md`：主技能说明
- `skills/ppt-deck-builder/assets/page_brief_template.md`：页级 brief 模板
- `skills/ppt-deck-builder/assets/slide_plan_template.json`：出图计划模板
- `skills/ppt-deck-builder/references/provider-adapters.md`：自定义 provider 协议说明
- `skills/ppt-deck-builder/scripts/generate_from_plan.py`：主出图脚本
- `skills/ppt-deck-builder/scripts/build_pptx_from_images.py`：图片打包为 PPTX

### 说明

- 这套 skill 适合通用 PPT 生成，不绑定某个客户项目。
- 这套 skill 更适合成品图交付型 PPT，不是高度可编辑的母版型 PPT。
- 如果要切换图片生成平台，推荐从 `command` provider 扩展，而不是重写主流程。

## English

A generic PPT generation skills repository.

The actual skill source lives under `skills/`. It is suitable for OpenClaw and also works for other workflows that load local skill directories.

### What This Skill Does

`ppt-deck-builder` helps with:

- turning notes, PDFs, spreadsheets, or old decks into a presentation storyline
- writing page briefs and fixed-text slide prompts
- generating slide images through a replaceable image provider
- rerunning only weak pages instead of rerunning the whole deck
- packaging final slide images into a `.pptx`

It is optimized for finished-image delivery decks, where each slide is generated as a complete visual page and then packed into PowerPoint.

### Repository Layout

```text
skills/
  ppt-deck-builder/
    SKILL.md
    agents/
    assets/
    references/
    scripts/
```

### Installation

Option 1: copy into a workspace-level `skills/` directory.

```bash
git clone https://github.com/lk251066/ppt-deck-builder-openclaw-skill.git
mkdir -p <your-workspace>/skills
cp -R ppt-deck-builder-openclaw-skill/skills/ppt-deck-builder <your-workspace>/skills/
```

Option 2: copy into a shared local `skills/` directory.

```bash
git clone https://github.com/lk251066/ppt-deck-builder-openclaw-skill.git
mkdir -p ~/.openclaw/skills
cp -R ppt-deck-builder-openclaw-skill/skills/ppt-deck-builder ~/.openclaw/skills/
```

### Requirements

From `skills/ppt-deck-builder/`, the workflow expects:

- `bash`
- `python3`
- `requests`
- `python-pptx`

Install Python dependencies if needed:

```bash
python3 -m pip install requests python-pptx
```

### Image Providers

This workflow supports replaceable image backends instead of forcing a single provider.

Built-in providers:

- `runninghub_g31`: ready-to-run RunningHub text-to-image backend
- `command`: generic adapter mode for custom image services

Before execution starts, confirm whether the user already has a RunningHub API key.
If the user does not specify a provider, explain that the default model is RunningHub 3.1 flash, which maps to `rhart-image-n-g31-flash` in this repository.

Provider selection order:

1. slide-level `image_provider`
2. CLI `--provider`
3. plan-level `image_provider`
4. environment variable `PPT_IMAGE_PROVIDER`
5. default `runninghub_g31`

### Quick Start

Enter the skill directory:

```bash
cd skills/ppt-deck-builder
```

Run environment checks:

```bash
bash scripts/check_env.sh
```

Before execution starts, confirm two things:

1. whether the user already has `RUNNINGHUB_API_KEY`
2. if no provider is specified, the default model is RunningHub 3.1 flash, which maps to `rhart-image-n-g31-flash`

RunningHub example:

```bash
export PPT_IMAGE_PROVIDER="runninghub_g31"
export RUNNINGHUB_API_KEY="your_api_key"
bash scripts/run_image_batch.sh plan.json output_dir
```

Custom provider example:

```bash
export PPT_IMAGE_PROVIDER="command"
export PPT_IMAGE_PROVIDER_COMMAND="python3 scripts/provider_command_template.py"
bash scripts/run_image_batch.sh plan.json output_dir
```

### Typical Workflow

1. define audience, goal, and page sequence
2. write one page brief per slide
3. convert briefs into a slide plan JSON
4. generate a small sample first
5. run the full batch
6. rerun only weak pages
7. QA the full image set
8. package the images into a `.pptx`

### Key Files

- `skills/ppt-deck-builder/SKILL.md`: main skill instructions
- `skills/ppt-deck-builder/assets/page_brief_template.md`: page brief template
- `skills/ppt-deck-builder/assets/slide_plan_template.json`: slide plan template
- `skills/ppt-deck-builder/references/provider-adapters.md`: custom provider contract
- `skills/ppt-deck-builder/scripts/generate_from_plan.py`: main image generation entrypoint
- `skills/ppt-deck-builder/scripts/build_pptx_from_images.py`: package slide images into PowerPoint

### Notes

- This skill is meant to be a generic PPT generation skill, not a customer-specific workflow.
- It is better suited for finished-image delivery decks than heavily editable theme-driven decks.
- If you want to switch image platforms, extend the `command` provider instead of rewriting the main workflow.
