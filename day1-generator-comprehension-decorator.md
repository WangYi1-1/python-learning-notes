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
