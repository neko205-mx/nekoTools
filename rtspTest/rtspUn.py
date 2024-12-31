import argparse
import cv2
import time
import os

# RTSP 视频流
def test_rtsp_stream(addresses):
    successful_addresses = []

    for address in addresses:
        address = address.strip()
        if not address:
            continue
        print(f"[*] 尝试打开 RTSP 流: {address}")
        cap = None
        try:
            cap = cv2.VideoCapture(f"rtsp://{address}")

            start_time = time.time()
            while time.time() - start_time < 5:
                if cap.isOpened():
                    # 读取一帧
                    ret, frame = cap.read()
                    if ret:
                        print(f"[+] RTSP 流成功: {address}")
                        successful_addresses.append(address)

                        # 保存图片
                        output_dir = "rtsp_snapshots"
                        os.makedirs(output_dir, exist_ok=True)
                        image_path = os.path.join(output_dir, f"{address.replace(':', '_').replace('/', '_')}.jpg")
                        cv2.imwrite(image_path, frame)
                        print(f"[+] 图片已保存: {image_path}")
                        break
                    else:
                        print(f"[-] RTSP 流失败: {address} (无法读取帧)")
                        break
                else:
                    time.sleep(0.1)
            else:
                print(f"[-] RTSP 流失败: {address} (超时 5 秒)")
        except Exception as e:
            print(f"[-] RTSP 流失败: {address} ({e})")
        finally:
            if cap:
                cap.release()

    return successful_addresses

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="从文件中读取 RTSP 地址并尝试播放。")
    parser.add_argument("-l", "--list", required=True, help="包含 RTSP 地址的文本文件，每行一个地址 (格式: IP:PORT)")

    args = parser.parse_args()

    # 读取
    try:
        with open(args.list, "r") as file:
            addresses = file.readlines()
    except FileNotFoundError:
        print(f"[!] 文件 {args.list} 不存在")
        exit(1)

    # 测试
    successful_addresses = test_rtsp_stream(addresses)

    # 输出
    print("\n[+] 成功打开的 RTSP 地址:")
    for address in successful_addresses:
        print(address)