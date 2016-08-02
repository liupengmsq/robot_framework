*** Settings ***
Test Setup       Open Browser To Login Page
#Test Teardown    Close Browser
Resource    ../resources/resource.robot
Library     String
Library      ../VerifyLibrary.py   http://${SERVER}    ${ADMIN USER}    ${DUBBO WEB API URL}

*** Test Cases ***
Test Investigate User
    [Documentation]    WEB UI 自动化, 测试调查

    log     清理所有"刘鹏测试"下的待办任务
    cleanup task by executor names   刘鹏测试

    log     设置首次调查的人员
    flow setup by people for inquireing   刘鹏测试

    log     产生新的进件
    populate task by nick names  auto_01

    log     使用管理员登陆系统
    Login With Valid Account    liupeng@renrendai.com   L123456
    Click TreeNode		 待办任务
    Page Title Visible   待办任务

    Wait Until Page Contains Element    ${FLOW TASK TABLE}
    ${row_count} =      Get Table Row Count   ${FLOW TASK TABLE}
    log     获取待办任务个数: ${row_count}
    should be equal as integers     ${row_count}    1       应该只搜索到一条数据

