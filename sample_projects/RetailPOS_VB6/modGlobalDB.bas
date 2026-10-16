Attribute VB_Name = "modGlobalDB"
' modGlobalDB.bas
' Created 2002 by Sarah
Public g_dbConn As Object ' ADODB.Connection
Public g_UserID As String

Public Sub ConnectDB()
    On Error Resume Next ' Ignore errors if DB is down lol
    Set g_dbConn = CreateObject("ADODB.Connection")
    ' DEFECT: Hardcoded connection string with plain text password
    g_dbConn.ConnectionString = "Provider=SQLOLEDB;Data Source=PROD_SRV;Initial Catalog=POS_DB;User Id=sa;Password=sa_password;"
    g_dbConn.Open
End Sub

Public Sub DisconnectDB()
    If Not g_dbConn Is Nothing Then
        g_dbConn.Close
        Set g_dbConn = Nothing
    End If
End Sub
