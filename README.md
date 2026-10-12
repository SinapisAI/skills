# SinapisAI Skills

SinapisAI 接入技能仓库。让支持 Agent Skills 的编程助手理解 SinapisAI 的接入方式，并根据你的项目完成服务端配置、调用代码与验证。

## 安装

在需要接入的项目目录运行首页提供的命令：

```bash
npx skills add SinapisAI/skills
```

第一版包含一个技能：`sinapisai-integration`。也可明确选择：

```bash
npx skills add SinapisAI/skills --skill sinapisai-integration
```

安装工具会让你选择目标助手与安装方式。可先用 `npx skills add SinapisAI/skills --list` 查看技能。更新使用 `npx skills update`。安装工具由 [Vercel Skills CLI](https://github.com/vercel-labs/skills) 提供，本仓库无需发布 npm 包。

## 使用

安装后，向你的编程助手提出需求，例如：

> 帮我把这个项目接入 SinapisAI，使用 Mio，保留现有调用结构并支持流式输出。

支持显式技能调用的助手也可使用 `$sinapisai-integration`。助手将检查现有项目、生成或修改接入代码，并执行相关检查。密钥由你在自己的服务端环境或密钥管理工具中配置，使用变量名 `SINAPISAI_API_KEY`；不要粘贴到聊天里。

统一 SDK Base URL 为 `https://api.sinapisai.com/v1`，Mio 模型 ID 为 `sinapisai/mio`。以当前密钥有权限访问的模型为准。当前文本接口参考已于 2026-10-12 核对生产公开 OpenAPI。

## 包含什么

- 一个 [SKILL.md](skills/sinapisai-integration/SKILL.md) 接入工作流。
- 文本 Chat Completions API、Node.js/Python 示例、SSE 与常见错误处理。
- 一个标准库 Python 模型检查脚本：只发送一次 `GET /v1/models`，不发送对话、不创建密钥、不修改账号配置。

安装技能不会创建 SinapisAI 账号或 API Key，也不会自动切换编程助手自身的模型。调用示例可能产生费用；真实生成由你授权后执行。第一版覆盖应用的服务端文本接入，其他模态和工具配置需核对当前官方能力。

平台与文档入口：https://sinapis.ai

## 维护与验证

```bash
python3 -m unittest discover -s tests -v
python3 tools/validate_skill.py
```

测试使用本地模拟数据，不读取你的密钥，也不发起真实生成。发布后还应在临时项目里执行安装、核对技能及参考文件，再验证目标助手识别技能；模型检查成功与真实生成成功分别记录。

更新公开接口说明时，核对当前官方文档与生产公开 OpenAPI，只收录公开接入契约。不要提交环境文件、密钥、内部接口、用户数据或完整内部 OpenAPI 快照。

本仓库内容采用 [MIT License](LICENSE)。
