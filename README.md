# ❄ Snowflake

Two little Christmas surprises made with code:

- **`snowflake.py`**: a spinning 3D snowflake that runs right in your terminal. It's white, with tips that fade into icy blue.
- **`crush.html`**: a page that "runs" a fake program, shows a spinning snowflake, and asks *"will you be my snowflake this christmas?"* Good luck pressing **no** 😌

---

## 🌐 crush.html (the easiest one)

### Just want to see it?

1. Click **`crush.html`** in the file list above.
2. Click the **download** button (the ⬇ icon at the top right of the file).
3. Find the file in your Downloads folder and **double-click it**. It opens in your browser.

That's it. No installing anything.

### Make it personal

Add these to the end of the page's address in your browser bar, then press Enter:

| Add this | What it does |
|---|---|
| `?to=Alex` | Says "hi Alex :)" and names the file `for_alex.py` |
| `?q=be my valentine?` | Changes the question |
| `?to=Alex&q=be my valentine?` | Does both |

Example: `crush.html?to=Alex`

---

## 💻 snowflake.py (runs in your terminal)

You need **Python 3**. It's already on most Macs. To check, open Terminal and type `python3 --version`.

### Download it

**Option A: no Git needed**

1. Click **`snowflake.py`** above, then the **download** button (⬇).
2. Open **Terminal** (Mac: press Cmd + Space and type "Terminal"; Windows: open "Command Prompt").
3. Go to your Downloads folder and run it:

```bash
cd ~/Downloads
python3 snowflake.py
```

On Windows, use `cd Downloads` and `python snowflake.py`.

**Option B: with Git**

```bash
git clone https://github.com/gurjevanbhatti/Snowflake.git
cd Snowflake
python3 snowflake.py
```

### Make it personal

```bash
python3 snowflake.py --to "Alex"
```

This shows **"Merry Christmas, Alex ❄"** under the snowflake.

### Tips

- Press **Ctrl + C** to stop it.
- Zoom your terminal **out** (Cmd + minus, or Ctrl + minus) and make the window bigger for a sharper snowflake.
- Colours look best in a dark terminal.

---

Made by [@gurjevanbhatti](https://github.com/gurjevanbhatti) ❄
