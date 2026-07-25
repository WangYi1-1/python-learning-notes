# Day 3: 面向对象核心

## 学习内容

### 1. @dataclass — 告别手写 __init__

- 声明字段 → 自动生成 `__init__` / `__eq__` / `__repr__`
- 三行替代十几行手写代码
- 可变默认值必须用 `field(default_factory=list)`，不能用 `= []`
  - 原因：`= []` 所有实例共享同一个 list
  - `default_factory=list` 每次创建新实例时调 `list()`，互不影响
- 适用场景：主要存数据的类（配置、DTO）
- **不适用**：行为/校验/计算属性为主的类（如 Circle、Thermometer）

### 2. @property — 方法假装成属性

- 读：`@property` → `obj.radius` 不用 `obj.get_radius()`
- 写：`@xxx.setter` → `obj.radius = 10` 自动触发校验
- 只读：只写 `@property`，不写 setter
- 惰性计算：第一次访问才计算，之后用缓存
- `@radius.setter` 里的 `radius` 来自 `@property` 生成的 property 对象

### 3. __str__ / __repr__ / __call__（魔法方法）

- `__init__`：创建对象时自动调 → Java 构造函数
- `__eq__`：`==` 比较时自动调 → Java `equals()`
- `__repr__`：`print()` 时自动调 → Java `toString()`
- `__str__`：`str()` 时自动调，给人看的友好版本
- `__call__`：`obj()` 时自动调 → 让实例当函数用

### 4. @ 装饰器串联理解

- Day 1: `@decorator` — 装饰函数
- Day 2: `@contextmanager` — 装饰 generator 变 Context Manager
- Day 3: `@dataclass` — 装饰类，加方法
- Day 3: `@property` — 装饰方法，变属性
- 原理全是：`东西 = 装饰器(东西)`

### 5. 综合练习：杨辉三角 OOP 版

- `@dataclass` 存配置
- `@property` 惰性缓存三角结果
- `__str__` 格式化输出居中对齐的三角形
- `__call__` 支持 `yt(5)` 取第 5 行

## 练习文件

- `learn_python_day3.py` — 可运行的交互式学习脚本
