"""
Python 进阶 Day 3: @dataclass, @property, __str__/__call__
==========================================================
每个概念：
  EXPLAIN — 为什么需要
  EXAMPLE — 能跑的示范
  PRACTICE — <TODO> 自己写
  REAL WORLD — mini-swe-agent 里怎么用的

运行方式：python learn_python_day3.py
"""

from dataclasses import dataclass, field
import math

# ============================================================
# 概念 0: __init__ / self 快速回顾（5 分钟）
# ============================================================
#
# Java 里的类：
#   class Person {
#       String name;
#       int age;
#       Person(String name, int age) { this.name = name; this.age = age; }
#   }
#
# Python 等价写法：

print("=" * 50)
print("概念 0: __init__ / self 回顾")
print("=" * 50)


class Person:
    """Python 的 __init__ 就是 Java 的构造函数。self = Java 的 this。"""

    def __init__(self, name: str, age: int):
        self.name = name  # self.name 是实例变量
        self.age = age

    def greet(self) -> str:
        return f"我是 {self.name}，今年 {self.age} 岁"


p = Person("小明", 20)
print(f"  {p.greet()}")
# 输出：我是小明，今年20岁

# 关键区别：
# - Python 用 self（约定俗成，写 this 也能跑但不规范）
# - self 必须显式写在方法参数里（Java 隐式传 this）
# - __init__ 不是真正的构造函数——对象已经创建好了，__init__ 只是初始化


# ============================================================
# 概念 1: @dataclass — 告别手写 __init__
# ============================================================
#
# 问题：每写一个类就要手写一遍 __init__，里面全是 self.x = x，烦不烦？
# Person 类上面 4 行 __init__ 其实只做了一件事——赋值。
#
# @dataclass 做的事情：你声明字段，它自动生成 __init__、__repr__、__eq__
#
# 对比：

print("\n\n" + "=" * 50)
print("概念 1: @dataclass")
print("=" * 50)

# --- 旧写法（手写 __init__）---
class StudentOld:
    def __init__(self, name: str, score: int, grade: str = "大一"):
        self.name = name
        self.score = score
        self.grade = grade

    def __repr__(self):  # 还得手写 __repr__ 不然打印出来是 <__main__.StudentOld at 0x...>
        return f"StudentOld(name={self.name!r}, score={self.score}, grade={self.grade!r})"


# --- 新写法（@dataclass）---
@dataclass
class Student:
    """三行搞定！__init__、__repr__、__eq__ 全自动生成"""
    name: str
    score: int
    grade: str = "大一"  # 有默认值的放后面


s1 = Student("小明", 95)
s2 = Student("小明", 95)
print(f"  s1: {s1}")                       # 自动生成的 __repr__
print(f"  s1 == s2: {s1 == s2}")           # 自动生成的 __eq__（逐个字段比较！）
# 如果手写 __init__ 不做 __eq__，这里会是 False（比较内存地址）

# --- @dataclass 的常用参数 ---


@dataclass
class Config:
    """模拟 mini-swe-agent 的 AgentConfig"""
    model_name: str = "deepseek-v4-pro"
    temperature: float = 0.0
    step_limit: int = 100
    # field() 可以定制更复杂的行为
    tags: list[str] = field(default_factory=list)  # ⚠️ 可变默认值必须用 default_factory！


cfg = Config(step_limit=50)
print(f"\n  Config: {cfg}")
print(f"  model_name: {cfg.model_name}")
print(f"  tags 初始为空: {cfg.tags}")


# ⚠️ 常见陷阱：可变默认值
# 错误写法：tags: list = []  ← 所有实例共享同一个 list！
# 正确写法：tags: list[str] = field(default_factory=list)  ← 每个实例各自新建


# ============================================================
# PRACTICE 1: 用 @dataclass 重写"代码统计配置"
# ============================================================

# 手写版（你能看出它只做赋值吗？）
class ScanConfigOld:
    def __init__(self, directory: str = ".", pattern: str = "*.py",
                 show_size: bool = True, show_lines: bool = True):
        self.directory = directory
        self.pattern = pattern
        self.show_size = show_size
        self.show_lines = show_lines


# <TODO>: 用 @dataclass 重写，3 行以内
@dataclass
class ScanConfig:
    directory: str = "."
    pattern: str = "*.py"
    show_size: bool = True
    show_lines: bool = True


print(f"\n  ScanConfig: {ScanConfig()}")
print(f"  ScanConfig(pattern='*.java'): {ScanConfig(pattern='*.java')}")


# ============================================================
# 概念 2: @property — 像属性一样调方法
# ============================================================
#
# 问题：你写了 get_xxx() / set_xxx()，调用时写 obj.get_xxx()
#      但 Python 里可以直接 obj.xxx，更自然
#
# Java:
#   person.getAge();      // 方法调用
#   person.setAge(20);
#
# Python @property：
#   person.age             # 像属性一样读
#   person.age = 20        # 像属性一样写
#
# 好处：外面的人用起来像属性，里面你想怎么算就怎么算

print("\n\n" + "=" * 50)
print("概念 2: @property")
print("=" * 50)


class Circle:
    def __init__(self, radius: float):
        self._radius = radius  # 下划线开头 = "这是内部变量，别直接动"

    # getter — 像属性一样读
    @property
    def radius(self) -> float:
        """读 radius 时自动调这个方法"""
        return self._radius

    # setter — 像属性一样写
    @radius.setter
    def radius(self, value: float):
        """写 radius 时自动调这个方法——可以加校验！"""
        if value < 0:
            raise ValueError(f"半径不能为负数，你给了 {value}")
        self._radius = value

    # 只读属性（没有 setter）
    @property
    def area(self) -> float:
        """面积是算出来的，不能直接设。像属性一样读：c.area"""
        return math.pi * self._radius ** 2

    @property
    def circumference(self) -> float:
        """周长也是算出来的"""
        return 2 * math.pi * self._radius


c = Circle(5)
print(f"  半径: {c.radius}")        # 不用写 c.get_radius()！
print(f"  面积: {c.area:.2f}")      # 不用写 c.get_area()！
print(f"  周长: {c.circumference:.2f}")

c.radius = 10                        # 不用写 c.set_radius(10)！
print(f"  改半径后面积: {c.area:.2f}")

try:
    c.radius = -1                    # setter 里的校验会拦截
except ValueError as e:
    print(f"  [ERROR] {e}")

# c.area = 100  # AttributeError: can't set attribute（没有 setter）

# --- @property 的另一个经典用途：惰性计算 ---


class DataSet:
    """假装这是一个很大的数据集"""
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._data = None  # 先不加载

    @property
    def data(self) -> list:
        """第一次访问才加载，之后直接用缓存"""
        if self._data is None:
            print(f"  [惰性加载] 正在读 {self.filepath}...")
            self._data = ["row1", "row2", "row3"]  # 假装是大文件
        return self._data


ds = DataSet("big_data.csv")
print(f"\n  还没加载，_data = {ds._data}")
print(f"  第一次访问: {ds.data}")   # 触发加载
print(f"  第二次访问: {ds.data}")   # 直接用缓存，不会重复加载


# ============================================================
# PRACTICE 2: 给"温度计"类加 @property
# ============================================================

class Thermometer:
    """
    <TODO>:
    1. 用 @property 保护 _celsius，设值时校验不能低于 -273.15（绝对零度）
    2. 加只读属性 fahrenheit，自动换算：F = C * 9/5 + 32
    3. 加只读属性 kelvin，自动换算：K = C + 273.15
    """
    def __init__(self, celsius: float = 0.0):
        self._celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if  value < -273.15:
            raise ValueError(f"温度不能低于绝对零度，你给了{value}")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32

    @property
    def kelvin(self):
        return self._celsius + 273.15


t = Thermometer(25)
print(f"\n  摄氏: {t.celsius}°C")
print(f"  华氏: {t.fahrenheit}°F")
print(f"  开尔文: {t.kelvin}K")

t.celsius = 100
print(f"  沸点: {t.celsius}°C = {t.fahrenheit}°F = {t.kelvin}K")

try:
    t.celsius = -300
except ValueError as e:
    print(f"  [ERROR] {e}")


# ============================================================
# 概念 3: __str__ / __repr__ / __call__ — "魔法方法"
# ============================================================
#
# Python 里 __ 双下划线开头的方法叫 "dunder methods"（double underscore）
# 它们不是给你直接调的——是 Python 解释器在特定时刻自动调的
#
# 你已经知道：
#   __init__ — 创建对象时自动调
#   __enter__ / __exit__ — 进/出 with 块时自动调
#
# 今天学三个最常见的：

print("\n\n" + "=" * 50)
print("概念 3: __str__ / __repr__ / __call__")
print("=" * 50)

# --- __str__ vs __repr__ ---
# __str__:  给人看的，print() 和 str() 调它。目标是"好看"
# __repr__: 给开发者看的，repr() 和交互式环境调它。目标是"无歧义"——最好能 eval 回来


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        """无歧义的表示——如果可能，应该像能 eval 回来的代码"""
        return f"Point({self.x}, {self.y})"

    def __str__(self):
        """给人看的友好表示"""
        return f"({self.x}, {self.y})"

    # --- __call__ — 让实例像函数一样被调用 ---
    def __call__(self, scalar: float):
        """p(2) = 把坐标乘以 2"""
        return Point(self.x * scalar, self.y * scalar)


p = Point(3, 4)
print(f"  str(p)  = {p}")           # print() 调 __str__
print(f"  repr(p) = {p!r}")         # !r 强制用 __repr__
# 在交互式环境（>>>）里直接敲 p，会显示 __repr__

print(f"  p(2)    = {p(2)}")        # __call__ — 实例当函数用！
print(f"  p(0.5)  = {p(0.5)}")

# ─── __call__ 的实战价值 ───
# 什么时候需要让实例"可调用"？
# 场景：一个函数需要"配置"，但又想保留状态


class Threshold:
    """一个可调用的过滤器：大于 threshold 的值保留，否则变 0"""
    def __init__(self, threshold: float):
        self.threshold = threshold

    def __call__(self, value: float) -> float:
        return value if value > self.threshold else 0.0


above_60 = Threshold(60)
scores = [45, 78, 92, 55, 88]
filtered = [above_60(s) for s in scores]
print(f"\n  原始分数: {scores}")
print(f"  及格以上: {filtered}")

# 这就是为什么 @dataclass 的 __call__ 这么有用——
# 你的对象既可以存配置，又可以直接当函数用。


# ============================================================
# PRACTICE 3: 实现一个"计数器"类，支持 __call__
# ============================================================

class Counter:
    """
    <TODO>: 实现一个计数器
    - __init__: 设初始值（默认 0）
    - __call__: 每次调 counter()，计数 +1，返回新值
    - __str__:   返回 f"计数器: {当前值}"
    - __repr__:  返回 f"Counter({初始值})"
    """
    def __init__(self, start: int = 0):
        self.start = start
        self.count = start

    def __call__(self):
        self.count += 1
        return self.count

    def __str__(self):
        return f"计数器: {self.count}"

    def __repr__(self):
        return f"Counter({self.start})"


c = Counter(10)
print(f"\n  {c}")           # 计数器: 10
print(f"  第1次: {c()}")   # 11
print(f"  第2次: {c()}")   # 12
print(f"  第3次: {c()}")   # 13
print(f"  {c}")            # 计数器: 13
print(f"  repr: {c!r}")    # Counter(10)


# ============================================================
# 综合练习：把杨辉三角改成 OOP 版
# ============================================================
# 你已经写过杨辉三角（Yanghui.java），现在用 Python 的 dataclass 重写。
# 要求：
#   1. 用 @dataclass 存配置（总行数、分隔符、填充符）
#   2. 用 @property 暴露计算结果（不用每次重新生成）
#   3. 用 __str__ 返回格式化的三角形字符串

print("\n\n" + "=" * 50)
print("综合练习：杨辉三角 OOP 版")
print("=" * 50)


@dataclass
class YanghuiConfig:
    """杨辉三角的配置"""
    total: int = 10           # 总行数（0 到 total）
    separator: str = " "      # 数字间分隔符
    pad_char: str = " "       # 居中填充符


class YanghuiTriangle:
    """
    <TODO>: 完成这个类
    1. 用 YanghuiConfig 存配置
    2. 生成杨辉三角（递推公式 C(i,j) = C(i-1,j-1) + C(i-1,j)）
    3. 用 @property 缓存
    4. 用 __str__ 格式化输出
    """

    def __init__(self, config: YanghuiConfig | None = None):
        self.config = config or YanghuiConfig()
        self._triangle: list[list[int]] | None = None  # 缓存

    # --- 核心算法 ---
    def _generate(self) -> list[list[int]]:
        """生成杨辉三角（内部方法，只被 property 调一次）"""
        n = self.config.total
        result: list[list[int]] = []
        for i in range(n + 1):
            row = [1] * (i + 1)
            for j in range(1, i):
                row[j] = result[i - 1][j - 1] + result[i - 1][j]
            result.append(row)
        return result

    # --- 对外接口 ---
    @property
    def triangle(self) -> list[list[int]]:
        """惰性计算：第一次访问才生成，之后直接返回缓存"""
        if self._triangle is None:
            self._triangle = self._generate()
        return self._triangle

    def row(self, n: int) -> list[int]:
        """获取第 n 行"""
        return self.triangle[n]

    # --- 格式化 ---
    def __str__(self) -> str:
        """格式化的三角形字符串"""
        sep = self.config.separator
        pad = self.config.pad_char
        # 算最大数字的宽度，用于对齐
        max_num = max(self.triangle[-1])
        width = len(str(max_num))

        lines = []
        for row in self.triangle:
            # 每个数字占 width 位，用 sep 分隔
            line = sep.join(f"{x:^{width}}" for x in row)
            lines.append(line)

        # 居中整个三角形
        max_line_len = len(lines[-1])
        centered = [line.center(max_line_len, pad) for line in lines]

        return "\n".join(centered)

    def __repr__(self) -> str:
        return f"YanghuiTriangle(total={self.config.total})"

    def __call__(self, n: int) -> list[int]:
        """yt(5) = 第 5 行"""
        return self.row(n)


# --- 测试 ---
yt = YanghuiTriangle(YanghuiConfig(total=8, separator="  "))
print(yt)
print(f"\n第 5 行: {yt(5)}")
print(f"第 8 行: {yt(8)}")
print(f"\n{yt!r}")

# 验证缓存：第二次调用不会重新生成
print(f"\n第二次访问 triangle（用缓存）: {yt.triangle[0]}")

# ============================================================
# 真实代码参考：mini-swe-agent 里的面向对象
# ============================================================

print("\n\n" + "=" * 50)
print("真实代码参考: mini-swe-agent")
print("=" * 50)

print("""
mini-swe-agent 里你能看到今天学的所有概念：

1. @dataclass（AGENTS.md 第8条明确要求）
   AgentConfig 用 Pydantic BaseModel（是 dataclass 的升级版）

2. @property
   虽然没有直接用，但 mini-swe-agent 的风格是
   "方法计算结果当属性暴露"——和你写的 Thermometer 一样

3. __init__ / self
   DefaultAgent.__init__() 接收 model, env, **kwargs
   → 依赖注入（比继承灵活）

4. __str__
   serialize() 方法返回 dict → json.dumps 就是它的"__str__"

再去读一遍 default.py，你至少能认出：
  - config_class: type = AgentConfig  ← 类型注解（Day 1）
  - self.extra_template_vars = {}      ← __init__ 初始化
  - self.messages: list[dict] = []     ← 类型注解
""")

# ============================================================
# Day 3 总结
# ============================================================

print("=" * 50)
print("Day 3 总结")
print("=" * 50)
print("""
  1. @dataclass — 3 行替代 10 行 __init__
     自动生成 __init__ / __repr__ / __eq__
     可变默认值用 field(default_factory=list)

  2. @property — 方法假装是属性
     读: @property → obj.xxx
     写: @xxx.setter → obj.xxx = value（可以加校验！）
     只读: 只写 @property，不写 setter

  3. __str__ vs __repr__
     __str__: 给人看（print）
     __repr__: 给开发者看（交互式环境），最好能 eval 回来

  4. __call__ — 让实例当函数用
     场景：有状态的函数（配置 + 行为一体）

  5. mini-swe-agent 里到处是这些模式
     AgentConfig = 配置 dataclass
     DefaultAgent = __init__ + 状态管理
""")
