# Functions

Functions are the building blocks of MIND programs.

## Declaration

Functions are declared using the `fn` keyword.

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

## Parameters and Return Types

Parameters must always have type annotations. The return type is specified after `->`. If omitted, it returns `()`.

## Implicit Return

The last expression in a function body is implicitly returned.

```rust
fn square(x: i32) -> i32 {
    x * x // No semicolon means return
}
```

## Higher-Order Functions

MIND supports passing functions as arguments.

```rust
fn apply(f: fn(i32) -> i32, x: i32) -> i32 {
    f(x)
}
```
