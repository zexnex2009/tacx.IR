# Step 2: Math and Text

Now that we know how to save information, let's do something with it!

## Basic Math

Tacx.IR can do math just like a calculator:

*   `+` (Jog / Plus)
*   `-` (Biyog / Minus)
*   `*` (Gun / Multiply)
*   `/` (Bhag / Divide)

```tacx
Rakho $taka = 100 + 50;
Bolo $taka; // This will say 150
```

You can even use variables in your math:

```tacx
Rakho $egg_price = 12;
Rakho $quantity = 4;
Rakho $total = $egg_price * $quantity;
Bolo $total; // This will say 48
```

## Mixing Text (Concatenation)

You can also join pieces of text together using the `+` sign.

```tacx
Rakho $name = "Zex";
Bolo "Hello " + $name; // This will say: Hello Zex
```

You can even join text and numbers:

```tacx
Rakho $score = 100;
Bolo "Your score is: " + $score; // This will say: Your score is: 100
```

## Comparisons

Sometimes you want to compare two things to see if they are the same or which one is bigger. This gives you a `Sotyo` (True) or `Mithya` (False) answer.

*   `==` (Is it equal?)
*   `!=` (Is it NOT equal?)
*   `>` (Is it greater?)
*   `<` (Is it smaller?)

```tacx
Bolo 10 > 5;  // Says: Sotyo
Bolo 10 == 5; // Says: Mithya
```

---
**Next Step:** [03_Decisions.md](./03_Decisions.md)
