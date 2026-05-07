# 📘 Logistics Agentic AI - System Master Guide (Fresher Edition)

This guide explains how to use our AI-powered tool to process logistics contracts. Even if you are new to logistics, this guide will show you how to transform complex Excel files into clean, ready-to-use data.

---

## 🌟 1. What is this System?
In shipping, "Contracts" or "Rate Sheets" are often messy Excel files. Our system uses **Agentic AI** (intelligent bots) to:
1.  **Read** the Excel like a human would.
2.  **Understand** the shipping routes, prices, and dates.
3.  **Fill** a standard template (`Ouput template.xlsx`) automatically.

---

## 🚦 2. Logistics 101 (Key Terms)
To use this system, you just need to know these 4 things:
- **FCL (Full Container Load)**: Shipping using entire containers (20ft, 40ft).
- **Origin/Destination**: Where the cargo starts and where it ends.
- **Freight**: The main cost of shipping across the ocean.
- **Surcharges (Recargos)**: Extra fees like "THC" (Terminal Handling) or "BAF" (Fuel).

---

## 🛠️ 3. How the AI "Thinks" (The Pipeline)

### Phase 1: The Scanner (Discovery)
The AI first looks at the sheet and draws "boxes" around tables. 
- It uses a **Pipe Separator (`|`)** to keep data clean.
- It handles **Merged Cells** (cells that span multiple rows/columns) so data doesn't get shifted.

### Phase 2: The Intelligence (Mapping)
The AI applies "Golden Rules" that you don't have to worry about:
1.  **The Export Rule**: If the trip starts in **Spain, Portugal, or Italy**, the AI knows it's an **Export**.
2.  **The 16-Container Grid**: It maps prices to 16 specific types (e.g., `20DRY`, `40HDRY`, `20TK` for Tanks).
3.  **The Shared Column Rule**: If a column says `40'GP/HC`, the AI is smart enough to put that price in **both** the `40DRY` and `40HDRY` columns.
4.  **Implicit Freight**: If it sees a table of prices but no name, it labels it as `FREIGHT`.

---

## 📖 4. Field Dictionary (Simple Version)
| Template Column | What goes here? |
| :--- | :--- |
| **ORIGIN** | The starting port (e.g., `Valencia, Spain`). |
| **DESTINATION** | The ending port (e.g., `New York, USA`). |
| **CHARGE** | The name of the fee (e.g., `OCEAN FREIGHT`, `THC`). |
| **CURRENCY** | The money used (EUR, USD). |
| **NOTAS** | **Very Important**: The name of the sheet we found the data on. |

---

## 📝 5. Step-by-Step Instructions for You
1.  **Upload**: Click the box on the website and select your contract file.
2.  **Verify**: The screen will show you the tables the AI found. Check if the table boundaries (like `A1:G100`) look right.
3.  **Process**: Click the blue **"Process to Template 🚀"** button.
4.  **Check**: The system will give you a file called `processed_...`. Open it and make sure the prices are in the right columns.

---

## 🆘 6. Troubleshooting
- **AI didn't find a table?** Check if the table is deeper than row 3000. If so, move it up.
- **Wrong Name?** The AI scans the rows **above** the table for a name. If it can't find one, it makes one up.
- **JSON Error?** This usually means the table was too huge. The system now handles up to 3000 rows, but keep tables clean for best results.
