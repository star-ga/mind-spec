# Control Flow

MIND provides standard control flow primitives similar to Rust and C-family languages.

## If Expressions

`if` is an expression in MIND, meaning it returns a value.

```rust
let x = 5;
let y = if x > 0 {
    1
} else {
    -1
};
```

## Loops

### `loop`
Infinite loop. Use `break` to exit.

```rust
let mut i = 0;
loop {
    i += 1;
    if i == 10 {
        break;
    }
}
```

### `while`
Conditional loop.

```rust
while x > 0 {
    x -= 1;
}
```

### `for`
Iterator loop.

```rust
for i in 0..10 {
    print!("{}", i);
}
```

## Pattern Matching

`match` allows for powerful control flow based on patterns.

```rust
let x = 1;
match x {
    1 => print!("One"),
    2 => print!("Two"),
    _ => print!("Other"),
}
```
