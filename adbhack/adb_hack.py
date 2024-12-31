import argparse
import subprocess


def adb_connect_test(tag,timeout):
    successip = []
    for targes in tag:
        print(f"[*]使用adb尝试连接到 {targes}....")
        try:
            connect = subprocess.check_output(["adb", "connect", targes], text=True, timeout=timeout)
            if "connected" in connect:
                successip.append(targes)
                print(f"[*]连接成功 {targes}")
                exec_run = subprocess.run(["adb", "-s", targes, "shell", "id"], capture_output=True, text=True)
                if exec_run.stdout.strip():
                    print(f"{targes} 命令回显: {exec_run.stdout.strip()}")
                else:
                    print(f"{targes} 没有回显: {exec_run.stdout}")
            else:
                print(f"[-]连接失败 {targes}")
        except Exception as e:
            print(f"[-]连接失败或超时 {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量检测adb连接情况命令')
    parser.add_argument("-l", "--list", help="包含ip端口的列表ip:port")
    parser.add_argument("-u", "--url", help="单个ip加端口")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="设置超时默认三秒")

    args = parser.parse_args()
    if args.url is not None:
        list = [args.url]  # 单个 URL 转换为列表
        adb_connect_test(list)

    if args.list:
        with open(args.list, 'r') as f:
            ip_list = [line.strip() for line in f]
        if not ip_list:
            print("没有输入,使用--list 输入列表 需要本地环境变量安装有adb")
        else:
            adb_connect_test(ip_list, timeout=args.timeout)

    devices = subprocess.run(["adb", "devices"], text=True, timeout=args.timeout)
    print(f"[*]当前连接信息{devices.stdout}")