#!/bin/bash

IPMI_HOST="172.16.110.76"
IPMI_USER="neko"

if [ -z "$IPMI_PASS" ]; then
    echo "环境变量 IPMI_PASS 未设置，请先设置密码。"
    exit 1
fi

if ! command -v ipmitool &> /dev/null; then
    echo "ipmitool 未安装，请先安装。"
    exit 1
fi

function stop_auto_control() {
    echo "停止风扇自动控制..."
    ipmitool -I lanplus -H "$IPMI_HOST" -U "$IPMI_USER" -P "$IPMI_PASS" raw 0x30 0x30 0x01 0x00
    if [ $? -eq 0 ]; then
        echo "自动控制已停止，切换为手动控制模式。"
    else
        echo "停止自动控制失败，请检查设备状态。"
        exit 1
    fi
}

function set_fan_speed() {
    local speed=$1
    echo "设置风扇转速为 $speed%..."
    ipmitool -I lanplus -H "$IPMI_HOST" -U "$IPMI_USER" -P "$IPMI_PASS" raw 0x30 0x30 0x02 0xff "$speed"
    if [ $? -eq 0 ]; then
        echo "风扇转速设置成功！"
    else
        echo "风扇转速设置失败！"
    fi
}

function main_menu() {
    echo "请选择风扇转速："
    echo "1) 10%"
    echo "2) 15%"
    echo "3) 30%"
    echo "4) 100%"
    echo "5) 恢复自动模式"
    echo "6) 退出"

    read -p "输入选项 [1-6]: " choice
    case $choice in
        1)
            stop_auto_control
            set_fan_speed 0x0a # 10%
            ;;
        2)
            stop_auto_control
            set_fan_speed 0x0f # 15%
            ;;
        3)
            stop_auto_control
            set_fan_speed 0x1e # 30%
            ;;
        4)
            stop_auto_control
            set_fan_speed 0x64 # 100%
            ;;
        5)
            echo "恢复自动控制模式..."
            ipmitool -I lanplus -H "$IPMI_HOST" -U "$IPMI_USER" -P "$IPMI_PASS" raw 0x30 0x30 0x01 0x01
            ;;
        6)
            echo "退出脚本。"
            exit 0
            ;;
        *)
            echo "无效选项，请重试。"
            main_menu
            ;;
    esac
}

main_menu
