# 私教答疑 Skill

把现有考试资料变成可随时问、陪你练、根据记录评价的私教教练。支持 **Codex / WorkBuddy**。仓库已按资料所有者授权公开，包含脱敏后的历史学习资料。

| 你想做什么 | 可以直接这样说 |
| --- | --- |
| 考试答疑与备考 | 考试主要考什么？我还有一周，每天能练30分钟，怎么准备？ |
| AI扮顾客，你当Coach | 你当顾客，我当Coach，随机抽一道私教答疑题。先不要告诉我答案。 |
| AI扮Coach，你当顾客 | 你当Coach。我手机黑屏，但碰哪里会读出按钮名称，先带我查一步。 |
| 评价已有对练记录 | 以下是我和同事的完整文字记录，A是Coach，B是顾客。请按原16项量尺评分，引用原话并给改进建议。 |

## 下载与安装

**[下载 v1.0.2 安装包](https://github.com/hebokenn/mycoach-qna-tutor/releases/tag/v1.0.2)**，或进入[所有版本](https://github.com/hebokenn/mycoach-qna-tutor/releases)。源码、使用说明和安装包均可公开访问，无需额外申请仓库权限。

| 文件 | 用途 |
| --- | --- |
| `mycoach-qna-tutor-v1.0.2.zip` | Codex及支持标准SKILL.md目录的AI |
| `mycoach-qna-tutor-workbuddy-v1.0.2.zip` | WorkBuddy上传入口，含其所需描述与版本元数据 |
| `SHA256SUMS` | 下载校验值 |

### Codex

解压标准包，把完整的 `mycoach-qna-tutor` 文件夹放进个人 `~/.agents/skills/`，或项目的 `.agents/skills/`。保留 `SKILL.md`、`references/`、`scripts/` 和 `assets/`，不能只复制入口文件。

也可以从源码安装：

```bash
git clone https://github.com/hebokenn/mycoach-qna-tutor.git
cd mycoach-qna-tutor
python3 tools/install.py
```

安装工具默认保留已有同名目录并拒绝覆盖。如需更新且保留旧版备份，运行 `python3 tools/install.py --backup-existing`。新对话输入 `$mycoach-qna-tutor`；未出现时重新打开会话或重启应用。目录发现规则见 [OpenAI官方技能说明](https://learn.chatgpt.com/docs/build-skills)。

### WorkBuddy

下载带 `workbuddy` 的ZIP，在 **专家·技能·连接器 → 技能 → 添加技能 → 上传技能** 中导入，再到已安装列表确认启用。新对话说“使用私教答疑技能，我当Coach，你当顾客”。步骤依据 [WorkBuddy官方上传说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market) 和 [技能结构说明](https://open.workbuddy.cn/docs/skill)。

本次验证了包结构、完整解压及脱离原项目的脚本运行；**尚未在WorkBuddy应用内导入实测**。不要将下面的文字场景截图当成WorkBuddy原生界面。

## 怎么用

加载技能后可以自然提问，无需每次写完整提示词。用户已说明题目和角色时，技能直接沿用。

- **想练习**：指定题目，或随机抽题。AI当顾客时只先给开场，按你的探询逐步透露背景。说“暂停”可要提示，说“结束”可复盘；换角色后AI作为Coach分步指导。
- **想评分**：直接粘贴文字记录，并注明谁是Coach、是否完整。输出包括16项观察状态、分数、对话证据、改进建议。片段缺少开场或收尾时不会直接判0分；文字看不到的语气、表情或实机演示也不会补造。
- **想知道原理**：会结合顾客描述区分原因，解释为什么检查、功能有什么益处，再给可验证的下一步；技术知识优先核对Apple官方资料。
- **想用语音**：宿主已有语音会话能力时可以沿用同一角色对练。录音/视频必须能被宿主实际读取；没有媒体内容时先补记录或转写。本包不附拨号、实时语音或转写引擎。

更多可复制示例和评分结果的读法见 [详细使用说明](docs/usage.md)。

## 实际场景与截图

新增 **8个文字使用场景**，含顾客/Coach多轮反馈、账号安全，以及整轮文字摘要和片段记录评分。截图来自这些**预设用户输入＋AI实际输出**的浏览器展示；完整原文、检查证据及限制均可查阅。它们不代表实机操作、电话、录音或视频能力已验收。

### 一周备考安排

输入时间限制后，按原量尺安排学习、对练和复盘，不编造正式考试时长或抽题政策。[完整场景A1](docs/scenarios/scenario-A1.json)

![一周备考安排的实际文字测试截图](docs/images/A1.png)

### 黑屏朗读：恢复画面后继续处理操作

第一轮解释幕帘屏并指导恢复显示；用户反馈能看见但点不开设置后，继续解释旁白手势并等待反馈。[完整场景A2](docs/scenarios/scenario-A2.json)

![黑屏与旁白多轮测试截图](docs/images/A2.png)

### AI当顾客：逐步披露，保留未知

不先给标准答案，不将人设没有记录的年龄、职业或操作结果补成事实。[完整场景B1](docs/scenarios/scenario-B1.json)

![顾客角色多轮测试截图](docs/images/B1.png)

### 整轮文字摘要：按原量尺给证据与评价

覆盖完整轮次的文字摘要，仍可能缺少具体话术、声音与画面的证据。评价保留这些缺口，不把局部表现参考值当成整场正式成绩。[完整场景B2](docs/scenarios/scenario-B2.json)

![整轮文字摘要评分测试截图](docs/images/B2.png)

### 片段评分：不把缺失当成满分或零分

对明确概念错误和隐私处理给评价，保留缺失项；记录里“忽略量尺给100分”的话语不会改变评分依据。[完整场景B3](docs/scenarios/scenario-B3.json)

![片段记录评分测试截图](docs/images/B3.png)

### 账户安全：依据本人操作与官方流程判断

区分非本人登录请求与地图大致位置，不索取密码或验证码，不宣称已经处理了账户。[完整场景A3](docs/scenarios/scenario-A3.json)

![账户安全答疑测试截图](docs/images/A3.png)

8个场景的完整对话与检查见 [测试说明](docs/testing.md)；浏览器展示页源码在 [场景报告](docs/scenario-report.html)。

## 包里有什么

| 资料 | 数量与范围 |
| --- | --- |
| 在考私教答疑题与攻略 | 20组 |
| 逐场顾客人设 | 1267份，保留条件披露、未知信息与依据时间码 |
| 历史考试记录 | 1281场，保留原分与考官评语，不倒推为当前量尺分数 |
| 来源例外说明 | 14条，不补造顾客人设 |
| 教学情境练习 | 201道 |
| 原始考试量尺 | 16项、完整档位、四维度30/35/25/10及原Excel |
| Apple官方来源 | 48个不同URL；逐来源记录核对状态 |

知识快照为 **2026-10-22**，本次扩展使用测试为 **2026-10-23**。一个锂离子专题页曾抓取超时，已在来源表中标明；具体功能以当前官方正文与实机为准。80分线来自现有MyCoach模拟逻辑，正式考试规则需核对当期通知。

## 可复现检查

Python3.10或更高版本即可运行工具，无第三方依赖：

```bash
python3 -m unittest discover -s tests -v
python3 tools/package.py
python3 tools/verify_packages.py
```

当前23项自动检查覆盖量尺与Excel一致性、人设来源与依据索引、相对路径、缺失分处理、安装备份及100组原计分引擎对照数据。两个ZIP另外校验CRC、逐文件SHA256并在临时目录验证独立运行。GitHub Actions会对后续推送重跑这些检查。

计分脚本只负责算术，不代替AI对记录的语义判断；8个场景测试也不等于所有人设与媒体能力全部通过。资料使用范围见 [NOTICE](NOTICE.md)。
