# Python 进阶 Day 6：拆解 PyCursor — 从项目意图到逐行代码

> 日期：2026-07-30
> 项目：暑假科研基础夯实 — Agent 线
> 仓库：[python-learning-notes](https://github.com/WangYi1-1/python-learning-notes)
> 关联仓库：[PyCursor-DeepSeek](https://github.com/WangYi1-1/PyCursor-DeepSeek)

---

## 一、今天做了什么

把 PyCursor（代码自修复 Agent）从 Ollama/Gemini 改造成 DeepSeek API 版本，然后**逐行理解全部 4 个核心文件**（~130 行代码）的设计意图。

## 二、项目总览：一个 LangGraph 流水线

```
用户输入 prompt
  → coder_node: prompt + 系统指令 → DeepSeek API → 返回代码
  → runner_node: 拿代码 → subprocess 执行 → 捕获 stderr
  → router: stderr 空？（是→结束 / 否→回 coder_node，把 stderr 贴进 prompt，最多 3 次）
```

## 三、逐文件知识点

### 3.1 executor.py — 安全执行 Python 代码

核心意图：**在隔离子进程里跑代码，10 秒不回来就杀掉。**

```python
result = subprocess.run(
    [sys.executable, file_path],   # 用当前 Python 解释器
    capture_output=True,           # 截获输出，不打印到终端
    text=True,                     # 返回字符串，不是 bytes
    timeout=10                     # 10 秒超时
)
```

新知识：

| 概念 | 说明 |
|------|------|
| `sys.executable` | 当前 Python 解释器的路径，不用硬编码 `python` |
| `f.flush()` + `os.fsync(f.fileno())` | 双保险确保数据真正写到磁盘（清 Python 缓冲区 + OS 缓冲区） |
| `capture_output=True` | stdout/stderr 被截获到 `result.stdout` / `result.stderr` |
| `exec()` vs `subprocess` | exec 在当前进程跑（危险），subprocess 在子进程跑（安全隔离） |
| **组合优于继承** | `executor.py` 和 `DeepSeekChat` 完全不认识 —— 各干各的，通过 state 松耦合 |

### 3.2 state_schema.py — 节点间的"交接单"

```python
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]   # 对话历史，追加不覆盖
    current_code: str                          # 最新生成的代码
    error_log: str                             # 空的=成功，有东西=报错
    iteration: int                             # 第几轮
```

新知识：

| 概念 | 说明 |
|------|------|
| `TypedDict` | 给字典规定 key 和类型，IDE 能自动补全 |
| `Annotated[类型, 合并函数]` | 给字段贴元数据 —— `add_messages` 告诉 LangGraph 消息如何追加 |
| `isinstance(obj, type)` | 检查变量类型 —— 用于实现"类型分发" |
| `hasattr(obj, "attr")` | 鸭子类型检查 —— "有没有这个属性"比"是不是某个类"更灵活 |

### 3.3 nodes.py — 两个工人 + 一个自己写的 LLM 壳

**DeepSeekChat 类** — 自己写的薄壳，用 stdlib 调 API：

```python
class DeepSeekChat:
    _ROLE_MAP = {"human": "user", "ai": "assistant", "system": "system"}

    def invoke(self, messages):
        # 统一格式 → HTTP POST → 返回 AIMessage
```

为什么自己写而不是用 LangChain 的 ChatOpenAI？
- 避免装 `langchain-openai`（几十个依赖）
- `urllib.request` 是 Python 自带的标准库，零额外依赖
- 只要实现 `.invoke(messages)` 接口，LangGraph 就能用

**coder_node** — 发 LLM 请求，从回复里抠代码：

```python
def coder_node(state):
    error = state.get("error_log", "")         # 拿上一轮的报错
    if error:
        sys_msg += f"\n[FIX THIS ERROR]:\n{error}"  # 喂给 LLM
    resp = llm.invoke([("system", sys_msg)] + messages)
    clean_code = re.search(r"```python\s*(.*?)\s*```", resp.content, re.DOTALL)
    return {"messages": [resp], "current_code": clean_code, "iteration": iteration + 1}
```

**runner_node** — 跑代码，返回报错：

```python
def runner_node(state):
    stdout, stderr = run_python_code(state["current_code"])
    return {"error_log": stderr if stderr else ""}
```

新知识：

| 概念 | 说明 |
|------|------|
| `json.dumps()` / `json.loads()` | Python ↔ JSON 互转（打包/拆箱） |
| `.encode()` | str → bytes，网络传输只能用字节 |
| `f"Bearer {key}"` | f-string 插值 |
| `urllib.request.Request(url, data, headers)` | 组装 HTTP POST 请求 |
| `with ... as` | 上下文管理器，自动关闭连接 |
| `try/except HTTPError as e` + `from e` | 捕获 HTTP 错误，保留因果链 |
| `dict.get(key, default)` | 安全取值，不存在给默认值 |
| 元组拆包 `a, b = ("x", "y")` | a→"x", b→"y" |
| `re.search(pattern, text, re.DOTALL)` | 正则搜索，DOTALL 让 `.` 匹配换行 |
| `_ROLE_MAP = {"human": "user", ...}` | 角色名翻译：LangChain 叫 `human`，API 要 `user` |
| `AIMessage(content=...)` | LangChain 消息对象（有 `.content` 和 `.type`），LangGraph 认识 |

### 3.4 app.py — 画流水线 + 网页界面

```python
workflow = StateGraph(AgentState)              # 建图纸
workflow.add_node("coder", coder_node)         # 注册工位
workflow.add_node("runner", runner_node)
workflow.add_edge(START, "coder")              # 固定路线
workflow.add_edge("coder", "runner")
workflow.add_conditional_edges("runner", router)  # 分流路口

def router(state):
    if not state.get("error_log") or state.get("iteration", 0) >= 3:
        return END
    return "coder"                              # 返回字符串，LangGraph 去调

app = workflow.compile()                        # 冻结

for event in app.stream(inputs):                # 跑一步，吐一次状态
    ...
```

新知识：

| 概念 | 说明 |
|------|------|
| `add_edge(A, B)` | 固定边：A 完了必须去 B |
| `add_conditional_edges(A, fn)` | 条件边：fn 返回去哪 |
| **控制反转** | 你把函数注册给框架，框架到时候调你 —— 不是你去调框架 |
| `:= ` 海象运算符 | 赋值 + 判断一行搞定 |
| `app.stream(inputs)` | 生成器：每完成一个节点 yield 一次状态 |

## 四、完整数据流（核心理解）

```
state = {messages, current_code, error_log, iteration}

用户输入 → coder_node:
  读: messages, error_log
  写: messages (AIMessage 追加), current_code, iteration+1

→ runner_node:
  读: current_code
  写: error_log (空=成功)

→ router:
  读: error_log, iteration
  决策: END 或 "coder"（回环）

第 N 轮 coder_node:
  读: messages (前 N-1 轮的对话历史), error_log (上一轮的报错)
  写: 同上
```

**三条关键数据线：**
- `current_code`: coder 写 → runner 读
- `error_log`: runner 写 → router + 下一轮 coder 读
- `messages`: coder 一直追加 → 下一轮 coder 读（对话记忆）

## 五、今日收获

1. 搞清楚了 **Agent 骨架的本质**：一个 while 循环，state 在节点间流转
2. 理解了 **LangGraph 是控制反转**：你注册函数，框架调你
3. 学会了 **用 stdlib 替代胖依赖**：`urllib` 替代 `langchain-openai`，零成本
4. 看懂了 **鸭子类型**在实践中的应用：只要类有 `.invoke()` 和 `.content`，就能插进 LangGraph
