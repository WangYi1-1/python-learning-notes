# Day 2: 文件操作 + 上下文管理

## 学习内容

### 1. f-string（格式化字符串）

- 比 Java 的 `String.format()` 和 `+` 拼接都方便
- 字符串里直接写变量：`f"{name} 考了 {score} 分"`
- 支持表达式：`f"明年 {score + 1} 分"`
- 支持格式化：`f"{3.1415:.2f}"` → `3.14`

### 2. pathlib（现代化文件路径）

- 替代 `os.path`，面向对象写法
- `/` 运算符拼接路径：`Path("data") / "images"`
- 一行读文件：`p.read_text()`
- 一行写文件：`p.write_text("hello")`
- 遍历目录：`Path(".").glob("*.py")`
- mini-swe-agent 项目规范明确要求使用 pathlib

### 3. with / Context Manager（上下文管理器）

- `with open("a.txt") as f:` — 自动关闭文件，不管是否异常
- 核心魔法：`__enter__`（进 with 时）和 `__exit__`（出 with 时）
- 自己写 Context Manager：
  - 类写法：实现 `__enter__` / `__exit__`
  - 函数写法：`@contextmanager` + `yield`（结合 Day 1 的 generator）

### 4. Day 1 + Day 2 联动

- `@contextmanager` + `yield` = generator 和 Context Manager 的结合
- `Timer` 计时器用 with 语法自动打印耗时

## 练习文件

- `learn_python_day2.py` — 可运行的交互式学习脚本
