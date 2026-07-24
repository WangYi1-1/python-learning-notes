# Python 进阶 Day 1：Generator、Comprehension、Decorator

> 日期：2026-07-24  
> 项目：暑假科研基础夯实 — Python 线  
> 仓库：[python-learning-notes](https://github.com/WangYi1-1/python-learning-notes)

---

## 一、Generator / yield

### 为什么需要？

普通函数 `return` 一次性返回所有结果，数据量大时内存爆炸：

```python
# 旧写法：1000万行全存内存
def yanghui(n):
    rows = []
    for i in range(n):
        row = 算一行
        rows.append(row)
    return rows  # 内存爆了
```

Generator 用 `yield` 每次只产生一个值，用完就扔：

```python
def yanghui_rows(n: int):
    row = [1]
    for _ in range(n):
        yield row  # 返回一行，暂停，等下次调用
        row = [1] + [row[i] + row[i+1] for i in range(len(row)-1)] + [1]
```

### yield vs return

| | `return` | `yield` |
|---|---|---|
| 行为 | 返回全部，函数结束 | 返回一个，暂停在这 |
| 下次调用 | 从头重新执行 | 从 yield 之后继续 |
| 比喻 | 复印整本书再给你 | 一页一页撕给你，读了就扔 |

### 练习：斐波那契数列 Generator

```python
def fibonacci(n: int):
    a, b = 1, 1
    for i in range(n):
        yield a
        a, b = b, a + b

print(list(fibonacci(10)))
# 输出：[1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

---

## 二、List / Dict Comprehension

### 语法

```python
[表达式 for 临时变量 in 来源 if 条件(可选)]
```

### 对比 Java 风格

```python
# Java 风格（Python 里不推荐）
old = []
for x in range(10):
    if x % 2 == 0:
        old.append(x * x)

# Python comprehension（一行搞定）
new = [x * x for x in range(10) if x % 2 == 0]
# → [0, 4, 16, 36, 64]
```

### Dict comprehension

```python
{x: x * x for x in range(5)}
# → {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

### 三种括号的区别

| 符号 | 生成什么 | 例子 |
|------|---------|------|
| `[...]` | list（列表） | `[x*x for x in range(3)]` → `[0, 1, 4]` |
| `{...}` | dict（字典） | `{x: x*x for x in range(3)}` → `{0:0, 1:1, 2:4}` |
| `(...)` | generator（惰性） | `(x*x for x in range(3))` → `<generator>` |

### 练习：过滤器改写

```python
def filter_and_upper_new(words: list[str], min_len: int) -> list[str]:
    return [w.upper() for w in words if len(w) >= min_len]
```

---

## 三、Decorator（装饰器）

### 本质

装饰器 = **接受函数，返回加了功能的函数**

```python
@decorator        # 语法糖
def func(): ...   # 等价于 func = decorator(func)
```

### 结构模板

```python
def 装饰器名(原函数):
    def 包装函数(*args, **kwargs):
        # 执行前：做点什么
        result = 原函数(*args, **kwargs)   # 调用原函数
        # 执行后：做点什么
        return result
    return 包装函数
```

### 示例：@timer 计时器

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  [TIMER] {func.__name__}: {elapsed:.6f}s")
        return result
    return wrapper

@timer
def slow_sum(n: int) -> int:
    total = 0
    for i in range(n):
        total += i
    return total

slow_sum(10000000)  # 自动打印耗时
```

### 练习：@bold 装饰器

```python
def bold(func):
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

@bold
def greet(name: str) -> str:
    return f"Hello, {name}!"

print(greet("World"))  # <b>Hello, World!</b>
```

---

## 四、附赠：*args 和 **kwargs

| 语法 | 含义 | 类型 |
|------|------|------|
| `*args` | 吃掉所有多余的位置参数 | `tuple` |
| `**kwargs` | 吃掉所有多余的关键字参数 | `dict` |

装饰器的 `wrapper` 里用它们，是因为 wrapper 不知道原函数要什么参数，所以 **全收下再全传过去**。

---

## 五、新认识的 Python 内置函数

| 函数 | 作用 | 例句 |
|------|------|------|
| `enumerate(seq)` | 遍历时自动编号，返回 `(下标, 值)` | `for i, x in enumerate(list):` |
| `list(gen)` | 把 generator 转成列表 | `list(fibonacci(10))` |

---

## 六、Type Hints 类型标注

```python
def yanghui_rows(n: int):                          # 参数 n 是 int
def greet(name: str) -> str:                       # 参数是 str，返回值也是 str
def filter_and_upper(words: list[str], min_len: int) -> list[str]:
```

- Python 运行时不强制检查，只是给人看的
- 相当于 Java 的 `int sum(int n)` 但写的位置不同
- mini-swe-agent 项目代码里到处在用，读源码前必须认识

---

## 今日总结

| 概念 | 一句话 | 动手写了 |
|------|--------|---------|
| `yield` | 不用 return 全量结果，一个一个给，省内存 | `fibonacci` generator |
| Comprehension | `[表达式 for x in 来源 if 条件]` 一行替代 for+append | `filter_and_upper_new` |
| Decorator | 不碰原函数，给它加功能 | `@bold` 包装返回值为 `<b>...</b>` |

---

# Day 2：f-string、pathlib、Context Manager

> 日期：2026-07-24  
> 练习文件：`learn_python_day2.py`

---

## 一、f-string（格式化字符串）

### 语法

```python
f"字符串里直接写 {变量} 和 {表达式}"
```

### 对比旧写法

```python
# 用 + 拼（Java 风格，Python 里不推荐）
"第" + str(i) + "行: " + str(row)

# f-string
f"第{i+1}行: {row}"
```

### 常用格式化

```python
f"π ≈ {3.14159:.2f}"      # :.2f  保留2位小数
f"{1000000:,}"             # :,    加千分位 → "1,000,000"
f"|{42:<10}|"              # :<10  左对齐占10位
f"|{42:>10}|"              # :>10  右对齐占10位
f"|{42:^10}|"              # :^10  居中占10位
```

### 练习：收银条格式化

```python
def report_new(items: list[str], prices: list[float]) -> str:
    result = ""
    total = 0
    for i in range(len(items)):
        result += f"{items[i]}: ￥{prices[i]:.2f}\n"
        total += prices[i]
    result += f"总计: ￥{total}"
    return result
```

---

## 二、pathlib（现代化文件路径）

### 核心对照表

| 旧世界 `os.path` | 新世界 `pathlib` |
|-----------------|-----------------|
| `os.path.join("a", "b", "c")` | `Path("a") / "b" / "c"` |
| `os.path.exists("x.txt")` | `Path("x.txt").exists()` |
| `open("x.txt").read()` | `Path("x.txt").read_text()` |
| `open("x.txt", "w").write("hi")` | `Path("x.txt").write_text("hi")` |

### 常用操作

```python
p = Path("file.py")
p.resolve()      # 绝对路径
p.parent         # 父目录
p.suffix         # 后缀 .py
p.exists()       # 是否存在
p.stat().st_size # 文件大小（字节）
p.read_text()    # 读全部文本（不用 open/close！）
p.write_text("hello")  # 写文件

# 遍历目录下所有 .py 文件
for py_file in Path(".").glob("*.py"):
    print(py_file)
```

**mini-swe-agent 项目规范明确写了：** "Use pathlib instead of os.path"

### 练习：统计代码行数

```python
def count_lines_new(directory: str) -> dict[str, int]:
    result = {}
    for p in Path(directory).glob("*.py"):
        result[p.name] = len(p.read_text().splitlines())
    return result
```

---

## 三、with / Context Manager（上下文管理器）

### 为什么需要？

Java 必须手动 `close()`：
```java
FileReader fr = new FileReader("a.txt");
try { ... }
finally { fr.close(); }  // 忘了就内存泄漏
```

Python 的 `with` **自动关闭**，不管中间有没有异常：
```python
with open("a.txt") as f:
    content = f.read()
# 出了缩进自动关闭，不用写 close()
```

### 自己实现 Context Manager

任何类实现了 `__enter__` 和 `__exit__` 就能用 `with`：

```python
class ResourceTracker:
    def __enter__(self):
        print("打开资源")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("释放资源")   # 无论如何都会执行（= Java finally）

with ResourceTracker():
    print("  正在使用资源...")
# 输出：打开资源 → 正在使用资源 → 释放资源
```

### @contextmanager 快捷写法（Day 1 + Day 2 联动）

```python
from contextlib import contextmanager

@contextmanager
def timer_cm():
    start = time.perf_counter()
    yield           # ← Day 1 的 yield！之前 = __enter__，之后 = __exit__
    elapsed = time.perf_counter() - start
    print(f"耗时: {elapsed:.4f}s")

with timer_cm():
    do_something()
```

---

## 四、class 基础（对比 Java）

| Java | Python |
|------|--------|
| `class Timer { }` | `class Timer:` |
| `public void enter() { }` | `def __enter__(self):` |
| `this.start` | `self.start` |
| `Timer t = new Timer()` | `t = Timer()` |

- 花括号 → 冒号 + 缩进
- `this` → `self`（必须显式写在参数里）

---

## Day1+2 总结

| 概念 | 一句话 | 写了 |
|------|--------|------|
| `yield` | 不 return 全部，一个个给 | `fibonacci` |
| Comprehension | `[x for x in ... if ...]` 一行替代 for+append | `filter_and_upper_new` |
| Decorator | 不碰原函数，给它加功能 | `@bold` |
| f-string | `f"{变量}"` 直接写，不用 + 拼字符串 | `report_new` |
| pathlib | `Path("a")/"b"`，`read_text()` 不用 open | `count_lines_new` |
| with / Context Manager | 自动管理资源，永不漏关 | `ResourceTracker` |
