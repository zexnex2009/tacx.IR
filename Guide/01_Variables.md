# Step 1: Variables (Saving Information)

In programming, a **Variable** is like a box. You can put a value inside it, give the box a name, and then use that name later to get the value back.

## How to create a Variable

In Tacx.IR, we use the word **`Rakho`** (Keep/Put) to save something into a variable. 

Variable names in Tacx.IR always start with a dollar sign (**`$`**).

```tacx
Rakho $naam = "Anis";
Rakho $boyosh = 20;
```

In the code above:
*   We "kept" the text `"Anis"` in a box called `$naam`.
*   We "kept" the number `20` in a box called `$boyosh`.

## Showing the value

To see what's inside a variable, we use **`Bolo`** (Say/Tell).

```tacx
Bolo $naam;
```
The computer will look inside the box `$naam` and print **Anis**.

## Different types of "Stuff"

You can put different things in your boxes:

1.  **Numbers**: `10`, `3.5`, `-5`
2.  **Text (Strings)**: Always put these in quotes, like `"Hello"`.
3.  **Yes/No (Booleans)**: 
    *   **`Sotyo`** (True/Correct)
    *   **`Mithya`** (False/Incorrect)

## Try it out!

Try writing this in a file:

```tacx
Rakho $am = 5;
Rakho $jam = 10;
Bolo $am;
Bolo $jam;
```

When you run this, the computer will tell you `5` and then `10`.

---
**Next Step:** [02_Math_and_Text.md](./02_Math_and_Text.md)
