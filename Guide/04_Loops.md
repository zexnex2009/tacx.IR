# Step 4: Repeating Tasks (Loops)

Computers are great at doing the same thing over and over again without getting tired. We call this a **Loop**.

## 1. Repeating a fixed number of times (`kor`)

If you know exactly how many times you want to do something, use **`kor`** (Run/Drive/Do) ... **`bar`** (times).

```tacx
kor 5 bar {
    bolo "Ami bhat khabo";
}
```

This will print "Ami bhat khabo" 5 times.

## 2. Repeating while something is true (`jtkhn`)

Sometimes you want to keep going **`jtkhn`** (As long as) a condition is true.

```tacx
rakho $count = 1;

jtkhn $count <= 5 {
    bolo "Count is: " + $count;
    rakho $count = $count + 1; // Increase the count by 1
}
```

**How it works:**
1.  Check if `$count` is less than or equal to 5.
2.  If yes, run the code inside.
3.  Update `$count` so it's now 2.
4.  Go back to step 1.
5.  When `$count` becomes 6, it stops because 6 is not `<=` 5.

## Stopping or Skipping

*   **`tham`** (Stop/Break): Immediately stops the loop.
*   **`chal`** (Continue): Skips the rest of the current turn and starts the next turn of the loop.

```tacx
rakho $i = 1;
jtkhn $i < 10 {
    jodi $i == 5 {
        tham; // Stop when i is 5
    }
    bolo $i;
    rakho $i = $i + 1;
}
```

---
**Next Step:** [05_Functions.md](./05_Functions.md)
