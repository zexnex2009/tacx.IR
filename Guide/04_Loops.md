# Step 4: Repeating Tasks (Loops)

Computers are great at doing the same thing over and over again without getting tired. We call this a **Loop**.

## 1. Repeating a fixed number of times (`Cholao`)

If you know exactly how many times you want to do something, use **`Cholao`** (Run/Drive) ... **`bar`** (times).

```tacx
Cholao 5 bar {
    Bolo "Ami bhat khabo";
}
```

This will print "Ami bhat khabo" 5 times.

## 2. Repeating while something is true (`Jotokhon`)

Sometimes you want to keep going **`Jotokhon`** (As long as) a condition is true.

```tacx
Rakho $count = 1;

Jotokhon $count <= 5 {
    Bolo "Count is: " + $count;
    Rakho $count = $count + 1; // Increase the count by 1
}
```

**How it works:**
1.  Check if `$count` is less than or equal to 5.
2.  If yes, run the code inside.
3.  Update `$count` so it's now 2.
4.  Go back to step 1.
5.  When `$count` becomes 6, it stops because 6 is not `<=` 5.

## Stopping or Skipping

*   **`Thamo`** (Stop/Break): Immediately stops the loop.
*   **`Chalano`** (Continue): Skips the rest of the current turn and starts the next turn of the loop.

```tacx
Rakho $i = 1;
Jotokhon $i < 10 {
    Jodi $i == 5 {
        Thamo; // Stop when i is 5
    }
    Bolo $i;
    Rakho $i = $i + 1;
}
```

---
**Next Step:** [05_Functions.md](./05_Functions.md)
