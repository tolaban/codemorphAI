           IDENTIFICATION DIVISION.
           PROGRAM-ID. FEE-CALC.
           DATA DIVISION.
           WORKING-STORAGE SECTION.
           01  WS-BASE-FEE PIC S9(3)V99 VALUE 35.00.

           LINKAGE SECTION.
           COPY ACCT-REC.
           01  LS-FEE-AMT  PIC S9(3)V99.

           PROCEDURE DIVISION USING ACCOUNT-RECORD, LS-FEE-AMT.
           100-CALC-FEE.
      *        MAGIC NUMBERS AND SPAGHETTI LOGIC
               IF ACCT-TYPE = 'C'
                   MOVE 35.00 TO LS-FEE-AMT
               ELSE IF ACCT-TYPE = 'S'
                   MOVE 25.00 TO LS-FEE-AMT
               ELSE
      *            UNKNOWN TYPE GETS MAX PENALTY
                   MOVE 50.00 TO LS-FEE-AMT
               END-IF.

      *        DEFECT: NO CHECK IF ACCT-BAL + FEE EXCEEDS OVERDRAFT LIMIT
      *        DEFECT: IF Y2K-FLAG = 'N' WE ADD $5 WEIRD SURCHARGE (LOST TO HISTORY WHY)
               IF Y2K-FLAG = 'N'
                   COMPUTE LS-FEE-AMT = LS-FEE-AMT + 5.00
               END-IF.

               EXIT PROGRAM.
