# Step 3: Making Decisions (jodi / naile)

Computers are smart because they can make decisions based on rules. In Tacx.IR, we use **`jodi`** (If) and **`naile`** (Otherwise/Else).

## The "jodi" Block

A decision looks like this:

```tacx
rakho $taka = 50;

jodi $taka > 30 {
    bolo "Ami biryani khabo!";
}
```

If `$taka` is more than 30, the computer will print the message. If it's less, the computer will do nothing.

## The "naile" Block

What if you want the computer to do something else if the condition is false?

```tacx
rakho $taka = 20;

jodi $taka > 30 {
    bolo "Biryani khabo!";
} naile {
    bolo "Chai-shingara khabo!";
}
```

Since 20 is NOT more than 30, the computer skips the first part and does the `naile` part. It will say **"Chai-shingara khabo!"**.

## Multiple Decisions

You can nest them to check many things:

```tacx
rakho $marks = 85;

jodi $marks >= 80 {
    bolo "Apni A+ paisen!";
} naile {
    jodi $marks >= 40 {
        bolo "Apni pass korsen!";
    } naile {
        bolo "Fail! Aro porun.";
    }
}
```

## Summary

1. **`jodi`** starts the decision.
2. The condition (like `$marks >= 80`) goes after it.
3. The instructions go inside the curly brackets `{ }`.
4. **`naile`** is what happens if the condition is not true.

---

**Next Step:** [04_Loops.md](./04_Loops.md)
