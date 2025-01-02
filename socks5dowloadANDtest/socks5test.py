#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import socks
import socket
import concurrent.futures  # 用于多线程


def test_socks5_proxy(proxy_host: str, proxy_port: int,
                      test_host: str = "www.google.com",
                      test_port: int = 80,
                      timeout: int = 1) -> bool:
    """
    测试单个SOCKS5代理是否可用。
    :param proxy_host: 代理服务器IP或域名
    :param proxy_port: 代理服务器端口
    :param test_host: 用于测试连接的目标主机
    :param test_port: 用于测试连接的目标端口
    :param timeout: 超时时间（默认为1秒）
    :return: True表示可用，False表示不可用
    """
    sock = socks.socksocket()
    sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
    sock.settimeout(timeout)
    try:
        # 连接到测试主机
        sock.connect((test_host, test_port))

        # 简单发送一个请求 (HEAD 请求)
        request_data = f"HEAD / HTTP/1.1\r\nHost: {test_host}\r\n\r\n"
        sock.sendall(request_data.encode("utf-8"))

        # 接收响应
        response = sock.recv(1024)
        # 判断响应里是否存在 HTTP 头
        return b"HTTP/" in response
    except Exception as e:
        # 如果需要可打印调试信息
        # print(f"[SOCKS5 Error] {proxy_host}:{proxy_port} -> {e}")
        return False
    finally:
        sock.close()


def test_http_proxy(proxy_host: str, proxy_port: int,
                    test_url: str = "http://www.google.com",
                    timeout: int = 1) -> bool:
    """
    测试单个HTTP代理是否可用。
    :param proxy_host: 代理服务器IP或域名
    :param proxy_port: 代理服务器端口
    :param test_url: 用于测试连接的URL（必须带 http:// 前缀）
    :param timeout: 超时时间（默认为1秒）
    :return: True表示可用，False表示不可用
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        # 连接到HTTP代理
        sock.connect((proxy_host, proxy_port))

        # 通过HTTP代理访问 test_url
        # 这里使用 HEAD 方法以减少数据量，也可改成 GET
        request_data = (
            f"HEAD {test_url} HTTP/1.1\r\n"
            f"Host: www.google.com\r\n"
            f"User-Agent: python-proxy-tester\r\n"
            f"Connection: close\r\n\r\n"
        )
        sock.sendall(request_data.encode("utf-8"))

        # 接收部分响应即可
        response = sock.recv(1024)
        # 如果能拿到 HTTP/ 标记，就认为这是一个可用的 HTTP 代理
        return b"HTTP/" in response
    except Exception as e:
        # 如果需要可打印调试信息
        # print(f"[HTTP Error] {proxy_host}:{proxy_port} -> {e}")
        return False
    finally:
        sock.close()


def test_proxy_line(line: str) -> tuple[str, bool, str]:
    """
    针对单行 (host:port) 的代理字符串进行测试。
    依次测试 SOCKS5 → HTTP。

    :return: (代理字符串, 是否可用, 协议类型)
             协议类型可为 "socks5" / "http" / "" (失败)
    """
    line = line.strip()
    if not line:
        return ("", False, "")

    try:
        host, port_str = line.split(":")
        port = int(port_str)
    except ValueError:
        print(f"[格式错误] {line}")
        return (line, False, "")

    # 先测试 SOCKS5
    if test_socks5_proxy(host, port):
        return (f"{host}:{port}", True, "socks5")
    else:
        # 如果 SOCKS5 不成功，则测试 HTTP
        if test_http_proxy(host, port):
            return (f"{host}:{port}", True, "http")
        else:
            return (f"{host}:{port}", False, "")


def main():
    parser = argparse.ArgumentParser(description="批量测试 SOCKS5/HTTP 代理可用性（多线程版）")
    parser.add_argument("-l", "--list", required=True,
                        help="包含代理列表的文件，按行写入，每行格式 host:port")
    parser.add_argument("-t", "--threads", type=int, default=10,
                        help="线程数（默认10）")
    args = parser.parse_args()

    # 读取代理列表文件
    with open(args.list, "r", encoding="utf-8") as f:
        proxy_lines = [line.strip() for line in f if line.strip()]

    # 保存成功的代理
    success_proxies = []

    # 使用线程池并发测试
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_line = {
            executor.submit(test_proxy_line, line): line for line in proxy_lines
        }

        for future in concurrent.futures.as_completed(future_to_line):
            proxy_str = future_to_line[future]  # 提交时的原始行
            try:
                result_proxy_str, is_success, proto = future.result()
            except Exception as exc:
                print(f"[错误] {proxy_str} 测试时出现异常: {exc}")
                continue

            if is_success:
                if proto == "socks5":
                    proxy_with_scheme = f"socks5://{result_proxy_str}"
                else:
                    proxy_with_scheme = f"http://{result_proxy_str}"

                print(f"[成功][{proto.upper()}] {proxy_with_scheme}")
                success_proxies.append(proxy_with_scheme)
            else:
                print(f"[失败] {result_proxy_str}")

    # 测试结束后，打印/使用“测试成功”的代理列表
    print("\n========= 测试成功的代理列表 =========")
    for proxy in success_proxies:
        print(proxy)


if __name__ == "__main__":
    main()
