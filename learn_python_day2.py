"""
Python 进阶 Day 2: Context Manager, pathlib, f-string
======================================================
每个概念：
  EXPLAIN — 为什么需要
  EXAMPLE — 能跑的示范
  PRACTICE — <TODO> 自己写

运行方式：python learn_python_day2.py
"""

from pathlib import Path
from contextlib import contextmanager
import time
import os

# ============================================================
# 概念 1: f-string（格式化字符串）
# ============================================================
#
# 你写 Java 拼字符串：
#   String s = "第" + i + "行: " + row;
# 或者：
#   String s = String.format("第%d行: %s", i, row);
#
# Python f-string 比这两种都方便——直接在字符串里写变量：

print("=" * 50)
print("概念 1: f-string")
print("=" * 50)

name = "Alice"
score = 95
print(f"  {name} 考了 {score} 分")
#      ↑直接写变量↑    ↑直接写变量↑

# f-string 里还能写表达式：
print(f"  明年 {name} 就 {score + 1} 分了")  # 不是 95 是 96
print(f"  {name.upper()} 是大写")            # 调方法

# 数字格式化：
print(f"  π ≈ {3.1415926535:.2f}")          # 保留2位小数
print(f"  1000000 加逗号: {1000000:,}")       # 加千分位

# f-string 的方法：
x = 42
print(f"  |{x:<10}|  左对齐，占10位")   # < 左对齐
print(f"  |{x:>10}|  右对齐，占10位")   # > 右对齐
print(f"  |{x:^10}|  居中，占10位")     # ^ 居中


# ============================================================
# PRACTICE 1: 把下面的旧写法改成 f-string
# ============================================================

def report_old(items: list[str], prices: list[float]) -> str:
    """旧写法：用 + 拼字符串"""
    result = ""
    total = 0
    for i in range(len(items)):
        result += items[i] + ": ￥" + str(prices[i]) + "\n"
        total += prices[i]
    result += "总计: ￥" + str(total)
    return result


def report_new(items: list[str], prices: list[float]) -> str:
    """<TODO>: 用 f-string 重写，每行格式为 '商品名: ￥价格'，保留2位小数"""
    result = ""
    total = 0
    for i in range(len(items)):
        result += f"{items[i]}: ￥{prices[i]:.2f}\n"
        total += prices[i]
    result += f"总计: ￥{total}"
    return result


sample_items = ["可乐", "薯片", "泡面"]
sample_prices = [3.5, 8.0, 4.5]
print(f"\n旧写法输出:\n{report_old(sample_items, sample_prices)}")
print(f"\nf-string 输出:\n{report_new(sample_items, sample_prices)}")


# ============================================================
# 概念 2: pathlib（现代化文件路径）
# ============================================================
#
# 你以前可能用 os.path 这些：
#   os.path.join("a", "b", "c")
#   os.path.exists("file.txt")
#   open("file.txt", "r").read()
#
# pathlib 把这些全统一成面向对象写法，mini-swe-agent 项目规范里明确写了：
# "Use pathlib instead of os.path"

print("\n\n" + "=" * 50)
print("概念 2: pathlib")
print("=" * 50)

# 创建路径对象
p = Path("learn_python_day2.py")
print(f"\n  文件名: {p}")
print(f"  绝对路径: {p.resolve()}")
print(f"  父目录: {p.parent}")
print(f"  后缀: {p.suffix}")
print(f"  是否存在: {p.exists()}")
print(f"  文件大小: {p.stat().st_size} bytes")

# 常用操作（不需要 open() + close()）：
print(f"\n  读取全部文本: {p.read_text()[:50]}...")  # 读前 50 字
# p.write_text("hello")  # 写文件，一行搞定

# 遍历目录：
print(f"\n  当前目录下所有 .py 文件:")
for py_file in Path(".").glob("*.py"):
    print(f"    {py_file}")

# 路径拼接（/ 运算符，比 os.path.join 直观）：
data_dir = Path("data") / "images" / "2024"
print(f"\n  拼接路径: {data_dir}")

# 创建目录：
# data_dir.mkdir(parents=True, exist_ok=True)  # 相当于 mkdir -p


# ============================================================
# PRACTICE 2: 用 pathlib 统计代码行数
# ============================================================

def count_lines_old(directory: str) -> dict[str, int]:
    """旧写法：用 os.path 统计目录下所有 .py 文件的行数"""
    import os
    result = {}
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as f:
                result[filename] = len(f.readlines())
    return result


def count_lines_new(directory: str) -> dict[str, int]:
    """<TODO>: 用 pathlib 重写上面这个函数"""
    result = {}
    for p in Path(directory).glob("*.py"):
        result[p.name] = len(p.read_text().splitlines())
        return result

# print(f"\n各文件行数 (旧): {count_lines_old('.')}")
# print(f"各文件行数 (新): {count_lines_new('.')}")  # <-- 写完后取消注释


# ============================================================
# 概念 3: with / Context Manager（上下文管理器）
# ============================================================
#
# 你写 Java 读文件：
#   FileReader fr = new FileReader("a.txt");
#   try {
#       // 读文件
#   } finally {
#       fr.close();  // 必须手动关！
#   }
#
# Python 的 with 自动帮你关，不管中间有没有异常：
#
#   with open("a.txt") as f:
#       content = f.read()
#   # 出了 with 块，文件自动关闭
#
# with 的魔法：进入 with 时调用 __enter__，离开时调用 __exit__
# 你可以自己写一个支持 with 的类

print("\n\n" + "=" * 50)
print("概念 3: Context Manager")
print("=" * 50)


# EXAMPLE — 自己动手写一个计时器 Context Manager
class Timer:
    """用 with 语法计时。进入 with 时开始计时，退出时打印耗时。"""

    def __enter__(self):
        self.start = time.perf_counter()
        return self  # 这个会赋给 as 后面的变量

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.start
        print(f"  [TIMER] 耗时: {elapsed:.4f}s")
        # 返回 False 表示不吞掉异常


print("\n手动计时：")
with Timer():
    total = sum(range(10_000_000))
    print(f"  结果: {total}")
# 出了 with 块，自动打印耗时


# 更简单的写法：用 @contextmanager 装饰器 + yield（Day 1 学的！）
@contextmanager
def timer_cm():
    """跟上面的 Timer 类功能一样，但用 generator 写更简洁"""
    start = time.perf_counter()
    yield  # ← Day 1 学的 yield！在这里暂停，等 with 块执行完再继续
    elapsed = time.perf_counter() - start
    print(f"  [TIMER] 耗时: {elapsed:.4f}s")


print("\n装饰器版计时器：")
with timer_cm():
    total = sum(range(10_000_000))
    print(f"  结果: {total}")


# ============================================================
# PRACTICE 3: 写一个资源追踪 Context Manager
# ============================================================

class ResourceTracker:
    """
    <TODO>: 实现一个 Context Manager
    - 进入 with 时：打印 "打开资源"
    - 离开 with 时：打印 "释放资源"
    - 无论中间是否抛异常，都要打印 "释放资源"
    """
    def __enter__(self):
        print("打开资源")

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("释放资源")


print("\n测试 ResourceTracker：")
with ResourceTracker():
    print("  正在使用资源...")        # <-- 写完后取消注释
# 期望输出：
#   打开资源
#     正在使用资源...
#   释放资源


# ============================================================
# BONUS: Day 1 + Day 2 合体练习
# ============================================================

print("\n\n" + "=" * 50)
print("合体练习：写一个代码统计工具")
print("=" * 50)

# 要求：用 pathlib 遍历目录，用 f-string 格式化输出，用 with 语法读文件
# 统计当前目录下每个 .py 文件的行数和大小

def scan_py_files(directory: str = ".") -> None:
    """<TODO>:
    遍历 directory 下所有 .py 文件，
    打印每个文件的文件名、行数、大小（用 f-string 格式化）
    """
    for p in Path(directory).glob("*.py"):
        print(f"{p.name},{len(p.read_text().splitlines())}，{p.stat().st_size}")


print("\n\n===== Day 2 总结 =====")
print("  1. f-string — 字符串里直接写变量和表达式，比 + 拼接和 % 格式化都好用")
print("  2. pathlib — 面向对象的文件路径，/ 拼接，read_text() 一行读文件")
print("  3. with/Context Manager — 自动管理资源，别忘了你还能自己写")
print("  4. @contextmanager + yield = Day 1 和 Day 2 联动了！")
