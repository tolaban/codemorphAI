VERSION 5.00
Begin VB.Form frmCheckout
   Caption         =   "POS Checkout v3.11"
   ClientHeight    =   3000
   ClientWidth     =   4000
   ScaleHeight     =   3000
   ScaleWidth      =   4000
   StartUpPosition =   3  'Windows Default
   Begin VB.CommandButton cmdProcess
      Caption         =   "Process Sale"
      Height          =   375
      Left            =   1560
      TabIndex        =   0
      Top             =   2280
      Width           =   1335
   End
   Begin VB.TextBox txtTotal
      Height          =   285
      Left            =   1680
      TabIndex        =   1
      Text            =   "100.00"
      Top             =   720
      Width           =   1215
   End
   Begin VB.TextBox txtTier
      Height          =   285
      Left            =   1680
      TabIndex        =   2
      Text            =   "1"
      Top             =   1200
      Width           =   1215
   End
   Begin VB.TextBox txtYears
      Height          =   285
      Left            =   1680
      TabIndex        =   3
      Text            =   "5"
      Top             =   1680
      Width           =   1215
   End
   Begin VB.Label lblTotal
      Caption         =   "Order Total:"
      Height          =   255
      Left            =   360
      TabIndex        =   4
      Top             =   720
      Width           =   1335
   End
   Begin VB.Label lblTier
      Caption         =   "Customer Tier:"
      Height          =   255
      Left            =   360
      TabIndex        =   5
      Top             =   1200
      Width           =   1335
   End
   Begin VB.Label lblYears
      Caption         =   "Years as Customer:"
      Height          =   255
      Left            =   360
      TabIndex        =   6
      Top             =   1680
      Width           =   1335
   End
End
Attribute VB_Name = "frmCheckout"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
' UI Checkout Form

Private Sub cmdProcess_Click()
    ' DEFECT: On Error Resume Next swallows critical errors
    On Error Resume Next

    Dim total As Double
    Dim finalTotal As Double
    Dim custTier As Integer
    Dim custYears As Integer

    ' DEFECT: UI code mixed directly with business logic and data access
    total = CDbl(txtTotal.Text)
    custTier = CInt(txtTier.Text)
    custYears = CInt(txtYears.Text)

    Dim discountCalc As New clsCustomerDiscount
    Dim discAmt As Double

    ' Ensure database connection is established before proceeding
    If g_dbConn Is Nothing Or g_dbConn.State <> adStateOpen Then
        ConnectDB
        ' If connection still fails, exit gracefully (or with a less informative error)
        If g_dbConn Is Nothing Or g_dbConn.State <> adStateOpen Then
            MsgBox "Database connection failed. Cannot process sale.", vbCritical
            Exit Sub
        End If
    End If

    ' DEFECT: If g_UserID is not set, it defaults to empty string, not triggering nepotism discount.
    ' This makes the nepotism discount only work if g_UserID is explicitly set elsewhere.
    ' This might be intentional to prevent accidental discounts, but is a subtle flaw in robustness.
    ' For testing, we'd need to set g_UserID = "JTIMMINS" before calling this.

    ' DEFECT: Customer discount calculation might return NaN or Inf if inputs are extreme
    discAmt = discountCalc.CalculateDiscount(custTier, custYears, total)
    finalTotal = total - discAmt

    ' DEFECT: SQL Injection risk if inputs were not sanitized (though CDbl/CInt provide some basic type checking)
    ' DEFECT: No transaction management around database inserts
    Dim sql As String
    sql = "INSERT INTO Sales (Total, Discount, OrderDate) VALUES (" & finalTotal & ", " & discAmt & ", GETDATE())"
    g_dbConn.Execute sql

    MsgBox "Sale Processed Successfully! Final Total: $" & Format(finalTotal, "#,##0.00"), vbInformation

    ' Clean up the discount object
    Set discountCalc = Nothing

End Sub

' Added for completeness: A method to set the global UserID for testing the nepotism rule.
Public Sub SetGlobalUserID(userID As String)
    g_UserID = userID
End Sub
