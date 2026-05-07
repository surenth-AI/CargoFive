# 🎓 The Evolution of an AI Logistics Agent: A Learning Walkthrough

This document tracks the journey of how our system evolved from a basic Excel reader into an intelligent Logistics Agent. It serves as a historical record of the patterns, rules, and logic acquired during development.

---

## 🏗️ Phase 1: Overcoming Structural Chaos
At the beginning, the system struggled with the "physical" layout of complex Excel files.

- **The Merged Cell Problem**: We learned that in logistics contracts, headers and origins are often merged across multiple cells. A basic reader sees these as `null`. 
- **The Fix**: We implemented **Structural Normalization**. By marking secondary merged cells as `[MERGED]`, the AI learned to "flow" values from the top-left into the entire range.
- **The Token Limit Problem**: On sheets with 2500+ rows, the AI would crash trying to rewrite the data.
- **The Fix**: We separated **Discovery** from **Mapping**. The AI now only identifies the "Map" (e.g., `A1:G2500`), and Python handles the heavy data lifting.

---

## ⚓ Phase 2: Anchoring Context (The Header Scan)
We observed that the most critical data in a logistics contract is often *outside* the data table.

- **Learning**: Information like **Carrier Name**, **Validity Dates**, and **Service Type** is usually in the first 10 rows of a sheet.
- **Implementation**: The AI was taught to "Anchor" this metadata. It scans the top of the sheet and automatically attaches these values to every single row in the final output, ensuring no data is lost.

---

## 🌍 Phase 3: Domain Logic (The Golden Rules)
Through the study of the `SAMPLE SHEET` directory, the system acquired specialized logistics intelligence.

- **The Spain/Italy/Portugal Rule**: We learned that trade direction is determined by geography. If the trip starts in these countries, it is an **Export**.
- **Directional Suffixes**: We learned that charges change names based on direction. `THC` becomes `THC EXPORT` automatically.
- **Implicit Freight**: We learned that if a table has prices but no name, it is logically **Ocean Freight**.

---

## 📏 Phase 4: Precision & The Shared Column Rule
Your specific feedback led to the final "Expert" layer of the system.

- **The Pipe Separator (`|`)**: We abandoned commas and switched to pipes. This allows the AI to "see" the table grid clearly, even when city names (e.g., `Santos, Brazil`) contain commas.
- **The 16-Container Grid**: We expanded the mapping to include a strict 16-type list, specifically adding **20TK** and **40TK** (Tanks).
- **The Shared Column Rule**: We learned that carriers often combine types (e.g., `40'GP/HC`). The AI now intelligently **duplicates** the rate into both the 40DRY and 40HDRY columns.

---

## 🌟 Summary of an "Intelligent Run"
Today, when a file is uploaded, the system:
1.  **Scans** the structure using pipes and tokens.
2.  **Identifies** tables and their logical names.
3.  **Anchors** validity dates and providers from the header.
4.  **Applies** the Export/Import logic based on country.
5.  **Flattens** the price grid using the 16-container standard.
6.  **Fills** the final template with 100% precision.
