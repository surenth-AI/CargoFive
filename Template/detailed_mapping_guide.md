# 🗺️ Detailed Technical Mapping Guide (39-Column Standard)

This guide provides the exact mapping logic for every field in the `Ouput template.xlsx`. This is the "Technical Bible" used by the AI Agent to ensure 100% data integrity.

---

## 🏗️ 1. Core Route Information

The system handles route information differently depending on the target sheet:

### A. Fletes y Recargos (FCL Ocean)
| # | Col | Column Name | Intelligence / Logic |
| :--- | :--- | :--- | :--- |
| **1** | **A** | **ORIGIN LOCATION** | City or Region of origin (e.g., `Madrid`). |
| **2** | **B** | **ORIGIN PORT** | 5-letter UN/LOCODE port of origin (e.g., `ESMAD`). |
| **3** | **C** | **DESTINATION PORT**| 5-letter UN/LOCODE port of destination (e.g., `CNSHA`). |
| **4** | **D** | **DESTINATION LOCATION** | City or Region of destination (e.g., `Shanghai`). |

### B. Arbitraries (Land/Feeder)
| # | Col | Column Name | Intelligence / Logic |
| :--- | :--- | :--- | :--- |
| **1** | **A** | **ORIGIN** | Combined origin point or route description. |
| **2** | **B** | **DESTINATION** | Combined destination point. |

---

## 💰 2. Charge & Financial Logic
| # | Col | Column Name | Intelligence / Logic |
| :--- | :--- | :--- | :--- |
## 💰 2. Charge & Financial Logic
| # | Col | Column Name | Intelligence / Logic |
| :--- | :--- | :--- | :--- |
| **5** | **E** | **CHARGE TYPE** | **Intelligent**: Identifies `Ocean Freight`, `Local Charge`, or `Surcharge` based on context. |
| **6** | **F** | **CHARGE** | **Standardized**: Maps source labels to industry standard codes (e.g., `THC`, `BAF`, `FREIGHT`). |
| **7** | **G** | **RATE BASIS** | **Standardized**: Maps to `PER_CONTAINER`, `PER_TEU`, `PER_BL`, etc. |
| **8** | **H** | **CURRENCY** | **Extraction**: Extracts ISO codes (USD, EUR,etc) from table headers or footer notes. |

---

## 📦 3. Container Price Grid (The 16 Columns)
The system intelligently identifies price grids and maps them to the appropriate container columns.
**CRITICAL RULES**:
1. **INTEGERS ONLY**: The system converts all extracted prices to numeric types, stripping symbols and text.
2. **Shift Prevention**: Agent uses spatial reasoning to ensure 20' and 40' data is correctly separated.

| # | Col | Column | Shared Column Logic |
| :--- | :--- | :--- | :--- |
| **9-13** | **I-M** | **DRY Units** | `20DRY`, `40DRY`, `40HDRY`, `45HDRY`, `40NOR`. |
| **14-16** | **N-P** | **Reefer Units** | `20RF`, `40HCRF`, `45RF`. |
| **17-19** | **Q-S** | **Open Top** | `20OT`, `40OT`, `40HCOT`. |
| **20-22** | **T-V** | **Flat Rack** | `20FR`, `40FR`, `40HCFR`. |
| **23-24** | **W-X** | **Tanks** | `20TK` and `40TK`. |

---

## 🏢 4. Provider & Service Context
| # | Col | Column Name | Intelligence / Logic |
| :--- | :--- | :--- | :--- |
| **26** | **Z** | **PROVIDER** | **Intelligent**: Identified from branding, logos, or sheet metadata. |
| **28** | **AB**| **START DATE** | **Extraction**: Pulled from validity headers or global sheet context. |
| **29** | **AC**| **EXPIRATION DATE**| **Extraction**: Pulled from validity headers or global sheet context. |
| **34** | **AH**| **INCLUDED CHARGES**| **Logic**: Identify surcharges listed as "Included" in notes or rate text. |
| **39** | **AM**| **NOTES** | **Context**: Captures trade lanes, service names, or source sheet info. |

---

## 📑 5. Multi-Sheet Output Logic
The system automatically routes data based on the identified transport mode:

| Mode of Transport | Target Sheet | Logic |
| :--- | :--- | :--- |
| **SEA / Unknown** | **Fletes y Recargos ** | Standard ocean freight and surcharges. |
| **ROAD / RAIL / TRUCK** | **Arbitraries** | Land-based transport rates and feeder arbitraries. |

---

## 🎯 Intelligence Checklist
1.  **Context Detective**: The system scans the entire sheet (headers, footers, names) to find Dates and Providers.
2.  **Data Cleaning**: Verbatim source text is cleaned into standardized formats (Integers, ISO Codes).
3.  **Generalization**: Designed to handle various layouts (horizontal grids, vertical lists, combined columns).
4.  **Route Intelligence**: Splits complex route strings into Origin/Destination Port and Location components.
5.  **Smart Mapping**: Standardizes messy source labels into clean industry codes (e.g. `Detention` -> `DET`).
