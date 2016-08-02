*** Settings ***
Test Setup       Open Browser To Login Page
Test Teardown    Close Browser
Resource    ../resources/resource.robot
Library     String
Library      ../VerifyLibrary.py   http://${SERVER}    ${ADMIN USER}

*** Test Cases ***
Administrator permission test
    [Documentation]    WEB UI自动化, 使用"管理员"账号登陆系统, 查看全部导航栏都应该显示, 并可以点击

    Login With Valid Account    ${ADMIN USER}   ${ADMIN PASSWORD}

    :FOR    ${node}    IN    @{TREE NODE TITLES}
    \   Click TreeNode		${node}
    \   Page Title Visible   ${node}

    Click TreeTitle     ${TREE TITLE ONLY NODE}
    Page Title Visible  ${TREE TITLE ONLY NODE}

Investigator permission test
    [Documentation]    WEB UI自动化, 使用"调查人员"账号登陆系统, 查看左侧导航栏里应该显示为: 用户查询, 待办任务, 办结任务, 我参与的进件

    log     ${VALID USER}
    log     &{DEPARTMENT NAME AND ID}[组织]
    log     &{ROLE NAME AND ROLE ID}[调查人员]
    ${response} =  UPDATE VERIFY USER ROLE     ${VALID USER}   &{DEPARTMENT NAME AND ID}[组织]   &{ROLE NAME AND ROLE ID}[调查人员]
    log     ${response}
    Login With Valid Account    ${VALID USER}   ${VALID PASSWORD}

    :FOR    ${node}    IN    @{INV TREE NODE TITLES}
    \   Click TreeNode		${node}
    \   Page Title Visible   ${node}

    :FOR    ${node}    IN    @{INV TREE NODE TITLES NOT VISIBLE}
    \   TreeNode Not Visble  ${node}
    TreeTitle Not Visble  ${TREE TITLE ONLY NODE}

Audit permission test
    [Documentation]    WEB UI自动化, 使用"审核人员"账号登陆系统, 查看左侧导航栏里应该显示为: 用户查询, 待办任务, 办结任务, 我参与的进件

    UPDATE VERIFY USER ROLE     ${VALID USER}   &{DEPARTMENT NAME AND ID}[组织]   &{ROLE NAME AND ROLE ID}[审核人员]
    Login With Valid Account    ${VALID USER}   ${VALID PASSWORD}

    :FOR    ${node}    IN    @{AUDIT TREE NODE TITLES}
    \   Click TreeNode		${node}
    \   Page Title Visible   ${node}

    Click TreeTitle     ${TREE TITLE ONLY NODE}
    Page Title Visible  ${TREE TITLE ONLY NODE}

    :FOR    ${node}    IN    @{AUDIT TREE NODE TITLES NOT VISIBLE}
    \   TreeNode Not Visble  ${node}

Audit manager permission testj
    [Documentation]    WEB UI自动化, 使用"审核经理"账号登陆系统, 查看左侧导航栏里应该显示为: 用户查询, 待办任务, 办结任务, 我参与的进件, 流程任务管理, 流程配置管理

    UPDATE VERIFY USER ROLE     ${VALID USER}   &{DEPARTMENT NAME AND ID}[组织]   &{ROLE NAME AND ROLE ID}[审核经理]
    Login With Valid Account    ${VALID USER}   ${VALID PASSWORD}

    :FOR    ${node}    IN    @{AUDIT MANAGER TREE NODE TITLES}
    \   Click TreeNode		${node}
    \   Page Title Visible   ${node}

    Click TreeTitle     ${TREE TITLE ONLY NODE}
    Page Title Visible  ${TREE TITLE ONLY NODE}

    :FOR    ${node}    IN    @{AUDIT MANAGER TREE NODE TITLES NOT VISIBLE}
    \   TreeNode Not Visble  ${node}
