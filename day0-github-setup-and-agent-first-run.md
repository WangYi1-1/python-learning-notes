# 科研入门 Day 0：GitHub 实战 + Python 环境搭建

> 日期：2026-07-22 ~ 07-23  
> 项目：mini-swe-agent 搭建全过程  
> 仓库：[mini-swe-agent (Fork)](https://github.com/WangYi1-1/mini-swe-agent)

---

## 一、GitHub 实战操作

### 1.1 Fork（复刻）

在 GitHub 网页上点 Fork 按钮，把 [SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 复制到自己账号下，变成 `WangYi1-1/mini-swe-agent`。

**Fork 的目的：** 别人的仓库你没有写权限，Fork 一份到自己的账号下，就可以随便改、随便 push。

### 1.2 Clone（克隆）

```bash
git clone https://github.com/WangYi1-1/mini-swe-agent.git
```

把 GitHub 上的代码下载到本地 `D:\claude-test\mini-swe-agent`。

### 1.3 配置双远程（最关键的一步）

```bash
# origin → 自己的 Fork（有写权限，可以 push）
git remote add origin https://github.com/WangYi1-1/mini-swe-agent.git

# upstream → 原始仓库（只能 pull，不能 push）
git remote add upstream https://github.com/SWE-agent/mini-swe-agent.git
```

**为什么配两个远程？**

```
upstream (SWE-agent/mini-swe-agent)     origin (WangYi1-1/mini-swe-agent)
    │                                        │
    │  ← pull 拉取最新代码                      │
    │                                        │
    └────────────────→ Fork ────────────────→ │
                                              │
                                        push →│  你自己的修改
```

- **origin** = 你自己的，随便改
- **upstream** = 官方的，只拉取更新，保持同步

查看远程配置：
```bash
git remote -v
# origin    https://github.com/WangYi1-1/mini-swe-agent.git (fetch)
# origin    https://github.com/WangYi1-1/mini-swe-agent.git (push)
# upstream  https://github.com/SWE-agent/mini-swe-agent.git (fetch)
# upstream  https://github.com/SWE-agent/mini-swe-agent.git (push)
```

---

## 二、Python 环境搭建（踩坑）

### 2.1 虚拟环境 venv

```bash
python -m venv .venv
```

在项目目录下创建 `.venv` 文件夹，装所有依赖。**为什么要用虚拟环境？** 不同项目依赖不同版本的库，venv 把它们隔离开，互不干扰。

### 2.2 pyproject.toml

现代 Python 项目的配置文件，相当于 Java 的 `pom.xml` 或 Node.js 的 `package.json`。定义了：
- 项目名、版本号
- 依赖哪些第三方库
- 用什么构建工具

### 2.3 pip install -e .（踩坑记录）

```bash
pip install -e .
```

`.` = 当前目录，`-e` = 开发模式（editable），改了源码不需要重新安装。

**遇到的坑：** litellm 1.93.0 需要 Rust 编译器编译，Python 3.13 + Windows 没有预编译包，装到一半报错。

**解决方案：**
```bash
# 先装旧版的预编译 wheel（跳过需要编译的新版）
pip install litellm --only-binary :all:

# 再装项目
pip install -e .
```

**学到的：**
- `--only-binary :all:` 只下载预编译好的包，跳过需要本地编译的
- Python 3.13 太新，有些库还没准备好 wheel → 以后知道降版本或等适配

### 2.4 配置 API Key

项目读取 `C:\Users\lenovo\AppData\Local\mini-swe-agent\mini-swe-agent\.env` 里的环境变量：
```
DEEPSEEK_API_KEY=xxx
```

`.env` 文件存放密钥，不提交到 git（`.gitignore` 会忽略它）。

---

## 三、首次运行 Demo

```bash
mini
```

启动 TUI 终端界面，输入任务：`Write a Python program that plays a number guessing game`

Agent 跑了 30 个 step，三个核心发现：

| 观察 | 具体表现 | 对应科研问题 |
|------|---------|-------------|
| 环境适配差 | 前 13 步全用 Linux 命令（cat/python3/heredoc），Windows 上全失败 | 环境感知 |
| 自我纠正有效 | 第 10 步发现 `python` 可用，逐渐切换到 Windows 兼容方式 | 错误恢复 |
| 不会适时停止 | Step 25 代码已正确，但纠结显示细节到 step 30 才手动停 | 终止策略 |

---

## 四、源码初读：Agent 核心循环

跟着真实运行轨迹，追了 `default.py` 的三个核心方法：

```
run() → while 循环，直到 messages[-1].get("role") == "exit"
  └─ step()
       └─ execute_actions(query())
            │              └─ 调 DeepSeek API，返回 tool_call
            └─ subprocess.run 执行命令，捕获输出
```

每个 step 的输出：
- `THOUGHT` + `bash <命令>` ← 来自 `query()` 调模型
- `<returncode>` + `<output>` ← 来自 `execute_actions()` 执行

**代码位置：** `src/minisweagent/agents/default.py` 第 88-155 行

---

## 本次收获总结

| 类别 | 学到的 | 对应操作 |
|------|--------|---------|
| GitHub | Fork → Clone → 双远程配置 | origin + upstream |
| Python | venv + pyproject.toml + pip install -e . | 项目环境搭建 |
| 踩坑 | `--only-binary :all:` 跳过编译 | litellm 安装失败 |
| 科研 | Agent 循环 = query → execute → 追加历史 → 循环 | 读了 default.py 源码 |
| 科研 | 三个研究方向：环境理解 / 错误恢复 / 终止策略 | 跑 demo 观察到的 |
