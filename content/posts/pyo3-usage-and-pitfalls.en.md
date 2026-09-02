+++
title = "PyO3 Usage and Pitfalls"
date = 2026-08-31T00:00:00+08:00
slug = "pyo3-usage-and-pitfalls-en"
[taxonomies]
    tags = ["Rust", "Python", "PyO3", "Language Bindings"]
+++

PyO3 connects Rust and Python. It supports several patterns: exposing Rust functions, structs, and modules to Python; retaining Python objects in Rust; and converting Python-created objects into Rust types so existing Rust business logic can be reused.

---

## 1. Expose a Rust Function to Python

The simplest approach is to mark a function with `#[pyfunction]` and register it in a `#[pymodule]`.

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

Python can call it directly:

```python
import calc

assert calc.add(2, 3) == 5
```

This approach fits calculation functions, utility functions, and performance-sensitive code.

## 2. Expose a Rust Struct as a Python Class

`#[pyclass]` defines a class visible to Python, while `#[pymethods]` exposes its constructor, methods, and properties.

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

Python usage:

```python
counter = calc.Counter()
counter.increment()
assert counter.value == 1
```

This approach fits objects whose Rust state must survive across multiple Python calls.

## 3. Pass Data Between Rust and Python

PyO3 can automatically convert many common types. For example, a Python dictionary can be extracted into a Rust `HashMap<String, f64>`:

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

`extract()` creates Rust-owned data. If the object only needs to be read during the current call, use `Bound<'py, T>` directly instead of converting the entire object into a Rust container first.

A simple rule:

- Convert to a Rust type when the data must outlive the Python call or be processed as Rust-owned data;
- Prefer borrowing with `Bound<'py, T>` when the object is only read during the current call.

## 4. Store a Python Object in Rust

The following three types are easy to confuse:

| Type | Meaning | Typical use |
|------|---------|-------------|
| `Python<'py>` | Proof that the current thread may access the Python interpreter | Calling Python APIs and binding `Py<T>` |
| `Bound<'py, T>` | An object reference bound to the current Python context | Reading or calling a Python object during the current call |
| `Py<T>` | A smart pointer holding a Python object reference without being tied to the current `'py` lifetime | Storing a Python object in a Rust struct for later use |

For example, Rust may need to store a Python callback and call it later when an event occurs:

```rust
#[pyclass]
struct Worker {
    callback: Py<PyAny>,
}
```

Bind it to the current Python context when calling it:

```rust
fn call(&self, py: Python<'_>) -> PyResult<()> {
    self.callback.bind(py).call0()?;
    Ok(())
}
```

`Py<T>` is not the Python interpreter itself, and Rust does not take ownership of the Python object's data. Rust holds a reference to an object managed by the Python interpreter.

For temporary access during the current call, use a bound reference instead:

```rust
fn read_data(data: &Bound<'_, PyDict>) -> usize {
    data.len()
}
```

## 5. Let Python Provide the Business Logic Required by a Rust Trait

Rust can define a trait and the surrounding business flow while letting a Python object provide the concrete implementation. A Rust wrapper stores a reference to the Python object and implements the Rust trait; when the trait method is called, the wrapper forwards the call to the Python object's method.

In this example, Rust defines the `Model` trait and the generic `solve_model()` function. Python defines `UserModel` and provides its `compute()` logic.

```python
class UserModel:
    def compute(self, value):
        return value * 2

model = UserModel()
assert calc.solve(model, 10.0) == 20.0
```

When Python calls `calc.solve()`, `model` is a `UserModel` instance. The Rust function exposed to Python receives that object and stores it in a wrapper:

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

The complete call chain is:

```text
Python creates a UserModel instance
    → Python calls calc.solve(model, 10.0)
    → PyO3 receives model as solve_wrapper's Py<PyAny> parameter
    → Rust creates UserModelWrapper and stores the Python object reference
    → solve_model() calls wrapper.compute() through the Model trait
    → wrapper.bind(py) obtains a Bound<'py, PyAny> for the current context
    → call_method1("compute", (10.0,)) calls Python's model.compute(10.0)
    → Python returns 20.0
    → extract() converts the result to Rust f64
    → solve_wrapper returns PyResult<f64>
    → Python receives 20.0
```

`UserModel` is not converted into an equivalent Rust struct. `UserModelWrapper` is only an adapter: it satisfies Rust's trait constraint, while the concrete `compute()` logic remains in Python.

## 6. Convert a Python Object Structure into Rust Types and Use Existing Rust Trait Implementations

Python objects cannot directly become a Rust `Box<dyn Evaluatable>`. When Python constructs the object structure while Rust already has the trait-based business logic, use three layers:

- **Native Rust types**: implement the trait and contain the business logic;
- **PyO3 wrapper types**: register Python classes so Python can construct the object structure;
- **Conversion function**: recursively traverse the Python object tree and rebuild the Rust trait-object tree.

The call chain is:

```text
Python constructs a PyAdd, PyVar, and PyConst object tree
    → Python calls the expression object's evaluate()
    → Rust receives the Python object tree
    → to_evaluatable() checks concrete types and recursively reads objects
    → PyAdd, PyVar, and PyConst become AddExpr, VarExpr, and ConstExpr
    → a native Rust expression tree is formed
    → the existing Evaluatable::evaluate() implementation runs
    → the result is returned to Python
```

Two different conversion operations appear here: `vars.extract()` is a PyO3-provided object method; `to_evaluatable(py, obj)` is an ordinary function defined in this example that recursively converts the expression tree.

### 1. Rust Trait and Native Types

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

> **Example note**: `Send + Sync` here is a concurrency constraint declared by the `Evaluatable` business trait itself. It is not a general PyO3 requirement. Keep it only if these expression objects must be safely sent between or shared across threads.

### 2. PyO3 Wrapper Types and the Conversion Bridge

The wrapper types are registered as Python classes. The conversion function checks concrete types and recursively builds a Rust object tree:

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

Python can build and evaluate an expression:

```python
import calc

x = calc.Var("x")
y = calc.Var("y")
expr = calc.Add(calc.Add(x, calc.Const(3.14)), y)

assert expr.evaluate({"x": 10.0, "y": 5.0}) == 18.14
```

This does not expose the Rust trait directly to Python. Instead, Python wrapper types form the interface, and the conversion step produces Rust objects implementing the trait.

The official PyO3 Trait Bounds tutorial addresses a different problem: a Rust wrapper holding a Python object implements an existing Rust trait, and that wrapper is passed to a generic function with a trait bound. It does not discuss recursively rebuilding a `Box<dyn Trait>` object tree as in this example.

## 7. Common Pitfalls

### 1. Do Not Confuse `Py<T>` with `Bound<'py, T>`

- Use `Py<T>` when Rust must retain a Python object for later reads or calls;
- Use `Bound<'py, T>` when the object is accessed only within the current Python context;
- When accessing a `Py<T>`, call `bind(py)` first to obtain `Bound<'py, T>`.

Confusing these types can lead to attempts to store a temporary `Bound<'py, T>` in a long-lived Rust struct, or to access `Py<T>` without first calling `bind(py)`.

### 2. Map Python Exceptions at the Boundary

If the Rust business layer returns `Result<T, String>`, map the error at the boundary to a specific Python exception such as `PyValueError`, `PyTypeError`, or `PyRuntimeError`.

### 3. Choose Conversion Logic by Actual Type

When Rust receives a parameter of type `Py<PyAny>`, it must determine at runtime which kind of Python object it is. Do not inspect strings such as `__class__.__name__`: an ordinary Python class can use the same name.

If only known `#[pyclass]` types are accepted, use `downcast::<PyConst>()`, `downcast::<PyVar>()`, and similar checks to inspect the object's actual PyO3 type and apply the corresponding conversion logic. Return `PyTypeError` only after all supported type checks fail.

### 4. Binding and Packaging Are Separate Concerns

PyO3 provides the Rust/Python bindings. Building the extension as an installable Python package usually also requires a packaging tool such as `maturin`. The module name, Cargo configuration, and Python package layout must agree.

## References

- [PyO3 User Guide](https://pyo3.rs/v0.23.5/)
- [PyO3 Bound API](https://pyo3.rs/main/doc/pyo3/struct.Bound)
- [PyO3 Trait Bounds Tutorial](https://pyo3.rs/v0.23.5/trait-bounds)
- [PyO3 docs.rs](https://docs.rs/pyo3/0.23.5/pyo3/)
- [maturin documentation](https://www.maturin.rs/)
- [Rust Trait Objects](https://doc.rust-lang.org/reference/types/trait-object.html)
