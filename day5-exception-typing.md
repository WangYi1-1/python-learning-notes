# Python 进阶 Day 5：Exception + typing + 重读 default.py 检验成果

> 日期：2026-07-27
> 项目：暑假科研基础夯实 — Python 线
> 仓库：[python-learning-notes](https://github.com/WangYi1-1/python-learning-notes)
> 练习文件：`learn_python_day5.py`

---

## 一、Exception 异常处理

### 1.1 try / except / else / finally

```python
try:
    result = a / b
except ZeroDivisionError:
    print("除数为 0")
except Exception as e:
    print(f"未知错误: {e}")
else:
    print("没出错才执行")     # 很少用但优雅
finally:
    print("无论如何都执行")    # 清理资源专用
```

关键原则：**except 从具体到笼统**。`ValueError` 是 `Exception` 子类，`except Exception` 放前面会吞掉 `ValueError`。

### 1.2 default.py 的三层异常处理（核心设计）

```python
while True:
    try:
        self.step()
    except FormatError:          # 第1层：格式错误 → 可恢复，让模型自我纠正
        ...
    except InterruptAgentFlow:   # 第2层：主动中断 → 正常退出（不是 bug）
        ...
    except Exception:            # 第3层：兜底 → 记录 + re-raise
        ... raise
    finally:
        self.save(...)           # 无论如何存盘（= Context Manager 精神）
```

设计精髓：**异常不仅是"错误处理"，更是"控制流"**。

### 1.3 异常继承体系

```
BaseException          ← 所有异常的根
+-- SystemExit         ← sys.exit()
+-- KeyboardInterrupt  ← Ctrl+C
+-- Exception          ← 正常异常的基类（自己定义异常继承它！）
    +-- ValueError, TypeError, KeyError...
    +-- 你的自定义异常
```

永远继承 `Exception`，不要继承 `BaseException`（否则 `Ctrl+C` 都可能被误抓）。

### 1.4 自定义异常 = 控制流工具

```python
class AgentException(Exception):
    def __init__(self, *messages: dict):
        self.messages = messages
        super().__init__(*messages)

class FormatError(AgentException):     # 格式错 → 可恢复
    ...

class TaskSubmitted(AgentException):   # 正常完成 → 优雅退出
    ...

class LimitsExceeded(AgentException):  # 限制达到 → 硬退出
    ...
```

## 二、typing 类型系统

### 2.1 Protocol — Duck Typing 的静态类型版

```python
class Model(Protocol):
    def query(self, messages: list[dict]) -> dict: ...
    def format_message(self, **kwargs) -> dict: ...
```

任何"碰巧"有 `query()` 和 `format_message()` 的类，自动算作 `Model`——不需要显式继承。这就是为什么 `DefaultAgent.__init__` 能接受 `LitellmModel`、`AnthropicModel` 甚至你自己的 `FakeModel`。

### 2.2 Union 类型（`X | Y`）

`Path | None` = 要么是 Path，要么是 None。Python 3.10+ 语法，等价于旧版的 `Union[Path, None]` 或 `Optional[Path]`。

### 2.3 Literal — 限定值的范围

```python
role: Literal["system", "user", "assistant", "exit"]
# → 只能是这四个字符串，不是任意 str
```

### 2.4 TypedDict — 给 dict 定义结构

```python
class ModelStats(TypedDict):
    instance_cost: float
    api_calls: int

class AgentData(TypedDict, total=False):  # total=False → 字段可选
    info: dict
    messages: list[dict]
```

`TypedDict` 在运行时不存在，对象就是普通 `dict`。只在类型检查时起作用。

### 2.5 泛型：Generic + TypeVar

`TypeVar("T")` = 声明一个类型占位符，"具体是什么到时候再说"。`Generic[T]` = 使用这个占位符。

```python
T = TypeVar("T")

class Result(Generic[T]):
    value: T | None = None

r1: Result[int] = Result(value=42)     # T → int
r2: Result[str] = Result(value="hi")   # T → str
```

### 2.6 Callable — 标注"参数是函数"

`Callable[[int], int]` = "接受一个 int、返回一个 int 的函数"。

### 2.7 cast — 骗过类型检查器

`cast(int, raw)` = "把这个值**当作** int 类型看"。运行时啥也不干，只在 mypy/pyright 检查时起作用。

## 三、default.py 逐行认领（Day 1-5 概念对应）

| 行号 | 代码片段 | 用到了什么 |
|------|---------|-----------|
| 3-9 | `import json, logging` / `from pathlib import Path` | Day 2: pathlib |
| 11 | `from jinja2 import ...` | Day 4: pyproject.toml 声明依赖 |
| 12 | `from pydantic import BaseModel` | Day 3: BaseModel = Pydantic 版 @dataclass |
| 15 | `from minisweagent.exceptions import ...` | Day 5: 自定义异常体系 |
| 19-35 | `class AgentConfig(BaseModel):` | Day 3: dataclass / Day 2: pathlib / Day 5: Union 类型 |
| 38-50 | `__init__(self, model: Model, **kwargs):` | Day 5: Protocol / Day 1: **kwargs / Day 3: 依赖注入 |
| 52-64 | `get_template_vars()` | Day 1: **kwargs |
| 66-67 | `_render_template()` | Jinja2: `{{变量}}` → 真实值 |
| 69-72 | `add_messages(*messages)` | Day 1: *args 展开 |
| 74-86 | `handle_uncaught_exception(e: Exception)` | Day 5: 异常处理 + 类型标注 |
| 88-122 | `run()` — while True + try/except/finally | Day 5: 异常分三层 / Day 2: finally 存盘 |
| 124-126 | `step() = execute_actions(query())` | Day 1: 一行风格（表达式直接传） |
| 128-150 | `query()` — raise LimitsExceeded | Day 5: 异常做控制流 |
| 152-155 | `execute_actions()` — `[... for action in ...]` | Day 1: List Comprehension / Day 1: *args 展开 |
| 157-178 | `serialize()` — f-string | Day 2: f-string |
| 180-188 | `save(path: Path | None)` | Day 2: pathlib / Day 5: Union 类型 |

## 四、今日澄清的细节

| 问题 | 答案 |
|------|------|
| `class AgentException(Exception)` 怎么继承的？ | 括号里写父类名 = 继承，`super().__init__()` 调用父类构造 |
| `*messages: dict` 的 `*` 是啥？ | 打包所有位置参数成一个元组，调用时 `*` 拆包 |
| `Path \| None` 是什么语法？ | Python 3.10+ Union 类型，"要么 Path 要么 None" |
| `TypedDict` 括号里的 `total=False`？ | 所有字段变成可选，缺哪个都行 |
| 泛型和 TypeVar 是啥？ | `TypeVar` 声明占位符，`Generic` 使用占位符，= 给容器贴标签 |
| `cast(int, raw)` 干什么？ | 骗类型检查器的，运行时啥也不干 |

## 五、10 道自测题

1. **Day 1**: `execute_actions` 里用什么语法一行执行多个 action？ → **List Comprehension**
2. **Day 1**: `add_messages(*messages)` 的 `*` 是什么？ → **参数展开/拆包**
3. **Day 2**: `save()` 用 pathlib 做了什么？ → **mkdir + write_text 一行写文件**
4. **Day 3**: `AgentConfig(BaseModel)` 和 `@dataclass` 什么关系？ → **Pydantic 增强版 dataclass**
5. **Day 3**: `__init__` 为什么不内部 new Model？ → **依赖注入，方便测试和替换**
6. **Day 4**: `from agents import get_agent` 为什么能 work？ → **`__init__.py` 作为 API 门面**
7. **Day 4**: `if __name__ == "__main__": app()` 作用？ → **直接运行启动 TUI，import 不启动**
8. **Day 5**: `run()` 三层 except 什么意思？ → **FormatError 可恢复 / InterruptAgentFlow 正常退出 / Exception 记录+raise**
9. **Day 5**: `finally: self.save()` 为什么重要？ → **每步存盘，崩了也不丢数据**
10. **Day 5**: `model: Model` 的 Model 为什么可以是 Protocol？ → **结构化子类型，有方法就算，不需要继承**

## 六、后续

Python 进阶五天全部完成。default.py 阅读能力：~30% → ~85%+。

接下来待推进：C++、GitHub、Transformer。
