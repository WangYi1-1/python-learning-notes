"""
Python 进阶 Day 5: Exception 异常处理 + typing 类型系统 + 重读 default.py 检验成果
======================================================================================
今天是 Python 进阶最后一天——把"异常处理"和"类型系统"补齐，
然后重新打开 default.py，检验你五天到底学了多少。

运行方式：python learn_python_day5.py
"""

import sys
import json
from pathlib import Path
from typing import (
    Protocol, Callable, Generic, TypeVar,
    Any, Union, Optional, Literal, TypedDict, cast,
)

# ============================================================
# 概念 1: try / except / else / finally — 异常处理完整版
# ============================================================
#
# 核心问题：代码运行中出错怎么办？
#   新手：让它崩（或者 if 判断每个可能出错的地方）
#   进阶：用 try/except 分层处理不同错误

print("=" * 60)
print("概念 1: try / except / else / finally")
print("=" * 60)

# --- 基础：try/except ---
print("\n--- 1.1 基础：捕获异常 ---")

def safe_divide(a: float, b: float) -> float | None:
    """安全除法——异常处理的"hello world"."""
    try:
        return a / b
    except ZeroDivisionError:
        print(f"  错误: 不能除以 0！({a}/0)")
        return None

print(f"  safe_divide(10, 2) = {safe_divide(10, 2)}")
print(f"  safe_divide(10, 0) = {safe_divide(10, 0)}")

# --- 进阶：异常链（多个 except）---
print("\n--- 1.2 分层捕获（从具体到笼统）---")

def parse_and_divide(s1: str, s2: str) -> float | None:
    """把两个字符串转成数字再除——可能出多种错。

    关键原则：except 顺序从具体到笼统！
    ValueError 是 Exception 的子类，如果把 except Exception 放前面，
    ValueError 就永远不会被触发。
    """
    try:
        n1 = float(s1)
        n2 = float(s2)
        result = n1 / n2
    except ValueError:
        # 具体错误：字符串不是数字
        print(f"  格式错误：'{s1}' 或 '{s2}' 不是数字")
        return None
    except ZeroDivisionError:
        # 具体错误：除数为 0
        print(f"  数学错误：除数为 0")
        return None
    except Exception as e:
        # 兜底：其他任何错误
        print(f"  未知错误: {type(e).__name__}: {e}")
        return None
    else:
        # else：只有 try 里没抛异常时才执行！
        print(f"  [OK] 计算成功！")
        return result
    finally:
        # finally：不管抛不抛异常，一定执行！
        print(f"  [finally] 清理工作（如关闭文件、释放锁）")

print("\n  测试 1: parse_and_divide('10', '2')")
parse_and_divide('10', '2')

print("\n  测试 2: parse_and_divide('abc', '2')")
parse_and_divide('abc', '2')

print("\n  测试 3: parse_and_divide('10', '0')")
parse_and_divide('10', '0')

print("""
  try/except/else/finally 一句话总结：
    try    — "试试看，可能出错"
    except — "出错了？我来处理"
    else   — "没出错才执行"（很少用，但很优雅）
    finally— "无论如何都要执行"（清理资源专用）
""")

# --- 实战：default.py 里的异常处理模式 ---
print("--- 1.3 实战分析：default.py run() 的异常处理（88-122行）---")
print("""
  这是 default.py 里最精彩的一段——异常分三层处理：

  while True:
      try:
          self.step()                              # 正常走一步
          self.n_consecutive_format_errors = 0     # 成功则重置错误计数
      except FormatError as e:                     # 第1层：格式错误
          self.n_consecutive_format_errors += 1     # 累加计数
          if 连续太多次:
              放弃，退出                            # -> "exit" role
          else:
              把错误消息加入历史，让模型自己修复       # -> 继续循环
      except InterruptAgentFlow as e:               # 第2层：主动中断
          self.add_messages(*e.messages)             # -> 加入退出消息
      except Exception as e:                        # 第3层：兜底
          self.handle_uncaught_exception(e)          # -> 格式化为退出消息
          raise                                      # -> 重新抛出，让调用者知道
      finally:
          self.save(...)                            # 无论如何都存盘！

  关键设计决策：
  1. FormatError 不直接退出——给模型机会自我纠正（容错）
  2. InterruptAgentFlow 是"正常退出"——不是 bug，是流程控制
  3. 真正的 Exception 记录后 re-raise——"我处理不了，让上层决定"
  4. finally 存盘——等价于 Context Manager，Day 2 的精神！

  对比 Java：
    Java:  checked exception（必须声明 throws），编译器强制处理
    Python: 所有异常都是 unchecked，约定优于强制
    -> Python 哲学："我们大家都是成年人了"（We're all consenting adults）
""")


# ============================================================
# 概念 2: Python 异常体系 — 从新手到"敢自己定义异常"
# ============================================================

print("\n\n" + "=" * 60)
print("概念 2: 异常继承体系 + 自定义异常")
print("=" * 60)

print("""
  Python 异常树（简化版）：
    BaseException           <- 所有异常的根
    +-- SystemExit          <- sys.exit() 抛出
    +-- KeyboardInterrupt   <- Ctrl+C
    +-- Exception           <- 所有"正常"异常的基类
        +-- ValueError      <- 值不对
        +-- TypeError       <- 类型不对
        +-- KeyError        <- dict 键不存在
        +-- FileNotFoundError
        +-- ZeroDivisionError
        +-- RuntimeError
        +-- ...你自己定义的异常

  关键：永远继承 Exception，不要继承 BaseException！
  因为 except Exception 是 Python 世界的"抓所有常规异常"，
  如果继承 BaseException，连 Ctrl+C 都可能被误抓。
""")

# --- 实战：仿写 mini-swe-agent 的异常体系 ---
print("--- 2.1 实战：仿写自定义异常 ---")

# 对照 mini-swe-agent/src/minisweagent/exceptions.py（完整 27 行）
# 我们来手写一个微缩版

class AgentException(Exception):
    """Agent 异常的基类——所有自定义异常都继承它。

    这样调用方可以用 except AgentException 抓所有 agent 异常，
    而不是一个个列举。
    """
    def __init__(self, *messages: dict):
        self.messages = messages
        super().__init__(*messages)


class FormatError(AgentException):
    """模型输出格式不对——不是 bug，是可恢复的。

    在 default.py 里，这个异常不会直接退出，
    而是把错误消息追加到对话历史，让模型看到并自我纠正。
    只有连续太多次才放弃。
    """


class TaskSubmitted(AgentException):
    """Agent 正常完成任务——"优雅退出"的信号。

    注意：这不是 Error！它是一种"控制流"。
    用异常做控制流是 Python 的常见模式（StopIteration 同理）。
    """


class LimitsExceeded(AgentException):
    """步数用完或钱花完了——硬限制触发。"""


# --- 练习：用这些异常写一个迷你循环 ---
print("\n--- 2.2 练习：用自定义异常控制流程 ---")

class MiniAgent:
    """用异常控制流程的迷你 Agent——演示 default.py 的设计模式。"""

    def __init__(self, max_steps: int = 5):
        self.max_steps = max_steps
        self.steps = 0
        self.history: list[str] = []

    def step(self):
        """一步——可能抛多种异常。"""
        self.steps += 1

        # 模拟：第 2 步输出格式错误
        if self.steps == 2:
            raise FormatError({"role": "tool", "content": "模型输出格式错误"})

        # 模拟：第 3 步达到限制
        if self.steps >= self.max_steps:
            raise LimitsExceeded({"role": "exit", "content": "LimitsExceeded"})

        # 正常步
        self.history.append(f"Step {self.steps}: OK")

    def run(self):
        """主循环——分层处理异常。"""
        consecutive_errors = 0

        while True:
            try:
                self.step()
                consecutive_errors = 0          # 成功则重置
                print(f"  [Step {self.steps}] OK 正常")
            except FormatError as e:
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    print(f"  [Step {self.steps}] X 连续 {consecutive_errors} 次格式错误，放弃")
                    break
                else:
                    print(f"  [Step {self.steps}] ! 格式错误 (第{consecutive_errors}次)，让模型纠正...")
            except LimitsExceeded as e:
                print(f"  [Step {self.steps}] STOP 限制达到，正常退出")
                break
            except AgentException as e:
                print(f"  [Step {self.steps}] X Agent 异常: {type(e).__name__}")
                break

        print(f"  运行结束，共 {self.steps} 步")

print()
agent = MiniAgent(max_steps=4)
agent.run()

print("""
  这个设计模式在大学课程里几乎不教，但真实项目中到处都是：
  -> 异常不仅是"错误处理"，更是"控制流"
  -> 自定义异常让代码意图清晰（FormatError != bug，LimitsExceeded != crash）
  -> 分层捕获让每一层只关心自己能处理的异常
""")


# ============================================================
# 概念 3: typing 类型系统 — 从 "看懂类型标注" 到 "自己写"
# ============================================================
#
# 你已经见过：list[dict], str | None, Path | None
# 今天深入：Protocol, TypeAlias, Generic, TypedDict, Literal

print("\n\n" + "=" * 60)
print("概念 3: typing — Python 的类型系统")
print("=" * 60)

# --- 3.1 Protocol — Python 的"接口" ---
print("--- 3.1 Protocol：Duck Typing 的静态类型版 ---")
print("""
  Protocol 是 Python 3.8 引入的"结构化子类型"（Structural Subtyping）。
  翻译成人话：我不关心你是谁家的孩子（继承），我只关心你有这些方法。

  对照 mini-swe-agent/src/minisweagent/__init__.py：

  class Model(Protocol):
      def query(self, messages: list[dict]) -> dict: ...
      def format_message(self, **kwargs) -> dict: ...
      ...

  class Environment(Protocol):
      def execute(self, action: dict) -> dict: ...
      ...

  Protocol 关键字：...（Ellipsis）
    -> "这个方法存在，但我不在这里实现"
    -> 不像 Java 的 interface（必须 implements）
    -> 不像 C++ 的纯虚函数（必须 override）
    -> 任何"碰巧"有这些方法的类，都算 Model！

  这就是 default.py 里 __init__ 的 model: Model 能接受
  LitellmModel、AnthropicModel、甚至你自己写的 FakeModel 的原因。
""")

# --- 3.2 TypeAlias + Union/Optional ---
print("--- 3.2 TypeAlias, Union, Optional ---")

# TypeAlias：给复杂类型起个短名字
# 写法1（Python 3.12+）：type JsonDict = dict[str, Any]
# 写法2（Python 3.10+）：直接用变量标注
JsonDict = dict[str, Any]            # 类型别名——本质就是一个"外号"
Message = dict[str, Any]
Messages = list[Message]

# Optional[X] = X | None（就是语法糖）
MaybePath = Path | None              # 等价于 Optional[Path]

def save_data(data: JsonDict, path: MaybePath = None) -> None:
    """演示类型别名——函数签名一目了然。"""
    if path:
        path.write_text(json.dumps(data, indent=2))

print(f"  JsonDict = {JsonDict}")
print(f"  MaybePath = {MaybePath}")

print("""
  在 default.py 里有：
    output_path: Path | None = None
    messages: list[dict] = []

  类型别名让你不用每次都写 list[dict[str, Any]]。
""")

# --- 3.3 Literal — "只能是这几个值" ---
print("--- 3.3 Literal：限定值的范围 ---")

def set_log_level(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]) -> None:
    """level 只能是这四个字符串之一。"""
    print(f"  设置日志级别为 {level}")

set_log_level("INFO")
# set_log_level("VERBOSE")  # <- IDE 会标红！类型检查器会报错！

print("""
  在 mini-swe-agent 里常用：
    role: Literal["system", "user", "assistant", "exit"]
    -> 不是任意字符串，只能是这四种角色
""")

# --- 3.4 TypedDict — "字典有固定结构" ---
print("--- 3.4 TypedDict：给 dict 定义结构 ---")

class ModelStats(TypedDict):
    """模型统计信息的结构定义。"""
    instance_cost: float
    api_calls: int

class AgentData(TypedDict, total=False):  # total=False -> 字段可选
    """Agent 序列化数据的结构。"""
    info: dict[str, Any]
    messages: list[dict[str, Any]]
    trajectory_format: str

stats: ModelStats = {"instance_cost": 0.5, "api_calls": 12}
print(f"  stats = {stats}")

print("""
  普通 dict[str, Any] 的问题是：你不知道里面有什么 key。
  TypedDict 告诉你：这个字典一定有 instance_cost: float 和 api_calls: int。

  在 default.py 的 serialize() 方法里，返回的就是这样一个固定结构的 dict。
""")

# --- 3.5 Generic + TypeVar — 泛型 ---
print("--- 3.5 Generic / TypeVar：泛型容器 ---")

T = TypeVar("T")

class Result(Generic[T]):
    """一个简单的 Result 类型——可以是成功或失败。"""
    def __init__(self, value: T | None = None, error: str | None = None):
        self.value = value
        self.error = error

    @property
    def is_ok(self) -> bool:
        return self.error is None

# 使用
r1: Result[int] = Result(value=42)
r2: Result[str] = Result(error="Not found")

print(f"  r1: is_ok={r1.is_ok}, value={r1.value}")
print(f"  r2: is_ok={r2.is_ok}, error={r2.error}")

print("""
  Generic[T] 让你写一个"适用于任何类型"的容器类。
  mini-swe-agent 里少见，但读其他研究项目（RL、数据处理 pipeline）会大量遇到。
""")

# --- 3.6 Callable — "参数是函数" ---
print("--- 3.6 Callable：标注回调函数 ---")

def apply_transforms(
    data: list[int],
    *transforms: Callable[[int], int]   # <- 每个 transform 是 int -> int 的函数
) -> list[int]:
    """对每个元素依次应用所有变换函数。"""
    result = data
    for transform in transforms:
        result = [transform(x) for x in result]
    return result

def double(x: int) -> int:
    return x * 2

def add_one(x: int) -> int:
    return x + 1

print(f"  apply_transforms([1,2,3], double) = {apply_transforms([1, 2, 3], double)}")
print(f"  apply_transforms([1,2,3], double, add_one) = {apply_transforms([1, 2, 3], double, add_one)}")

print("""
  Callable[[int], int] = "接受 int、返回 int 的函数"
  Callable[[str, int], bool] = "接受 str 和 int、返回 bool 的函数"

  在 agent 代码里：
    execute: Callable[[dict], dict]  <- 接受命令 dict，返回结果 dict
""")

# --- 3.7 cast — "我比类型检查器聪明" ---
print("--- 3.7 cast：告诉类型检查器你知道更多 ---")

def get_config_value(key: str) -> Any:
    """模拟：从配置里取值，返回 Any。"""
    config = {"timeout": 30, "host": "localhost"}
    return config.get(key)

# 类型检查器只知道 raw 是 Any
raw = get_config_value("timeout")
# 你告诉它："相信我，这个 Any 其实是 int"
timeout: int = cast(int, raw)
print(f"  timeout (cast from Any): {timeout} * 2 = {timeout * 2}")

print("""
  cast 不改变运行时行为——它就一个标注，告诉 mypy/pyright
  "我知道类型检查器推断不出来，但这个值就是 X 类型"。
""")


# ============================================================
# PRACTICE: 给自己写的函数加类型标注和异常处理
# ============================================================

print("\n\n" + "=" * 60)
print("练习 1: 给计算器函数加完整类型标注 + 异常处理")
print("=" * 60)

# --- 类型定义 ---
CalcFunc = Callable[[float, float], float]
"""计算器函数的类型——接受两个 float，返回一个 float。"""

class CalcError(Exception):
    """计算器相关异常。"""

class DivisionByZeroError(CalcError):
    """除零错误。"""
    def __init__(self, numerator: float):
        self.numerator = numerator
        super().__init__(f"不能将 {numerator} 除以 0")

# --- 完整版计算器（带类型 + 异常） ---
def safe_add(a: float, b: float) -> float:
    """加法——不会出错，不需要异常处理。"""
    return a + b

def safe_divide_v2(a: float, b: float) -> float:
    """除法——可能除零，抛自定义异常。

    Raises:
        DivisionByZeroError: 当 b 为 0 时
    """
    if b == 0:
        raise DivisionByZeroError(a)
    return a / b

def parse_number(s: str) -> float:
    """把字符串转成数字——可能格式错误。

    Raises:
        ValueError: 当 s 不是合法数字时
    """
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"'{s}' 不是合法的数字") from None  # <- 隐藏原始异常链

def calc(expr: str) -> float:
    """解析并计算简单表达式 'a+b' 或 'a/b'。

    Raises:
        ValueError: 表达式格式不对
        DivisionByZeroError: 除数为 0
    """
    for op in ("+", "/"):
        if op in expr:
            left, right = expr.split(op, 1)
            a = parse_number(left.strip())
            b = parse_number(right.strip())
            if op == "+":
                return safe_add(a, b)
            else:
                return safe_divide_v2(a, b)
    raise ValueError(f"不支持的运算: '{expr}'（目前只支持 + 和 /）")

# --- 测试 ---
print("\n测试 calc():")
test_cases = ["3.14 + 2.86", "10/3", "10/0", "abc + 1", "5 * 3"]

for expr in test_cases:
    try:
        result = calc(expr)
        print(f"  [OK] {expr} = {result}")
    except DivisionByZeroError as e:
        print(f"  [ERR] {expr} -> 除零: {e}")
    except ValueError as e:
        print(f"  [ERR] {expr} -> 格式/值错误: {e}")
    except Exception as e:
        print(f"  [ERR] {expr} -> 未知错误: {type(e).__name__}: {e}")

print("""
  这次和 Day 1 写同样的计算器不一样的地方：
  -> 每个函数有完整类型标注（一看就知道输入输出）
  -> 异常有自定义类型（调用者可以精确捕获 DivisionByZeroError）
  -> raise ... from None 隐藏内部调用链，只显示清晰的错误信息
""")


# ============================================================
# 练习 2: 用 Protocol 定义接口，写一个可替换的模型
# ============================================================

print("\n\n" + "=" * 60)
print("练习 2: 用 Protocol 模拟 default.py 的依赖注入")
print("=" * 60)

# --- 定义协议（就是 minisweagent/__init__.py 里的 Model/Environment Protocol）---
class LLM(Protocol):
    """语言模型协议——任何模型只要实现这个方法就能用。"""
    def query(self, messages: list[dict]) -> dict:
        """发送消息，返回回复。"""
        ...

class Executor(Protocol):
    """执行环境协议。"""
    def execute(self, action: dict) -> dict:
        """执行一个动作，返回结果。"""
        ...

# --- 两个实现：一个真、一个假 ---
class DeepSeekModel:
    """真实的 DeepSeek 模型（简化版）。"""
    def query(self, messages: list[dict]) -> dict:
        # 真实代码里这里调 API
        return {"role": "assistant", "content": "我用 DeepSeek 思考..."}

class FakeModel:
    """假的模型——测试专用！"""
    def __init__(self, fixed_response: str = "fake response"):
        self.fixed_response = fixed_response
        self.call_count = 0

    def query(self, messages: list[dict]) -> dict:
        self.call_count += 1
        return {"role": "assistant", "content": f"[Fake] {self.fixed_response}"}

# --- Agent 只依赖协议，不依赖具体实现 ---
class TypedAgent:
    """带类型标注的 Agent——依赖注入 + Protocol。"""

    def __init__(self, model: LLM, env: Executor | None = None, *, max_steps: int = 3):
        self.model: LLM = model             # <- 类型标注是 Protocol，不是具体类！
        self.max_steps: int = max_steps
        self.history: list[dict] = []

    def run(self, task: str) -> dict:
        """运行 Agent——和 default.py 同样的模式。"""
        self.history = [
            {"role": "system", "content": "You are a coding agent."},
            {"role": "user", "content": task},
        ]
        for _ in range(self.max_steps):
            response = self.model.query(self.history)
            self.history.append(response)
            if "exit" in response.get("content", "").lower():
                break
        return {"status": "done", "steps": len(self.history)}

# --- 测试：同一个 Agent，换不同 Model ---
print("\n用 DeepSeekModel:")
agent1 = TypedAgent(DeepSeekModel(), max_steps=2)
print(f"  结果: {agent1.run('写一个快排')}")

print("\n用 FakeModel（测试模式）:")
fake = FakeModel("我完成了任务! exit")
agent2 = TypedAgent(fake, max_steps=5)
print(f"  结果: {agent2.run('写一个快排')}")
print(f"  FakeModel 被调用了 {fake.call_count} 次")

print("""
  这就是 Protocol 的威力：
    -> Agent 的 __init__ 标的是 model: LLM（协议）
    -> 传入的可以是 DeepSeekModel、FakeModel、AnthropicModel...
    -> 只要它们有 query() 方法，就能工作
    -> 测试时用 FakeModel，不花钱也不调 API
    -> 这就是"依赖注入"+"面向协议编程"的组合拳
""")


# ============================================================
# 练习 3: 重新读 default.py —— 检验五天的成果！
# ============================================================

print("\n\n" + "=" * 60)
print("终极测试：重新打开 default.py，你能认出多少？")
print("=" * 60)

# 重新读取 default.py
default_py = Path(__file__).parent / "mini-swe-agent" / "src" / "minisweagent" / "agents" / "default.py"
code = default_py.read_text(encoding="utf-8")

print(f"""
现在，请打开你的 default.py（{default_py}），
逐段往下读。下面是你应该能认出的每一个概念：
""")

print("""
  +---------------------------------------------------------------+
  |  行号  |  代码片段                 |  用到了什么               |
  +---------------------------------------------------------------+
  |  3-9   | import json, logging      | Day 2: pathlib          |
  |        | from pathlib import Path  |                          |
  +---------------------------------------------------------------+
  |  11    | from jinja2 import ...    | Day 4: 第三方库，       |
  |        |                           | pyproject.toml 声明依赖  |
  +---------------------------------------------------------------+
  |  12    | from pydantic import      | Day 3: @dataclass       |
  |        |   BaseModel               | BaseModel=Pydantic 版    |
  +---------------------------------------------------------------+
  |  15    | from minisweagent.exceptions import (               |
  |        |   FormatError,            | Day 5: 自定义异常体系！  |
  |        |   InterruptAgentFlow,     |   -> 异常当控制流用      |
  |        |   LimitsExceeded,         |                          |
  |        |   TimeExceeded            |                          |
  |        | )                         |                          |
  +---------------------------------------------------------------+
  |  19-35 | class AgentConfig(        | Day 3: @dataclass (但是 |
  |        |   BaseModel):             | Pydantic 版)             |
  |        |   system_template: str    | Day 5: 类型标注！       |
  |        |   step_limit: int = 0     | Day 4: 默认值            |
  |        |   output_path: Path|None  | Day 2: pathlib          |
  |        |                           | Day 5: Union (X|None)   |
  +---------------------------------------------------------------+
  |  38-50 | class DefaultAgent:       |                          |
  |        |   def __init__(self,      | Day 1: **kwargs          |
  |        |     model: Model,         | Day 5: Protocol 类型！   |
  |        |     env: Environment,     | Day 5: Protocol 类型！   |
  |        |     **kwargs):            | Day 1: **kwargs          |
  |        |   self.messages:          | Day 5: 类型标注          |
  |        |     list[dict] = []       | Day 1: type hints        |
  |        |   self.model = model      | Day 3: 依赖注入！        |
  +---------------------------------------------------------------+
  |  52-64 | get_template_vars()       | Day 1: **kwargs          |
  |        |   -> recursive_merge      | Day 4: 了解项目结构      |
  +---------------------------------------------------------------+
  |  66-67 | _render_template()        | Day 1: f-string 精神     |
  +---------------------------------------------------------------+
  |  69-72 | add_messages(*messages)   | Day 1: *args 展开！     |
  |        |   -> self.messages.extend  | Day 5: 类型标注          |
  +---------------------------------------------------------------+
  |  74-86 | handle_uncaught_          | Day 5: 异常处理！        |
  |        |   exception(e: Exception) | Day 5: 类型标注          |
  |        |   -> format_message(      |                          |
  |        |     role="exit", ...)     | Day 5: Literal 类型！    |
  +---------------------------------------------------------------+
  |  88-122| run() <- 核心方法！       |                          |
  |        |   def run(                | Day 1: **kwargs          |
  |        |     self, task: str="",   | Day 5: 类型标注          |
  |        |     **kwargs) -> dict:    | Day 5: 返回类型          |
  |        |   self.extra_template_    | Day 1: |= 字典合并       |
  |        |     vars |= {**kwargs}    |                          |
  |        |   while True:             |                          |
  |        |     try:                  | Day 5: 异常分三层！      |
  |        |       self.step()         |   try/except/else/finally|
  |        |     except FormatError:   |   FormatError -> 可恢复   |
  |        |     except Interrupt-     |   InterruptAgentFlow ->   |
  |        |       AgentFlow:          |     正常退出              |
  |        |     except Exception:     |   未知异常 -> 记录 + raise |
  |        |       ... raise           |                          |
  |        |     finally:              | Day 5: finally 存盘！    |
  |        |       self.save(...)      | Day 2: Context Manager   |
  |        |                           |   精神的手动版           |
  +---------------------------------------------------------------+
  |  124-126| def step() -> list[dict]:| Day 5: 返回类型标注      |
  |        |   return self.execute_    | Day 1: comprehension    |
  |        |     actions(self.query()) |         风格（一行！）    |
  +---------------------------------------------------------------+
  |  128-150| def query() -> dict:     | Day 5: 类型标注          |
  |        |   if step_limit <= ...:   | Day 5: 异常做控制流！    |
  |        |     raise LimitsExceeded  |   用 raise 退出循环      |
  |        |   self.model.query(       |                          |
  |        |     self.messages)        |                          |
  |        |   self.cost += message    |                          |
  |        |     .get("extra", {})     |                          |
  |        |     .get("cost", 0.0)     | dict 的链式 .get()      |
  +---------------------------------------------------------------+
  |  152-155| execute_actions()        |                          |
  |        |   outputs = [self.env     | Day 1: List comprehens-  |
  |        |     .execute(action)      |   ion——列表推导式！      |
  |        |     for action in ...]    | Day 5: 类型推断          |
  |        |   self.add_messages(      | Day 1: *args 展开        |
  |        |     *self.model           |                          |
  |        |     .format_observation   |                          |
  |        |     _messages(...)        |                          |
  |        |   )                       |                          |
  +---------------------------------------------------------------+
  |  157-178| serialize() -> dict:     | Day 5: 返回类型          |
  |        |   f"{self.__class__       | Day 2: f-string！        |
  |        |     .__module__}..."      |                          |
  |        |                           |                          |
  +---------------------------------------------------------------+
  |  180-188| save(path: Path|None)    | Day 5: Union 类型        |
  |        |   path.parent.mkdir(      | Day 2: pathlib！         |
  |        |     parents=True,         |                          |
  |        |     exist_ok=True)        |                          |
  |        |   path.write_text(        | Day 2: Path 一行写文件！ |
  |        |     json.dumps(           |                          |
  |        |       data, indent=2))    |                          |
  +---------------------------------------------------------------+
""")


# ============================================================
# 最终检验：你能回答这些问题吗？
# ============================================================

print("\n" + "=" * 60)
print("Day 5 自我检验：能答上来说明五天没白学")
print("=" * 60)

questions = [
    ("Day 1", "execute_actions 里用了什么语法在一行内执行多个 action？",
     "List Comprehension: [self.env.execute(a) for a in ...]"),

    ("Day 1", "add_messages(*messages) 里的 * 是什么意思？",
     "参数展开——把元组/列表拆成一个个参数传给函数"),

    ("Day 2", "save() 方法用 pathlib 做了什么？",
     "path.parent.mkdir(parents=True) 创建目录 + path.write_text() 写文件"),

    ("Day 3", "AgentConfig(BaseModel) 和 @dataclass 是什么关系？",
     "BaseModel 是 Pydantic 的 dataclass 增强版：类型校验 + JSON 序列化 + model_dump()"),

    ("Day 3", "DefaultAgent.__init__ 为什么不内部 new Model()？",
     "依赖注入：把依赖从外部传进来，方便测试和替换"),

    ("Day 4", "from minisweagent.agents import get_agent 为什么能 work？",
     "agents/__init__.py 把 get_agent 暴露在包层面，作为 API 门面"),

    ("Day 4", "mini.py 底部 if __name__ == '__main__': app() 的作用？",
     "直接运行时启动 TUI，被 import 时不启动"),

    ("Day 5", "run() 里 except 分了三层，每层什么意思？",
     "FormatError->可恢复，InterruptAgentFlow->正常退出，Exception->记录+raise"),

    ("Day 5", "run() 里的 finally: self.save() 为什么重要？",
     "ensure 每步都存盘，即使崩了也不会丢全部数据（= Context Manager 精神）"),

    ("Day 5", "model: Model 里的 Model 是什么？为什么可以是 Protocol？",
     "Protocol = 结构化子类型，任何有 query()/format_message() 的类都能当 Model 用"),
]

# 自动展示问题和答案（非交互模式）
for day, question, answer in questions:
    print(f"\n  [{day}] {question}")
    print(f"  -> {answer}")

print("\n\n" + "=" * 60)
print("五天总结：你的 Python 工具箱")
print("=" * 60)

print("""
  Day 1 - Generator/yield, List Comprehension, Decorator, *args/**kwargs
  Day 2 - f-string, pathlib, Context Manager (with/__enter__/__exit__)
  Day 3 - @dataclass, @property, __str__/__repr__/__call__, 依赖注入
  Day 4 - if __name__=="__main__", __init__.py, pyproject.toml, 精读 default.py
  Day 5 - Exception(try/except/else/finally), typing(Protocol/TypeAlias/...), 检验

  五天前：能写 Python，但看不懂 default.py 的设计意图
  五天后：default.py 的 190 行，每一行都能说出它用了什么、为什么这样写

  接下来四条线继续推进：
    1. Python [DONE]（五天进阶完成，之后在实践中积累）
    2. C++ -> 待启动
    3. GitHub -> 待启动
    4. Transformer -> 待启动
""")

print("\n*** Day 5 完成！Python 进阶之旅到此结束。 ***")
print("   你的 default.py 阅读能力：从 ~30% -> ~85%+")
