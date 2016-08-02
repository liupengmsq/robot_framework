*** Settings ***
Resource    ../resources/resource.robot
Library      ../VerifyCoupon.py
Test Setup  my setup
Test Teardown  my cleanup


*** Test Cases ***
Test create fixed time coupon batch
    [Documentation]    接口自动化, 测试创建固定时间的优惠券批次的接口
    create fixed time coupon batch

Test create fixed length coupon batch
    [Documentation]    接口自动化, 测试创建固定时长的优惠券批次的接口
    create fixed length coupon batch

#Test system fixed time coupon grant
#    system fixed time coupon grant

#Test system fixed length coupon grant
#    system fixed length coupon grant

#Test disable and in time range system fixed length coupon grant
#    disable and in time range system fixed length coupon grant

Test disable and not in time range system fixed length coupon grant
    [Documentation]    接口自动化, 禁用一个固定时长的优惠券批次, 测试系统不会自动分发优惠券
    disable and not in time range system fixed length coupon grant

#Test disable and in time range system fixed time coupon grant
#    disable and in time range system fixed time coupon grant

Test disable and not in time range system fixed time coupon grant
    [Documentation]    接口自动化, 禁用一个固定时间的优惠券批次, 测试系统不会自动分发优惠券
    disable and not in time range system fixed time coupon grant
