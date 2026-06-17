"""
爱蜜莉雅 - 交互式对话

在终端中自由输入问题，与爱蜜莉雅实时对话。
输入 /exit 或 /quit 退出。
"""

import sys
from conftest import load_system_prompt
from api_client import ApiClient


def main():
    # 将 stdin/stdout 统一为 UTF-8，与 chcp 65001 终端保持一致
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

    system_prompt = load_system_prompt()
    if not system_prompt:
        print("[错误] prompt.md 未找到或为空")
        sys.exit(1)

    try:
        client = ApiClient(system_prompt=system_prompt)
    except ValueError as e:
        print(f"[错误] {e}")
        sys.exit(1)

    print()
    print("=" * 50)
    print("  爱蜜莉雅 - 交互式对话")
    print(f"  模型: {client.model}")
    print("  输入 /exit 或 /quit 退出")
    print("=" * 50)
    print()
    # print("  爱蜜莉雅: 你好，我是爱蜜莉雅。有什么想聊的吗？")
    print()

    history = []

    while True:
        try:
            user_input = input("  你: ")
        except (EOFError, KeyboardInterrupt):
            print("\n  再见~")
            break

        if user_input.strip().lower() in ("/exit", "/quit"):
            print("  再见~")
            break

        if not user_input.strip():
            continue

        history.append({"role": "user", "content": user_input})
        reply = client.chat(history)
        history.append({"role": "assistant", "content": reply})

        print(f"  爱蜜莉雅: {reply}")
        print()


if __name__ == "__main__":
    main()
