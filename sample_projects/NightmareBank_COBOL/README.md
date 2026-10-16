# NightmareBank COBOL - Overdraft Fee Calculation

This project simulates a legacy COBOL batch system for calculating overdraft fees.

## Business Rules (as understood from the code)

1.  **Transaction Processing:** The system reads transaction records from `transactions.csv`.
2.  **Overdraft Detection:** If an account's balance (`ACCT-BAL`) is negative, an overdraft fee is considered.
3.  **Fee Calculation (`FEE-CALC`):**
    *   Account Type 'C' incurs a base fee of $35.00.
    *   Account Type 'S' incurs a base fee of $25.00.
    *   Any other account type incurs a $50.00 fee.
    *   **Legacy Anomaly:** If the `Y2K-FLAG` is 'N', an additional $5.00 is added to the fee. The origin of this rule is lost to time.
4.  **Fee Application:** The calculated fee is subtracted from `ACCT-BAL`.
5.  **Overdraft Limit (Commented Out/Ignored):** There is a field `OVD-LIMIT` which historically might have been used, but recent modifications by "MIKE" in 2004 have commented out its usage to prevent production crashes. The system does NOT currently enforce overdraft limits.
6.  **Y2K Compliance:** A `Y2K-FLAG` is present, indicating potential Y2K readiness. A check was added by "DAVE" in 1999.

## Dependencies

*   `ACCT-REC.cpy`: A shared copybook defining the account record structure.
*   `FEE-CALC.cbl`: A subprogram that performs the actual fee calculation.
*   `transactions.csv`: Synthetic data file.

## Known Issues (Refer to `expected_analysis.json`)

*   Spaghetti code with `GO TO` statements.
*   Hardcoded magic numbers for fee amounts.
*   Lack of overdraft limit enforcement.
*   Unexplained surcharge based on `Y2K-FLAG`.
*   Potential for data type issues or unexpected balance behavior due to insufficient validation.
