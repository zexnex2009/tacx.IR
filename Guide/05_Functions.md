# Step 5: Functions (Recipes)

A **Function** is like a recipe. You give it a name and a set of instructions. Later, you can just call the name to run all those instructions at once.

## Creating a Function (`dhori`)

In Tacx.IR, we use **`dhori`** (Let's assume/Define) to make a function.

```tacx
dhori baniye_bolo(naam) {
    bolo "Hello " + naam + ", kemon achen?";
}
```

In this example:
*   The name is `baniye_bolo`.
*   It takes one input called `naam` (this is called a **parameter**).

## Using the Function

To use it, just type its name with parentheses `( )`:

```tacx
baniye_bolo("Sagor");
baniye_bolo("Anika");
```

## Giving back a value (`dao`)

Sometimes a function does a calculation and needs to give the answer back to you. We use **`dao`** (Return/Give).

```tacx
dhori jog_koro(a, b) {
    dao a + b;
}

rakho $result = jog_koro(10, 20);
bolo $result; // Says 30
```

## Why use functions?

1.  **Don't repeat yourself**: Write the code once, use it 100 times.
2.  **Organization**: Keep your code clean by grouping tasks together.
3.  **Readability**: It's easier to read `calculate_salary()` than a long mess of math.

---
## Congratulations! 🎉

You have learned the basics of Tacx.IR. You are now a programmer! 

Try creating your own file (like `my_code.tacx`) and run it using:
`python tacxIR.py my_code.tacx`
