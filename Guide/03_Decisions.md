# Step 3: Making Decisions (Jodi / Naile)

Computers are smart because they can make decisions based on rules. In Tacx.IR, we use **`Jodi`** (If) and **`Naile`** (Otherwise/Else).

## The "Jodi" Block

A decision looks like this:

```tacx
Rakho $taka = 50;

Jodi $taka > 30 {
    Bolo "Ami biryani khabo!";
}
```

If `$taka` is more than 30, the computer will print the message. If it's less, the computer will do nothing.

## The "Naile" Block

What if you want the computer to do something else if the condition is false?

```tacx
Rakho $taka = 20;

Jodi $taka > 30 {
    Bolo "Biryani khabo!";
} Naile {
    Bolo "Chai-shingara khabo!";
}
```

Since 20 is NOT more than 30, the computer skips the first part and does the `Naile` part. It will say **"Chai-shingara khabo!"**.

## Multiple Decisions

You can nest them to check many things:

```tacx
Rakho $marks = 85;

Jodi $marks >= 80 {
    Bolo "Apni A+ paisen!";
} Naile {
    Jodi $marks >= 40 {
        Bolo "Apni pass korsen!";
    } Naile {
        Bolo "Fail! Aro porun.";
    }
}
```

## Summary

1. **`Jodi`** starts the decision.
2. The condition (like `$marks >= 80`) goes after it.
3. The instructions go inside the curly brackets `{ }`.
4. **`Naile`** is what happens if the condition is not true.

---

**Next Step:** [04_Loops.md](./04_Loops.md)