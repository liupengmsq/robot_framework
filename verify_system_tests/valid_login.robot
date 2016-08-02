*** Settings ***
Resource          ../resources/resource.robot

*** Test Cases ***
Valid Login
    Open Browser To Login Page
    Input Username    liupeng@renrendai.com
    Input Password    L123456
    Submit Credentials
    Wait Until Keyword Succeeds		2 min		10 sec		Welcome Page Should Be Open
    [Teardown]    Close Browser
