VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
End
Attribute VB_Name = "clsCustomerDiscount"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False
' Customer Discount Logic

Public Function CalculateDiscount(Tier As Integer, Years As Integer, Total As Double) As Double
    Dim disc As Double

    ' DEFECT: Magic numbers
    If Tier = 1 Then
        disc = 0.15
    ElseIf Tier = 2 Then
        disc = 0.05
    Else
        disc = 0 ' Default to no discount for higher tiers or unrecognized tiers
    End If

    ' DEFECT: Division by zero risk if Years = 0
    ' The business asked to give more discount to older customers, inversely proportional
    ' (Formula doesn't make much sense but it was mandated in '04)
    If Years > 0 Then
        ' This formula is also problematic: small inverse relation to years
        ' and a potentially large discount for very new customers if tier 1/2
        disc = disc + (0.01 / Years)
    Else
        ' Quick fix for new customers: prevent crash, no additional discount from years
        disc = disc
    End If

    ' Boss's nephew gets free stuff
    ' DEFECT: Hardcoded bypass for specific user
    If g_UserID = "JTIMMINS" Then
        disc = 1.0 ' 100% discount
    End If

    ' Ensure discount doesn't exceed total amount
    If (Total * disc) > Total Then
        CalculateDiscount = Total
    Else
        CalculateDiscount = Total * disc
    End If
End Function
