+++
title = "PyO3 用法与踩坑"
date = 2026-08-31T00:00:00+08:00
slug = "pyo3-usage-and-pitfalls"
[taxonomies]
    tags = ["Rust", "Python", "PyO3", "跨语言绑定"]
+++

PyO3 用来连接 Rust 与 Python。常见做法不是只有一种：可以把 Rust 函数、结构体和模块暴露给 Python，也可以让 Rust 持有 Python 对象；还可以把 Python 创建的对象转换为 Rust 类型，继续使用已有的 Rust 业务逻辑。

---

## 一、把 Rust 函数暴露给 Python

最简单的用法是通过 `#[pyfunction]` 导出普通函数，再在 `#[pymodule]` 中注册。

```rust
use pyo3::prelude::*;

#[pyfunction]
fn add(left: i64, right: i64) -> i64 {
    left + right
}

#[pymodule]
fn calc(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(add, m)?)?;
    Ok(())
}
```

Python 侧可以直接调用：

```python
import calc

assert calc.add(2, 3) == 5
```

这种方式适合计算函数、工具函数和性能热点。

## 二、把 Rust 结构体暴露为 Python 类

`#[pyclass]` 定义 Python 可见的类，`#[pymethods]` 暴露构造函数、方法和属性。

```rust
use pyo3::prelude::*;

#[pyclass]
struct Counter {
    #[pyo3(get)]
    value: i64,
}

#[pymethods]
impl Counter {
    #[new]
    fn new() -> Self {
        Self { value: 0 }
    }

    fn increment(&mut self) {
        self.value += 1;
    }
}
```

Python 侧：

```python
counter = calc.Counter()
counter.increment()
assert counter.value == 1
```

这种方式适合需要在多次 Python 调用之间保留 Rust 状态的对象。

## 三、将 Python 数据转换为 Rust 类型

PyO3 可以自动转换许多常见类型。例如，可以把 Python 字典提取为 Rust 的 `HashMap<String, f64>`：

```rust
use std::collections::HashMap;
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[pyfunction]
fn sum_values(values: &Bound<'_, PyDict>) -> PyResult<f64> {
    let values: HashMap<String, f64> = values.extract()?;
    Ok(values.values().sum())
}
```

`extract()` 会创建 Rust 拥有的数据。如果只需要在当前调用中读取 Python 对象，可以直接使用 `Bound<'py, T>`，不必先把整个对象转换成 Rust 容器。

简单判断：

- 需要脱离 Python 生命周期保存或处理数据时，提取为 Rust 类型；
- 只在当前调用中读取对象时，优先借用 `Bound<'py, T>`。

## 四、在 Rust 中保存 Python 对象

下面三个类型容易混淆：

| 类型 | 含义 | 典型用途 |
|------|------|----------|
| `Python<'py>` | 当前线程可以访问 Python 解释器的凭证 | 调用 Python API、绑定 `Py<T>` |
| `Bound<'py, T>` | 绑定到当前 Python 上下文的对象引用 | 当前调用中读取或调用 Python 对象 |
| `Py<T>` | 持有 Python 对象引用、但不绑定当前 `'py` 生命周期的智能指针 | 在 Rust 结构体中保存 Python 对象，供以后使用 |

例如，Rust 结构体需要保存 Python 回调，等以后发生事件时再调用：

```rust
#[pyclass]
struct Worker {
    callback: Py<PyAny>,
}
```

调用时再绑定到当前 Python 上下文：

```rust
fn call(&self, py: Python<'_>) -> PyResult<()> {
    self.callback.bind(py).call0()?;
    Ok(())
}
```

这里的 `Py<T>` 不是 Python 解释器本身，也不是 Rust 获得了 Python 对象数据的所有权，而是 Rust 持有一个由 Python 解释器管理的对象引用。

如果只需要当前调用中的临时访问，则使用：

```rust
fn read_data(data: &Bound<'_, PyDict>) -> usize {
    data.len()
}
```

## 五、让 Python 提供 Rust Trait 所需的业务逻辑

Rust 可以定义 Trait 和业务流程，但让 Python 对象提供具体实现。此时，Rust wrapper 保存 Python 对象的引用，并实现 Rust 所需的 Trait；Trait 方法被调用时，wrapper 再把调用转发给 Python 对象的方法。

下面的例子中，Rust 定义 `Model` Trait 和泛型函数 `solve()`，Python 定义 `UserModel` 并实现具体的 `compute()` 逻辑。

```python
class UserModel:
    def compute(self, value):
        return value * 2

model = UserModel()
assert calc.solve(model, 10.0) == 20.0
```

Python 调用 `calc.solve()` 时，传入的 `model` 是一个 `UserModel` 实例。Rust 对外暴露的函数接收这个对象，并将它保存到 wrapper 中：

```rust
use pyo3::prelude::*;

trait Model {
    fn compute(&self, py: Python<'_>, value: f64) -> PyResult<f64>;
}

struct UserModelWrapper {
    model: Py<PyAny>,
}

impl Model for UserModelWrapper {
    fn compute(&self, py: Python<'_>, value: f64) -> PyResult<f64> {
        self.model
            .bind(py)
            .call_method1("compute", (value,))?
            .extract()
    }
}

fn solve_model<M: Model>(py: Python<'_>, model: &M, value: f64) -> PyResult<f64> {
    model.compute(py, value)
}

#[pyfunction(name = "solve")]
fn solve_wrapper(py: Python<'_>, model: Py<PyAny>, value: f64) -> PyResult<f64> {
    let wrapper = UserModelWrapper { model };
    solve_model(py, &wrapper, value)
}

#[pymodule]
fn calc(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve_wrapper, m)?)?;
    Ok(())
}
```

完整调用链是：

```text
Python 创建 UserModel 实例
    → Python 调用 calc.solve(model, 10.0)
    → PyO3 将 model 接收到 solve_wrapper 的 Py<PyAny> 参数
    → Rust 创建 UserModelWrapper，并保存 Python 对象的引用
    → solve_model() 按 Model Trait 调用 wrapper.compute()
    → wrapper.bind(py) 获得当前调用中的 Bound<'py, PyAny>
    → call_method1("compute", (10.0,)) 调用 Python 的 model.compute(10.0)
    → Python 返回 20.0
    → extract() 将返回值转换为 Rust 的 f64
    → solve_wrapper 返回 PyResult<f64>
    → Python 得到 20.0
```

这里没有把 `UserModel` 转换为等价的 Rust 结构体。`UserModelWrapper` 只是一个代理：Rust 通过它满足自己的 Trait 约束，但具体的 `compute()` 逻辑仍由 Python 执行。

## 六、将 Python 对象结构转换为 Rust 类型，使用已有的 Rust Trait 实现

Python 对象不能直接变成 Rust 的 `Box<dyn Evaluatable>`。当 Python 负责组合对象，而 Rust 已有一套 trait 业务逻辑时，可以使用三层结构：

- **Rust 原生类型**：实现 Trait，负责业务逻辑；
- **PyO3 包装类型**：注册为 Python 类，负责让 Python 构造对象结构；
- **转换函数**：遍历 Python 对象树，重建 Rust trait object 树。

调用链如下：

```text
Python 构造 PyAdd、PyVar、PyConst 对象树
    → Python 调用表达式对象的 evaluate()
    → Rust 接收 Python 对象树
    → to_evaluatable() 按具体类型递归读取对象
    → PyAdd、PyVar、PyConst 转换为 AddExpr、VarExpr、ConstExpr
    → 形成 Rust 原生表达式树
    → 调用已有的 Evaluatable::evaluate()
    → 结果返回 Python
```

这里同时出现两个不同层次的转换操作：`vars.extract()` 是 PyO3 提供的对象方法；`to_evaluatable(py, obj)` 是本文定义的普通函数，负责按表达式树规则递归转换对象。

### 1. Rust Trait 与原生类型

```rust
use std::collections::HashMap;

pub trait Evaluatable: Send + Sync {
    fn evaluate(&self, vars: &HashMap<String, f64>) -> Result<f64, String>;
}

pub struct ConstExpr {
    pub value: f64,
}

pub struct VarExpr {
    pub name: String,
}

pub struct AddExpr {
    pub left: Box<dyn Evaluatable>,
    pub right: Box<dyn Evaluatable>,
}

impl Evaluatable for ConstExpr {
    fn evaluate(&self, _: &HashMap<String, f64>) -> Result<f64, String> {
        Ok(self.value)
    }
}

impl Evaluatable for VarExpr {
    fn evaluate(&self, vars: &HashMap<String, f64>) -> Result<f64, String> {
        vars.get(&self.name)
            .copied()
            .ok_or_else(|| format!("Undefined: {}", self.name))
    }
}

impl Evaluatable for AddExpr {
    fn evaluate(&self, vars: &HashMap<String, f64>) -> Result<f64, String> {
        Ok(self.left.evaluate(vars)? + self.right.evaluate(vars)?)
    }
}
```

> **示例说明**：这里的 `Send + Sync` 是 `Evaluatable` 这个业务 trait 自己声明的并发约束，不是 PyO3 的通用要求。只有当这些表达式对象需要在线程之间安全传递或共享时，才需要保留它。

### 2. PyO3 包装类型与转换桥

包装类型注册为 Python 类，转换函数则按具体类型检查对象并递归构建 Rust 对象树：

```rust
use pyo3::exceptions::{PyRuntimeError, PyTypeError};
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[pyclass(name = "Const")]
pub struct PyConst {
    #[pyo3(get)]
    pub value: f64,
}

#[pymethods]
impl PyConst {
    #[new]
    fn new(value: f64) -> Self {
        Self { value }
    }
}

#[pyclass(name = "Var")]
pub struct PyVar {
    #[pyo3(get)]
    pub name: String,
}

#[pymethods]
impl PyVar {
    #[new]
    fn new(name: &str) -> Self {
        Self { name: name.into() }
    }
}

#[pyclass(name = "Add")]
pub struct PyAdd {
    #[pyo3(get)]
    pub left: Py<PyAny>,
    #[pyo3(get)]
    pub right: Py<PyAny>,
}

#[pymethods]
impl PyAdd {
    #[new]
    fn new(left: Py<PyAny>, right: Py<PyAny>) -> Self {
        Self { left, right }
    }

    fn evaluate(&self, py: Python<'_>, vars: &Bound<'_, PyDict>) -> PyResult<f64> {
        let vars: HashMap<String, f64> = vars.extract()?;
        AddExpr {
            left: to_evaluatable(py, &self.left)?,
            right: to_evaluatable(py, &self.right)?,
        }
        .evaluate(&vars)
        .map_err(PyRuntimeError::new_err)
    }
}

fn to_evaluatable(py: Python<'_>, obj: &Py<PyAny>) -> PyResult<Box<dyn Evaluatable>> {
    let obj = obj.bind(py);

    if let Ok(value) = obj.downcast::<PyConst>() {
        return Ok(Box::new(ConstExpr {
            value: value.borrow().value,
        }));
    }

    if let Ok(value) = obj.downcast::<PyVar>() {
        return Ok(Box::new(VarExpr {
            name: value.borrow().name.clone(),
        }));
    }

    if let Ok(value) = obj.downcast::<PyAdd>() {
        let value = value.borrow();
        return Ok(Box::new(AddExpr {
            left: to_evaluatable(py, &value.left)?,
            right: to_evaluatable(py, &value.right)?,
        }));
    }

    Err(PyTypeError::new_err("Expected Const, Var, or Add"))
}
```

Python 侧构造表达式并求值：

```python
import calc

x = calc.Var("x")
y = calc.Var("y")
expr = calc.Add(calc.Add(x, calc.Const(3.14)), y)

assert expr.evaluate({"x": 10.0, "y": 5.0}) == 18.14
```

这不是把 Rust trait 直接暴露给 Python，而是让 Python 包装类型充当接口，再转换成实现该 trait 的 Rust 对象。

PyO3 官方 Trait Bounds 教程解决的是另一类问题：让一个持有 Python 对象的 Rust wrapper 实现既有 Rust trait，再把这个 wrapper 传给带 trait bound 的泛型函数。它不讨论本文这种递归重建 `Box<dyn Trait>` 对象树的方案。

## 七、常见坑点

### 1. 不要混淆 `Py<T>` 与 `Bound<'py, T>`

- 需要让 Rust 保存一个 Python 对象，供以后再次读取或调用时，使用 `Py<T>`；
- 已经处于 Python 上下文、只需当前访问时使用 `Bound<'py, T>`；
- 从 `Py<T>` 访问对象时，先通过 `bind(py)` 获得 `Bound<'py, T>`。

混淆这两种类型时，常见后果是：试图把带有临时生命周期的 `Bound<'py, T>` 保存到长期存在的 Rust 结构体，或者忘记先调用 `bind(py)` 就直接访问 `Py<T>`。

### 2. Python 异常需要映射

Rust 业务层若返回 `Result<T, String>`，不能直接成为理想的 Python 异常。应在边界处把错误映射为 `PyValueError`、`PyTypeError`、`PyRuntimeError` 等具体异常。

### 3. 根据实际类型选择转换逻辑

当 Rust 收到的参数类型是 `Py<PyAny>` 时，需要在运行时判断它具体是哪一种 Python 对象。不要通过读取 `__class__.__name__` 等类名字符串来判断，因为普通 Python 类也可能使用相同的名字。

如果只接受已知的 `#[pyclass]` 类型，应使用 `downcast::<PyConst>()`、`downcast::<PyVar>()` 等方式检查对象的实际 PyO3 类型，并为每种类型执行对应的转换逻辑。所有检查都失败时，再返回 `PyTypeError`。

### 4. 绑定代码与打包是两件事

PyO3 负责 Rust/Python 绑定；要把扩展模块构建成 Python 可安装的软件包，通常还需要 `maturin` 等构建工具。模块名、Cargo 配置和 Python 包布局必须保持一致。

## 参考链接

- [PyO3 官方文档](https://pyo3.rs)
- [PyO3 用户指南](https://pyo3.rs/v0.23.5/)
- [PyO3 Bound API](https://pyo3.rs/main/doc/pyo3/struct.Bound)
- [PyO3 Trait Bounds 教程](https://pyo3.rs/v0.23.5/trait-bounds)
- [PyO3 docs.rs](https://docs.rs/pyo3/0.23.5/pyo3/)
- [maturin 官方文档](https://www.maturin.rs/)
- [Rust Trait Object](https://doc.rust-lang.org/reference/types/trait-object.html)
