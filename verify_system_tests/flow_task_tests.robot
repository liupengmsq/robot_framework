*** Settings ***
Test Setup     cleanup task by executor names   刘鹏测试   刘鹏测试2   刘鹏测试3
Resource    ../resources/resource.robot
Library     String
Library      ../VerifyLibrary.py   http://${SERVER}    ${ADMIN USER}    ${DUBBO WEB API URL}

*** Test Cases ***
Test Flow Task By People For Inquireing
    [Documentation]    接口自动化, 测试"首次调查"按人员分配

    log     设置首次调查的人员
    flow setup by people for inquireing   刘鹏测试  刘鹏测试2   刘鹏测试3
    Test Flow Task For Inquireing

Test Flow Task By People For First Verify
    [Documentation]    接口自动化, 测试"一审"按人员分配

    log     设置首次调查的人员
    flow setup by people for inquireing   刘鹏测试  刘鹏测试2   刘鹏测试3

    log     设置一审的人员
    flow setup by people for inquire success  刘鹏测试  刘鹏测试2   刘鹏测试3
    test flow task for first verify

Test Flow Task By People For Second Verify
    [Documentation]    接口自动化, 测试"二审"按人员分配

    log     设置首次调查的人员
    flow setup by people for inquireing   刘鹏测试  刘鹏测试2   刘鹏测试3
    log     设置一审的人员
    flow setup by people for inquire success  刘鹏测试  刘鹏测试2   刘鹏测试3
    log     设置二审的人员
    flow setup by people for first verify success  刘鹏测试2   刘鹏测试3
    test flow task for second verify

Test Flow Task By People For Third Verify
    [Documentation]    接口自动化, 测试"上签"按人员分配

    log     设置首次调查的人员
    flow setup by people for inquireing   刘鹏测试  刘鹏测试2   刘鹏测试3
    log     设置一审的人员
    flow setup by people for inquire success  刘鹏测试  刘鹏测试2   刘鹏测试3
    log     设置二审的人员
    flow setup by people for first verify success  刘鹏测试2   刘鹏测试3
    log     设置上签的人员
    flow setup by people for second verify success  刘鹏测试    刘鹏测试3
    test flow task for third verify

Test Flow Task By Role For Inquireing
    [Documentation]    接口自动化, 测试"首次调查"按角色分配

    Set flow setup by role
    Test Flow Task For Inquireing

Test Flow Task By Role For First Verify
    [Documentation]    接口自动化, 测试"一审"按角色分配

    Set flow setup by role
    Test Flow Task For First Verify

Test Flow Task By Role For Second Verify
    [Documentation]    接口自动化, 测试"二审"按角色分配
    Set flow setup by role
    Test Flow Task For Second Verify

Test Flow Task By Role For Third Verify
    [Documentation]    接口自动化, 测试"上签"按角色分配
    Set flow setup by role
    Test Flow Task For Third Verify

*** Keywords ***
Set flow setup by role
    log     设置首次调查的角色
    assign verify user to mul roles  刘鹏测试   &{ROLE NAME AND ROLE ID}[调查人员]  &{ROLE NAME AND ROLE ID}[审核人员]  &{ROLE NAME AND ROLE ID}[管理员]
    assign verify user to mul roles  刘鹏测试2   &{ROLE NAME AND ROLE ID}[调查人员]  &{ROLE NAME AND ROLE ID}[审核人员]  &{ROLE NAME AND ROLE ID}[审核经理]
    assign verify user to mul roles  刘鹏测试3   &{ROLE NAME AND ROLE ID}[调查人员]  &{ROLE NAME AND ROLE ID}[审核人员]  &{ROLE NAME AND ROLE ID}[审核经理]  &{ROLE NAME AND ROLE ID}[管理员]
    flow setup by role for inquireing  &{ROLE NAME AND ROLE ID}[调查人员]
    flow setup by role for inquire success  &{ROLE NAME AND ROLE ID}[审核人员]
    flow setup by role for first verify success  &{ROLE NAME AND ROLE ID}[审核经理]
    flow setup by role for second verify success  &{ROLE NAME AND ROLE ID}[管理员]

Test Flow Task For Inquireing
    log     产生新的进件
    populate task by nick names  auto_01    auto_02    auto_03

    log     验证分配到首次调查的进件
    verify pending job  刘鹏测试    auto_01     首次调查
    verify pending job  刘鹏测试2    auto_02     首次调查
    verify pending job  刘鹏测试3    auto_03     首次调查


Test Flow Task For First Verify
    log     分配首次调查的进件
    populate task by nick names  auto_01    auto_02    auto_03

    log     将auto_01调查通过
    commit to first verify   刘鹏测试  auto_01
    sleep  1
    log     验证auto_01分配到了一审，其他进件依然在首次调查节点
    verify pending job  刘鹏测试    auto_01     待一审
    verify done job  刘鹏测试    auto_01     首次调查
    verify involved job  刘鹏测试    auto_01     首次调查
    verify pending job  刘鹏测试2    auto_02     首次调查
    verify pending job  刘鹏测试3    auto_03     首次调查

    log     将auto_02调查通过
    commit to first verify   刘鹏测试2  auto_02
    sleep  1
    log     验证auto_02分配到了一审，其他进件依然在首次调查节点
    verify pending job  刘鹏测试    auto_02     待一审
    verify done job  刘鹏测试2    auto_02     首次调查
    verify involved job  刘鹏测试2    auto_02     首次调查
    verify pending job  刘鹏测试    auto_01     待一审
    verify pending job  刘鹏测试3    auto_03     首次调查

    log     将auto_03调查通过
    commit to first verify   刘鹏测试3  auto_03
    sleep  1
    log     验证auto_03分配到了一审，没有进件在首次调查节点
    verify pending job  刘鹏测试2    auto_03     待一审
    verify done job  刘鹏测试3    auto_03     首次调查
    verify involved job  刘鹏测试3    auto_03     首次调查
    verify pending job  刘鹏测试    auto_01     待一审
    verify pending job  刘鹏测试    auto_02     待一审

Test Flow Task For Second Verify
    log     分配首次调查的进件
    populate task by nick names  auto_01    auto_02    auto_03
    log     将auto_01调查通过
    commit to first verify   刘鹏测试  auto_01
    sleep  1
    log     将auto_02调查通过
    commit to first verify   刘鹏测试2  auto_02
    sleep  1
    log     将auto_03调查通过
    commit to first verify   刘鹏测试3  auto_03
    sleep  1

    log     将auto_01通过一审
    commit to second verify  刘鹏测试   auto_01
    sleep  1
    log     验证将auto_01分给了刘鹏测试3
    verify pending job  刘鹏测试3   auto_01    二审
    verify done job  刘鹏测试   auto_01     首次调查
    verify done job  刘鹏测试   auto_01     待一审
    verify involved job  刘鹏测试   auto_01     待一审

    log     将auto_02通过一审
    commit to second verify  刘鹏测试   auto_02
    sleep  1
    log     验证将auto_02分给了刘鹏测试2
    verify pending job  刘鹏测试2   auto_02    二审
    verify done job  刘鹏测试   auto_02     待一审
    verify involved job  刘鹏测试   auto_02     待一审

    log     将auto_03通过一审
    commit to second verify  刘鹏测试2   auto_03
    sleep  1
    log     验证将auto_03分给了刘鹏测试3
    verify pending job  刘鹏测试3   auto_03    二审
    verify done job  刘鹏测试2   auto_03     待一审
    verify involved job  刘鹏测试2   auto_03     待一审

Test Flow Task For Third Verify
    log     分配首次调查的进件
    populate task by nick names  auto_01    auto_02    auto_03
    log     将auto_01调查通过
    commit to first verify   刘鹏测试  auto_01
    sleep  1
    log     将auto_02调查通过
    commit to first verify   刘鹏测试2  auto_02
    sleep  1
    log     将auto_03调查通过
    commit to first verify   刘鹏测试3  auto_03
    sleep  1
    log     将auto_01通过一审
    commit to second verify  刘鹏测试   auto_01
    sleep  1
    log     将auto_02通过一审
    commit to second verify  刘鹏测试   auto_02
    sleep  1
    log     将auto_03通过一审
    commit to second verify  刘鹏测试2   auto_03
    sleep  1

    log     将auto_01通过二审，进入上签
    commit to pass second verify  刘鹏测试3   5001  auto_01
    sleep  1
    log     验证auto_01分给了刘鹏测试
    verify pending job  刘鹏测试   auto_01   上签
    verify done job  刘鹏测试3      auto_01     二审
    verify involved job  刘鹏测试3      auto_01     二审

    log     将auto_02通过二审，进入上签
    commit to pass second verify  刘鹏测试2   5001  auto_02
    sleep  1
    log     验证auto_01分给了刘鹏测试
    verify pending job  刘鹏测试   auto_02   上签
    verify done job  刘鹏测试2      auto_02     二审
    verify involved job  刘鹏测试2      auto_02     二审

    log     将auto_03通过二审，进入上签
    commit to pass second verify  刘鹏测试3   5001  auto_03
    sleep  1
    log     验证auto_03分给了刘鹏测试3
    verify pending job  刘鹏测试3   auto_03   上签
    verify done job  刘鹏测试3      auto_03     二审
    verify involved job  刘鹏测试3      auto_03     二审

    log     开始验证任务数
    ${task count} =    get pending task count  刘鹏测试
    should be equal as integers  ${task count}  2   刘鹏测试应该有2个待办任务
    ${task count} =    get done task count  刘鹏测试
    should be equal as integers  ${task count}  3   刘鹏测试应该有3个办结任务
    ${task count} =    get involved task count  刘鹏测试
    should be equal as integers  ${task count}  2   刘鹏测试应该有2个我参与的进件任务

    ${task count} =    get pending task count  刘鹏测试2
    should be equal as integers  ${task count}  0   刘鹏测试2应该没有待办任务
    ${task count} =    get done task count  刘鹏测试2
    should be equal as integers  ${task count}  3   刘鹏测试2应该有3个办结任务
    ${task count} =    get involved task count  刘鹏测试2
    should be equal as integers  ${task count}  2   刘鹏测试2应该有2个我参与的进件任务

    ${task count} =    get pending task count  刘鹏测试3
    should be equal as integers  ${task count}  1   刘鹏测试3应该有1个待办任务
    ${task count} =    get done task count  刘鹏测试3
    should be equal as integers  ${task count}  3   刘鹏测试3应该有3个办结任务
    ${task count} =    get involved task count  刘鹏测试3
    should be equal as integers  ${task count}  2   刘鹏测试3应该有2个我参与的进件任务
