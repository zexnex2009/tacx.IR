# Step 2: Math and Text

Now that we know how to save information, let's do something with it!

## Basic Math

Tacx.IR can do math just like a calculator:

*   `+` (Jog / Plus)
*   `-` (Biyog / Minus)
*   `*` (Gun / Multiply)
*   `/` (Bhag / Divide)

```tacx
rakho $taka = 100 + 50;
bolo $taka; // This will say 150
```

You can even use variables in your math:

```tacx
rakho $egg_price = 12;
rakho $quantity = 4;
rakho $total = $egg_price * $quantity;
bolo $total; // This will say 48
```

## Mixing Text (Concatenation)

You can also join pieces of text together using the `+` sign.

```tacx
rakho $name = "Zex";
bolo "Hello " + $name; // This will say: Hello Zex
```

You can even join text and numbers:

```tacx
rakho $score = 100;
bolo "Your score is: " + $score; // This will say: Your score is: 100
```

## Comparisons

Sometimes you want to compare two things to see if they are the same or which one is bigger. This gives you a `sotyo` (True) or `mithya` (False) answer.

*   `==` (Is it equal?)
*   `!=` (Is it NOT equal?)
*   `>` (Is it greater?)
*   `<` (Is it smaller?)

```tacx
bolo 10 > 5;  // Says: sotyo
bolo 10 == 5; // Says: mithya
```

---
**Next Step:** [03_Decisions.md](./03_Decisions.md)
