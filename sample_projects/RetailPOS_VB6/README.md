# Retail POS VB6 - Checkout and Discount System

This project simulates a legacy VB6 Point-of-Sale (POS) checkout form with customer discount logic.

## Business Rules (as understood from the code)

1.  **Checkout Processing:** Users enter an order total, their customer tier, and the number of years they've been a customer.
2.  **Discount Calculation (`clsCustomerDiscount`):**
    *   **Tier-Based Discount:**
        *   Tier 1: 15% discount.
        *   Tier 2: 5% discount.
        *   Tiers 3+: No base discount.
    *   **Loyalty Bonus:** An additional discount is calculated based on years as a customer. The formula `0.01 / Years` is applied.
        *   **Edge Case:** If `Years` is 0, no additional discount is added (to prevent division by zero errors).
    *   **Special Exception:** The global `g_UserID` variable is checked. If it matches `"JTIMMINS"`, a 100% discount is applied, overriding all other calculations.
3.  **Final Total:** The calculated discount amount is subtracted from the original order total.
4.  **Database Recording:** The final total and discount amount are inserted into a `Sales` table, along with the current date.
5.  **Database Connection:** A global `ADODB.Connection` object (`g_dbConn`) is used, established via `modGlobalDB.bas`.

## Dependencies

*   `modGlobalDB.bas`: Contains global database connection management (`ConnectDB`, `DisconnectDB`).
*   `clsCustomerDiscount.cls`: Implements the customer discount calculation logic.
*   `frmCheckout.frm`: The main VB6 form for the checkout process.
*   `sales_data.csv`: Synthetic data for sales transactions.

## Known Issues (Refer to `expected_analysis.json`)

*   Global variable abuse for database connection (`g_dbConn`).
*   Hardcoded database credentials in `modGlobalDB.bas`.
*   Extensive use of `On Error Resume Next`, masking potential errors.
*   UI code mixed with business logic and direct SQL execution in the form's event handler.
*   Magic numbers for discount percentages.
*   Potential division by zero in discount calculation (mitigated by a basic `If Years > 0` check).
*   SQL injection vulnerabilities due to string concatenation for SQL queries.
*   Lack of transactional integrity for database operations.
*   Hardcoded user exception for discounts.
