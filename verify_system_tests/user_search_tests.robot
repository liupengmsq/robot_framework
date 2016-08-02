*** Settings ***
Test Setup       Open Browser To Login Page
#Test Teardown    Close Browser
Resource    ../resources/resource.robot
Library     String
#Library      ../VerifyLibrary.py   http://${SERVER}    ${ADMIN USER}
Library      ../VerifyLibrary.py   http://${SERVER}    ${ADMIN USER}    ${DUBBO WEB API URL}
Test Template    Search user test

*** Test Cases ***
Test Search By Nick Name And Uncommit        昵称      等待提交    auto_01    100034832
Test Search By Nick Name And Inquireing        昵称     等待调查   auto_01    100034832
Test Search By Nick Name And Inquire Success       昵称     等待一审   auto_01    100034832
Test Search By Nick Name And First Verify Success       昵称     等待二审   auto_01    100034832
Test Search By Nick Name And First Verify Sendback       昵称     一审退回   auto_01    100034832
Test Search By Nick Name And Verify Success       昵称     审核通过   auto_01    100034832
Test Search By Nick Name And Second Verify Sendback       昵称     二审退回   auto_01    100034832
Test Search By Nick Name And Verify Reject       昵称     退件   auto_01    100034832
Test Search By Nick Name And Verify Fail       昵称     补件    auto_01    100034832
Test Search By Mobile And Uncommit        手机号    等待提交    13146865530    100034832
Test Search By Mobile And Inquireing        手机号   等待调查    13146865530    100034832
Test Search By Mobile And Inquire Success        手机号    等待一审      13146865530    100034832
Test Search By Mobile And First Verify Success        手机号    等待二审      13146865530    100034832
Test Search By Mobile And First Verify Sendback        手机号    一审退回      13146865530    100034832
Test Search By Mobile And Verify Success        手机号    审核通过     13146865530    100034832
Test Search By Mobile And Second Verify Sendback        手机号    二审退回      13146865530    100034832
Test Search By Mobile And Verify Reject        手机号    退件      13146865530    100034832
Test Search By Mobile And Verify Fail        手机号    补件     13146865530    100034832
Test Search By IdNo And Uncommit        身份证    等待提交    130521199307091000    100034832
Test Search By IdNo And Inquireing        身份证    等待调查       130521199307091000    100034832
Test Search By IdNo And Inquire Success        身份证    等待一审         130521199307091000    100034832
Test Search By IdNo And First Verify Success        身份证    等待二审         130521199307091000    100034832
Test Search By IdNo And First Verify Sendback        身份证    一审退回    130521199307091000    100034832
Test Search By IdNo And Verify Success        身份证    审核通过   130521199307091000    100034832
Test Search By IdNo And Second Verify Sendback        身份证    二审退回    130521199307091000    100034832
Test Search By IdNo And Verify Reject        身份证    退件    130521199307091000    100034832
Test Search By IdNo And Verify Fail        身份证    补件   130521199307091000    100034832
Test Search By Real Name Uncommit        姓名      等待提交    施旭宁    100034832
Test Search By Real Name Inquireing        姓名      等待调查         施旭宁    100034832
Test Search By Real Name Inquire Success        姓名    等待一审      施旭宁    100034832
Test Search By Real Name First Verify Success        姓名    等待二审      施旭宁    100034832
Test Search By Real Name First Verify Sendback        姓名    一审退回      施旭宁    100034832
Test Search By Real Name Verify Success        姓名    审核通过   施旭宁    100034832
Test Search By Real Name Second Verify Sendback        姓名    二审退回      施旭宁    100034832
Test Search By Real Name Verify Reject        姓名    退件     施旭宁    100034832
Test Search By Real Name Verify Fail        姓名    补件   施旭宁    100034832

*** Keywords ***
Search user test
    [Arguments]     ${search key}  ${verify status}  ${key}  ${user id}
    Login With Valid Account    ${ADMIN USER}   ${ADMIN PASSWORD}
    Click TreeNode		 用户查询
    Page Title Visible   用户查询
    Select Frame   ${USER SEARCH IFRAME}
    Run Keyword If      '${search key}' == '昵称'     User Search Select By NickName
    Run Keyword If      '${search key}' == '手机号'    User Search Select By Mobile
    Run Keyword If      '${search key}' == '身份证'    User Search Select By IdNo
    Run Keyword If      '${search key}' == '姓名'     User Search Select By RealName
    populate task by nick names  auto_01
    Update Verify User Status   ${user id}      ${verify status}
    Run Keyword If      '${verify status}' == '等待提交'      User Search Select By UNCOMMIT Status
    Run Keyword If      '${verify status}' == '等待调查'      User Search Select By INQUREING Status
    Run Keyword If      '${verify status}' == '等待一审'      User Search Select By INQUIRE_SUCCESS Status
    Run Keyword If      '${verify status}' == '一审退回'      User Search Select By FIRST_SEND_BACK Status
    Run Keyword If      '${verify status}' == '等待二审'      User Search Select By FIRST_VERIFY_SUCCESS Status
    Run Keyword If      '${verify status}' == '审核通过'      User Search Select By VERIFY_SUCCESS Status
    Run Keyword If      '${verify status}' == '二审退回'      User Search Select By SECOND_SEND_BACK Status
    Run Keyword If      '${verify status}' == '补件'      User Search Select By VERIFY_FAIL Status
    Run Keyword If      '${verify status}' == '退件'      User Search Select By VERIFY_REJECT Status
    Input Text     id=oText    ${key}
    Click Button   id=oSubmit
    Wait Until Page Contains Element    ${USER SEARCH TABLE}

    ${row_count} =      Get Table Row Count   ${USER SEARCH TABLE}
    Log     共有行数：${row_count}
    should be equal as integers     ${row_count}    1       应该只搜索到一条数据

    : FOR    ${i}   IN RANGE    ${row_count}
    \   ${row} =       Get User Search Results     ${USER SEARCH TABLE}    ${i}
    \   Log     第${i}行：${row}
    \   Compare User Search Result      ${row}      ${i}       ${key}   ${search key}   ${verify status}
