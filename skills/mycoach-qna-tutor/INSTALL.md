# 安装与使用

当前GitHub发布版为v1.1.2：[安装包与校验值](https://github.com/hebokenn/mycoach-qna-tutor/releases/tag/v1.1.2)、[完整使用示例与实测截图](https://github.com/hebokenn/mycoach-qna-tutor)。仓库与安装包已按资料所有者授权公开，下载无需额外申请仓库权限。

解压后保留整个`mycoach-qna-tutor`文件夹，SKILL.md、references、scripts和assets一起移动。仅粘贴SKILL.md会丢失题库、人设、原量尺和案例。

## Codex

把文件夹放到个人`~/.agents/skills/`，或某个项目的`.agents/skills/`。也可从仓库运行`python3 tools/install.py`；已有同名目录时默认拒绝覆盖，指定`--backup-existing`才会保留旧版备份后安装。其他电脑直接安装整个文件夹即可，不需要原电脑路径。

在新对话输入`$mycoach-qna-tutor`，或说“用私教答疑技能陪我备考”。Codex会发现本地技能，未出现时重新打开会话或重启应用。依据：[OpenAI官方技能说明](https://learn.chatgpt.com/docs/build-skills)。

## WorkBuddy

在“专家·技能·连接器”打开“技能”，选择“添加技能 → 上传技能”，上传本地ZIP包，并在已安装列表确认已启用。此处指WorkBuddy桌面本地技能导入，不是开放平台公开市场上架；公开平台有额外元数据与发布要求，本包未上架。

导入后在新对话说“使用私教答疑技能，我当Coach，你当顾客，随机开始”。本包依据其官方SKILL.md＋references/scripts结构制作；本次未在你的WorkBuddy界面实际导入验收。若宿主不能读相对附件路径，须保留整个文件夹并让它读取目录，不能只上传入口文本。依据：[WorkBuddy本地上传说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)、[官方技能结构](https://open.workbuddy.cn/docs/skill)。

## 可以直接这样说

- “考试主要考什么？我还有一周，每天能练30分钟，怎么准备？”
- “你扮顾客，我当Coach，抽一道题；先不要告诉我答案。”
- “练第1题电池质量。你当Coach，我当顾客，用一步一反馈的方式带我处理。”
- “这是我和同事的完整对练记录。A是Coach，B是顾客，请按原16项标准逐项评分，引用原话并给改进建议。”
- “这里只是排障片段，帮我评这一段；开场和收尾没有录到。”
- “开语音后你继续当这位顾客，结束时给我复盘。”

文字对练直接可用。实时口头对练、音频转写和视频观察取决于宿主能力；本包不附电话拨号/接听引擎。提交原记录不等于授权向第三方上传；不需要网站账号、付费API密钥或生产连接。

## 已验证和使用边界

结构、引用、题目/人设/案例覆盖与评分算术均可本地复核；评分判断仍由加载技能的AI基于证据完成。支持Python3时脚本仅依赖标准库，不支持时可直接阅读Markdown和JSON，按量尺计算。

本包保存的是2026-10-22快照，资料更新后需重打包。Apple菜单以实机与官方现行正文为准；缺少正式考务通知的事项会如实说明未知。包内案例为内部学习资料，未公开发布。
