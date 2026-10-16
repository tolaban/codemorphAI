           IDENTIFICATION DIVISION.
           PROGRAM-ID. OVD-DRIVER.
           AUTHOR. DAVE.
           DATE-WRITTEN. 1998-05-12.
      *    MODIFIED 1999-11-20 DAVE: ADDED Y2K FLAG CHECK
      *    MODIFIED 2004-03-01 MIKE: FIX PROD CRASH - COMMENTED OUT LIMIT
           ENVIRONMENT DIVISION.
           INPUT-OUTPUT SECTION.
           FILE-CONTROL.
               SELECT ACCT-FILE ASSIGN TO 'transactions.csv'
                   ORGANIZATION IS LINE SEQUENTIAL.
           DATA DIVISION.
           FILE SECTION.
           FD  ACCT-FILE.
           01  FILE-REC PIC X(50).

           WORKING-STORAGE SECTION.
           01  WS-EOF-FLAG         PIC X VALUE 'N'.
           01  WS-FEE-AMT          PIC S9(3)V99 VALUE ZERO.
           01  WS-REC-COUNT        PIC 9(4) VALUE ZERO.

           COPY ACCT-REC.

           PROCEDURE DIVISION.
           100-MAIN-LOGIC.
               OPEN INPUT ACCT-FILE
               PERFORM 200-PROCESS-RECORDS UNTIL WS-EOF-FLAG = 'Y'
               CLOSE ACCT-FILE
               DISPLAY 'TOTAL RECORDS: ' WS-REC-COUNT
               STOP RUN.

           200-PROCESS-RECORDS.
               READ ACCT-FILE INTO ACCOUNT-RECORD
                   AT END
                       MOVE 'Y' TO WS-EOF-FLAG
                       GO TO 200-EXIT
               END-READ

               ADD 1 TO WS-REC-COUNT

      *        IF OVD-LIMIT IS ZERO DONT DO ANYTHING - MIKE
               IF OVD-LIMIT = 0
                   GO TO 200-PROCESS-RECORDS
               END-IF

               IF ACCT-BAL < 0
      *            PASS TO FEE CALC MODULE
                   CALL 'FEE-CALC' USING ACCOUNT-RECORD, WS-FEE-AMT
                   COMPUTE ACCT-BAL = ACCT-BAL - WS-FEE-AMT
                   DISPLAY 'OVERDRAFT FEE CHARGED. NEW BAL: ' ACCT-BAL
               END-IF.

           200-EXIT.
               EXIT.
