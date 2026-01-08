# 🏭 Manufacturing Cost Estimator & Proposal Automation

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![GUI](https://img.shields.io/badge/GUI-Tkinter-green?style=for-the-badge)
![Data](https://img.shields.io/badge/Data-Pandas-orange?style=for-the-badge)

## 📖 Overview

This is a comprehensive desktop application designed to streamline the **cost estimation** and **proposal generation** process for Small and Medium-sized Businesses (SMBs) in the manufacturing industry.

Developed to bridge the gap between engineering design and sales, this tool allows users to calculate precise costs for raw materials, standard parts (motors, bearings, etc.), and labor, automatically converting currencies and generating professional Excel reports.

## 🚀 Key Features

* **Dynamic Catalog Management:**
    * Includes a built-in database (JSON) for standard parts like Motors, Reducers, Bearings, and Raw Materials.
    * **"Add on the Fly":** Users can manually add new items during the estimation process, which are automatically saved to the persistent database.
* **Live Currency Integration:**
    * Fetches real-time exchange rates (USD/EUR) from the **Central Bank of the Republic of Turkey (TCMB)** using XML parsing.
    * Automatically converts all costs to the desired currency.
* **Advanced Cost Analysis:**
    * Separates **Raw Costs** vs. **Sales Prices**.
    * Applies different profit margins for **Materials** (e.g., 30%) and **Labor** (e.g., 60%).
    * Calculates VAT (KDV) and generates the final offer price.
* **Labor & Outsourcing Calculation:**
    * Calculates labor costs based on worker count, hours, and hourly rates.
    * Includes sections for outsourced services (e.g., Automation/Software).
* **Excel Export:**
    * Generates a detailed `.xlsx` file with a summary sheet and itemized breakdown, ready to be sent to customers.

## 🛠️ Tech Stack

* **Language:** Python 3.12+
* **GUI Framework:** Tkinter (Custom layout with Treeview)
* **Data Manipulation:** Pandas, NumPy
* **Network/API:** Requests (for TCMB Currency Data)
* **Database:** JSON (Local persistent storage)
* **Concurrency:** Threading (Non-blocking UI during API calls)

## 📸 Screenshots

*(You can upload a screenshot of your app here to show how it looks)*

## 📦 Installation & Usage

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/hasanmihalicli23/Manufacturing-Cost-Estimator.git](https://github.com/hasanmihalicli23/Manufacturing-Cost-Estimator.git)
    cd Manufacturing-Cost-Estimator
    ```

2.  **Install Dependencies**
    ```bash
    pip install pandas openpyxl requests
    ```

3.  **Run the Application**
    ```bash
    python maliyet.py
    ```

4.  **Create Executable (Optional)**
    To run as a standalone `.exe` on Windows without Python installed:
    ```bash
    pyinstaller --onefile --noconsole --name "CostEstimator" maliyet.py
    ```

## 🔮 Future Roadmap

* [ ] SQL Database integration for multi-user support.
* [ ] PDF Proposal generation with company logo.
* [ ] Cloud synchronization for catalog items.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/hasanmihalicli23/Manufacturing-Cost-Estimator/issues).

## 👨‍💻 Author

**Hasan Mıhalıçlı**
* *Mechanical Engineer & Developer*
* [LinkedIn Profile](https://www.linkedin.com/in/hasanmihalicli23/)

---
*This project was developed to solve real-world calculation problems in a machinery manufacturing environment.*
