*** Settings ***
Test Setup     cleanup task by executor names   刘鹏测试   刘鹏测试2   刘鹏测试3
Resource    ../resources/resource.robot
Library     String
Library      ../VerifyLibrary.py   http://${SERVER}    ${ADMIN USER}    ${DUBBO WEB API URL}

*** Test Cases ***
Test Verify Log Personal Register User With All Pass Flow
    [Documentation]    接口自动化, 测试个人注册用户, 全部通过审核情况下的审核流水

    log     更新用户类型为PERSONAL_REGISTER
    update user channel type to personal register  auto_01

    Test Verify Log With All Pass Flow

Test Verify Log BD Import User With All Pass Flow
    [Documentation]    接口自动化, 测试BD渠道用户, 全部通过审核情况下的审核流水

    log     更新用户类型为BD_IMPORT
    update user channel type to db import  auto_01

    Test Verify Log With All Pass Flow

Test Verify Log Personal Register With Verify Refuse
    [Documentation]    接口自动化, 测试个人注册用户, 每个审核节点都退回, 最终通过审核

    log     更新用户类型为PERSONAL_REGISTER
    update user channel type to personal register  auto_01

    Test Verify Log With Verify Refuse

Test Verify Log BD Import With Verify Refuse
    [Documentation]    接口自动化, 测试BD渠道注册用户, 每个审核节点都退回, 最终通过审核

    log     更新用户类型为BD_IMPORT
    update user channel type to db import  auto_01

    Test Verify Log With Verify Refuse


*** Keywords ***
Flow Task Setup By People
    [Arguments]    ${verify user name}
    log     设置首次调查的人员
    flow setup by people for inquireing   ${verify user name}
    log     设置一审的人员
    flow setup by people for inquire success  ${verify user name}
    log     设置二审的人员
    flow setup by people for first verify success  ${verify user name}
    log     设置上签的人员
    flow setup by people for second verify success  ${verify user name}

Test Verify Log With All Pass Flow
    Flow Task Setup By People    刘鹏测试
    log     将auto_01初始化，并注册
    populate task by nick names  auto_01

    log     比较审核流水中的用户信息部分，API返回与数据库中的记录是否一致
    compare user info for verify log  auto_01

    log     验证审核流水中的每个条目
    compare verify log  auto_01     0   用户注册    等待提交
    compare verify log  auto_01     1   提交审核    首次调查
    ${verify log count} =   get verify log count  auto_01
    should be equal as integers  2      ${verify log count}     应该有2条审核流水

    log    提交到一审
    commit to first verify      刘鹏测试    auto_01
    sleep   1
    compare verify log  auto_01  2   调查    待一审   刘鹏测试   调查备注
    ${verify log count} =   get verify log count  auto_01
    should be equal as integers  3      ${verify log count}     应该有3条审核流水

    log    提交到二审
    commit to second verify       刘鹏测试    auto_01
    sleep   1
    compare verify log  auto_01  3   一审     二审   刘鹏测试   一审备注    1000.0    黑卡五星    12.0
    ${verify log count} =   get verify log count  auto_01
    should be equal as integers  4      ${verify log count}     应该有4条审核流水

    log    提交到上签
    commit to pass second verify  刘鹏测试    5001    auto_01
    sleep   1
    compare verify log  auto_01  4   二审     上签   刘鹏测试   二审备注    5001.0    黑卡五星    12.0
    ${verify log count} =   get verify log count  auto_01
    should be equal as integers  5      ${verify log count}     应该有5条审核流水

    log    提交到最终审核通过
    commit to pass third verify  刘鹏测试    10000    auto_01
    sleep   1
    compare verify log  auto_01  5   上签     审核通过   刘鹏测试   最终审核通过    10000.0    黑卡五星    12.0
    ${verify log count} =   get verify log count  auto_01
    should be equal as integers  6      ${verify log count}     应该有6条审核流水

Test Verify Log With Verify Refuse
    Flow Task Setup By People    刘鹏测试
    log     将auto_01初始化，并注册
    populate task by nick names  auto_01
    sleep   1

    log     将auto_01补件
    commit to verify fail  刘鹏测试     auto_01
    sleep   1

    log     将auto_01补件后再次提交
    commit user by nick names  auto_01
    sleep   1

    log    提交到一审
    commit to first verify      刘鹏测试    auto_01
    sleep   1

    log    一审退回
    commit to first verify back  刘鹏测试   auto_01
    sleep   1

    log    再次一审
    commit to first verify      刘鹏测试    auto_01
    sleep   1

    log    提交到二审
    commit to second verify       刘鹏测试    auto_01
    sleep   1

    log    二审退回
    commit to second verify back       刘鹏测试    auto_01
    sleep   1

    log    再次二审
    commit to second verify       刘鹏测试    auto_01
    sleep   1

    log    提交到上签
    commit to pass second verify  刘鹏测试    5001    auto_01
    sleep   1

    log     上签退件
    commit to refuse  刘鹏测试  auto_01
    sleep   1

    log     比较审核流水中的用户信息部分，API返回与数据库中的记录是否一致
    compare user info for verify log  auto_01

    log     验证审核流水中的每个条目
    compare verify log  auto_01     0   用户注册    等待提交
    compare verify log  auto_01     1   提交审核    首次调查
    compare verify log  auto_01     2   调查      补件      刘鹏测试        补件调查
    compare verify log  auto_01     3   提交审核      补件调查
    compare verify log  auto_01     4   调查      待一审     刘鹏测试        调查备注
    compare verify log  auto_01     5   一审     退回调查     刘鹏测试        一审退回
    compare verify log  auto_01     6   调查      待一审     刘鹏测试        调查备注
    compare verify log  auto_01     7   一审     二审   刘鹏测试   一审备注    1000.0    黑卡五星    12.0
    compare verify log  auto_01     8   二审     退回一审     刘鹏测试        二审退回
    compare verify log  auto_01     9   一审     二审   刘鹏测试   一审备注    1000.0    黑卡五星    12.0
    compare verify log  auto_01     10   二审     上签   刘鹏测试   二审备注    5001.0    黑卡五星    12.0
    compare verify log  auto_01     11   上签      退件     刘鹏测试

    ${verify log count} =   get verify log count  auto_01
    should be equal as integers  12      ${verify log count}     应该有12条审核流水
