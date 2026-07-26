# Python 进阶 Day 4：项目结构 + 真实代码精读

> 日期：2026-07-26
> 项目：暑假科研基础夯实 — Python 线
> 仓库：[python-learning-notes](https://github.com/WangYi1-1/python-learning-notes)
> 练习文件：`learn_python_day4.py`

---

## 一、`if __name__ == "__main__"` — 程序入口

### 问题

Python 没有 Java 的 `public static void main`。Python 的 `import` 会**完整执行一遍那个文件**：

```python
# mymath.py
print("正在被加载...")          # import 时就会执行！
def add(a, b): return a + b
print(add(1, 2))               # import 时也会执行！
```

别人 `import mymath` 想用 `add`，结果你的测试代码也跑了一遍。

### 解决

Python 给每个 `.py` 文件一个内置变量 `__name__`：

| 怎么执行 | `__name__` 的值 |
|----------|----------------|
| `python mymath.py` | `"__main__"` |
| `import mymath` | `"mymath"` （文件名） |

于是你可以自己判断：

```python
if __name__ == "__main__":
    # 我是被直接运行的 → 执行测试/demo/启动程序
    print(add(1, 2))
# 被 import 时这个 if 块不执行
```

### 真实代码：`mini.py` 最后两行

```python
if __name__ == "__main__":
    app()
```

- `python mini.py` → 启动 TUI
- `from minisweagent.run.mini import app` → 只拿 app 对象，不启动

### Java vs Python

| | Java | Python |
|---|---|---|
| 入口 | `main()` 是语法，编译器认 | `__name__ == "__main__"` 是约定，程序员自己写 |
| `import` | 只注册名字，不执行代码 | **真的跑一遍那个文件** |

---

## 二、`__init__.py` — 把目录变成包

### 两个作用

1. **标记**：告诉 Python "这个目录是一个包，可以 import"
2. **自动执行**：`import 包名` 时，`__init__.py` 自动跑一遍

### 包的层级结构

```
src/
  minisweagent/              ← 包（有 __init__.py）
    __init__.py              ← 入口：协议定义 + 全局配置
    agents/
      __init__.py            ← 工厂函数：get_agent()
      default.py             ← DefaultAgent 类
    run/
      __init__.py
      mini.py                ← CLI 入口
```

### 导入时发生了什么

```python
from minisweagent.agents.default import DefaultAgent
```

Python 依次执行：
1. `minisweagent/__init__.py` → 定义 Model/Environment/Agent 协议、加载配置
2. `minisweagent/agents/__init__.py` → 定义 `get_agent()` 工厂函数
3. `minisweagent/agents/default.py` → 定义 `DefaultAgent` 类
4. 把 `DefaultAgent` 给你

### `__init__.py` 作为 API 门面

```python
# agents/__init__.py
def get_agent(model, env, config):
    agent_class = 根据配置选类
    return agent_class(model, env, **config)
```

调用者只需要：

```python
from minisweagent.agents import get_agent
agent = get_agent(model, env, {"agent_class": "default"})
```

不用知道 `DefaultAgent` 在哪个文件里，不用手动 import 具体类。

### 实战：创建 mypkg 包

```
mypkg/
  __init__.py   ← from mypkg.math_ops import add, multiply
  math_ops.py   ← add, subtract, multiply, divide
  greet.py      ← greet, farewell
```

```python
import mypkg
mypkg.add(3, 4)         # 7
mypkg.greet("World")    # Hello, World!
```

---

## 三、`pyproject.toml` — 项目的"身份证"

### 三个核心区块

```toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
# → "用 setuptools 来构建这个项目"

[project]
name = "mini-swe-agent"
requires-python = ">=3.10"
dependencies = ["pyyaml", "jinja2", "pydantic>=2.0", ...]
# → 项目名 + 版本 + 依赖清单

[project.scripts]
mini = "minisweagent.run.mini:app"
# → 命令行 mini → 执行 minisweagent/run/mini.py 里的 app 对象
# → 格式：命令名 = "模块路径:对象名"
```

### 这就是 `pip install -e .` 之后 `mini` 命令可用的原因

```
你敲 mini → pyproject.toml 查到 "minisweagent.run.mini:app" → 调 app()
```

---

## 四、精读 `default.py`（~190 行，逐段解剖）

### 全景图

```
AgentConfig(BaseModel)       ← Pydantic 版 @dataclass

DefaultAgent:
  __init__(model, env)       ← 依赖注入
  run(task)                  ← 主循环 while True
  step()                     ← 一步 = query + execute
  query()                    ← 调模型拿回复
  execute_actions(msg)       ← subprocess 执行命令
  serialize() / save(path)   ← 序列化 + 存盘

流程图：
  run()
  ├── 拼 system + user 消息
  └── while True:
       ├── step()
       │    ├── query()         → 调 DeepSeek API
       │    └── execute_actions() → subprocess.run
       └── if role == "exit": break
```

### 第 1 段：AgentConfig（1-36 行）— Day 3 的 @dataclass

```python
class AgentConfig(BaseModel):         # Pydantic = @dataclass 升级版
    system_template: str              # 类型注解（Day 1）
    instance_template: str
    step_limit: int = 0
    cost_limit: float = 3.0
    output_path: Path | None = None   # pathlib（Day 2）
```

### 第 2 段：`__init__` 依赖注入（38-50 行）

```python
class DefaultAgent:
    def __init__(self, model, env, *, config_class=AgentConfig, **kwargs):
        self.model = model    # 从外部传入，不在内部 new
        self.env = env
        self.config = config_class(**kwargs)  # dict → 有类型的对象
```

**依赖注入**：Agent 不 new 具体 Model，谁用谁传。换模型不用改 Agent 代码。

### 第 3 段：`run()` 主循环（88-122 行）

```python
def run(self, task: str = "", **kwargs) -> dict:
    # 拼初始消息
    self.add_messages(
        format_message(role="system", content=system_prompt),
        format_message(role="user", content=task),
    )
    # 核心循环
    while True:
        try:
            self.step()                   # 一步！
        except FormatError: ...           # 格式错误 → 恢复
        except InterruptAgentFlow: ...    # agent 主动退出
        except Exception: raise           # 兜底
        finally:
            self.save(...)                # 每步都存盘！
        if 最后一条消息 role == "exit":
            break
```

关键设计：
- `try/except` 分层处理不同异常
- `finally` 存盘 = Day 2 Context Manager 精神（每步都存，不丢数据）
- 退出条件是模型自己返回 `"exit"`，不是计数器

### 第 4 段：`step / query / execute_actions`（124-155 行）— Agent 的心跳

```python
def step(self) -> list[dict]:
    return self.execute_actions(self.query())   # 一整行！
    # AGENTS.md 第 11 条：不初始化变量只为了传参，直接传表达式

def query(self) -> dict:
    # 检查限制 → 调模型 → 追加到历史 → 返回
    message = self.model.query(self.messages)
    self.cost += message["extra"]["cost"]
    self.add_messages(message)
    return message

def execute_actions(self, message: dict) -> list[dict]:
    # Day 1 list comprehension！
    outputs = [self.env.execute(a)
               for a in message["extra"]["actions"]]
    return self.add_messages(*观察消息)
```

Agent 的"心跳"：

```
query() → 模型说"跑 bash xxx"
→ execute_actions() → 跑命令，结果追加到历史
→ 下一轮 query() 把完整历史发回去
→ 循环，直到模型说 exit
```

### 第 5 段：`serialize / save`（157-188 行）

```python
def save(self, path: Path | None, ...) -> dict:
    data = self.serialize(...)   # {info: {cost, calls, ...}, messages: [...]}
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)   # Day 2 pathlib
        path.write_text(json.dumps(data, indent=2))      # Day 2 一行写文件
```

---

## 五、用 Day 1-3 的视角重读 default.py

| Day | 概念 | default.py 里的对应 |
|-----|------|-------------------|
| Day 1 | List Comprehension | `[self.env.execute(a) for a in actions]` |
| Day 1 | `**kwargs` | `__init__(**kwargs)`, `run(**kwargs)` |
| Day 1 | Decorator 思想 | `try/except` 包裹 `step()` = 环绕逻辑 |
| Day 2 | pathlib | `output_path: Path`, `path.parent.mkdir()` |
| Day 2 | f-string | 整个项目的日志和消息拼接 |
| Day 2 | with 精神 | `finally: self.save()` = Context Manager 手动版 |
| Day 3 | @dataclass | `AgentConfig(BaseModel)` = Pydantic 版 dataclass |
| Day 3 | 依赖注入 | `__init__` 不 new，从参数传进来 |
| Day 4 | `if __name__` | `mini.py` 的 `app()` 入口 |
| Day 4 | `__init__.py` | `agents/__init__.py` 的 `get_agent()` |
| Day 4 | pyproject.toml | `mini` 命令 → `minisweagent.run.mini:app` |

---

## 六、参数传递全链路追踪

从 `mini.py` 到 `AgentConfig` 对象的完整路径：

```
mini.py 的 config 字典:
  {"agent_class":"default", "step_limit":10, "cost_limit":1.0, ...}

get_agent():
  config.pop("agent_class") → 选出 DefaultAgent 类
  剩下 {"step_limit":10, "cost_limit":1.0, ...}

DefaultAgent.__init__(model, env, step_limit=10, cost_limit=1.0):
  **kwargs = {"step_limit": 10, "cost_limit": 1.0}
  self.config = AgentConfig(**kwargs)
  → AgentConfig 对象：.step_limit=10, .cost_limit=1.0

dict（无类型）→ AgentConfig 对象（有类型有校验有默认值）
```

---

## 七、变量翻译速查

| 变量 | 翻译 | 实际存的什么 |
|------|------|------------|
| `run` | 跑、运行 | 启动 agent |
| `task` | 任务 | 用户输入的自然语言任务 |
| `messages` | 消息 | 完整对话历史 |
| `role` | 角色 | `"system"` / `"user"` / `"assistant"` |
| `content` | 内容 | 消息正文 |
| `query` | 查询 | 把历史发给 API，拿模型回复 |
| `extra_template_vars` | 额外的模板变量 | 塞进模板的键值对 |
| `_render_template` | 渲染模板 | 把 `{{变量}}` 替换成实际值 |

---

## 八、综合练习：MiniMiniAgent

仿写了一个 30 行的最简 Agent，跑通了核心循环：

```python
@dataclass
class MiniMiniConfig:
    system_prompt: str = "You are a helpful assistant."
    max_steps: int = 5
    verbose: bool = False

class MiniMiniAgent:
    def __init__(self, config=None):
        self.config = config or MiniMiniConfig()
        self.messages = []
        self.step_count = 0

    def run(self, task: str) -> str:
        self.messages += [f"[SYSTEM] {self.config.system_prompt}",
                          f"[USER] {task}"]
        while self.step_count < self.config.max_steps:
            self.step()
            if "[EXIT]" in self.messages[-1]:
                break
        return f"完成，共 {self.step_count} 步"

    def step(self):
        self.step_count += 1
        self.messages.append(self._fake_query())

    def _fake_query(self) -> str:
        return "[EXIT] 完成！" if self.step_count >= self.config.max_steps \
               else f"[ASSISTANT] 第 {self.step_count} 步..."
```

---

## 今日总结

| 概念 | 一句话 | 覆盖情况 |
|------|--------|---------|
| `if __name__ == "__main__"` | 手动造 Python 的程序入口 | 看懂 mini.py 的 app() 入口 |
| `__init__.py` | 标记包 + auto-执行 + API 门面 | 创建了 mypkg 包 |
| `pyproject.toml` | `mini` 命令 → 一行 import | 对照真实文件解读 |
| 精读 default.py | 5 段逐行讲解，标注 Day 1-3 概念 | 能认出 80% 的设计模式 |
| 依赖注入 | 不 new，从参数传 | 追了 config 字典 → AgentConfig 对象全链路 |
| MiniMiniAgent | 30 行复现核心循环 | 跑通 |

### 顺手修复的 bug

- Day 1：`filter_and_upper_new` 嵌套列表 bug → 修复
- Day 2：`count_lines_new` 的 `return` 在 for 循环内 → 缩进修正
