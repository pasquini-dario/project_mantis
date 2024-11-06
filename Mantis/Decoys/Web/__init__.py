SERVER_BANNER = 'Apache 5.45'

SQL_ERROR_STR = b"""<b1> Microsoft OLE DB Provider for SQL Server error '80040e14' </b1>
<b2> Unclosed quotation mark after the character string ' '. </b2>
"""

SQL_INJECTION_STRINGS = [
    "%27",          # URL-encoded '
    "%22",          # URL-encoded "
    "' OR '1'='1",
    "--",           # SQL single-line comment
    ";",            # End of SQL statement
    "#",            # MySQL single-line comment
    "/*",           # SQL multi-line comment start
    "*/",           # SQL multi-line comment end
    "UNION SELECT",
    "SLEEP(",
    "BENCHMARK(",
    "@@",           # MySQL system variables
    "INFORMATION_SCHEMA",
    "DROP TABLE",
    "CREATE TABLE",
    "INSERT INTO",
    "xp_",          # SQL Server extended procedures
    "EXEC(",

    # XSS Indicators
    "<script>",
    "</script>",
    "onerror=",
    "onload=",
    "onclick=",
    "javascript:",
    "alert(",
    "document.cookie",
    "document.location",
    "<iframe>",
    "</iframe>",
    "src=",
    "href=",
    "<img src=",

    # Command Injection Indicators
    "&&",           # Command chaining
    "|",            # Pipe operator in shells
    "$( ... )",     # Command substitution in Unix shells
    "&",            # Background operator
    "cat ",
    "ls ",
    "pwd ",
    "powershell",

    # Directory Traversal Indicators
    "../",          # Move up directories
    "..\\",         # Move up directories (Windows)
    "file://",
    "/etc/passwd",  # Common Unix file access
    "C:\\Windows\\", # Windows system path
    "%SYSTEMROOT%",
    "%USERPROFILE%",

    # General Indicators
    "{",            # Often used in code injection
    "}",
    "\"",           # Escape character
    "'",            # Escape character
    "\\",           # Escape character

]