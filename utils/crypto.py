"""
APIキーの暗号化・復号化ユーティリティ
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path


class APIKeyManager:
    """APIキーの暗号化管理"""

    def __init__(self):
        # マシン固有のキーを生成（ユーザー名とPCホスト名から）
        self.key = self._generate_machine_key()
        self.cipher = Fernet(self.key)

    def _generate_machine_key(self) -> bytes:
        """マシン固有の暗号化キーを生成"""
        # ユーザー名とコンピュータ名を組み合わせて固有のソルトを作成
        username = os.environ.get('USERNAME', 'default')
        computername = os.environ.get('COMPUTERNAME', 'default')
        salt = f"{username}_{computername}_botan_2025".encode()

        # パスワードベースのキー導出
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )

        # 固定のマスターパスワード（コードに埋め込み）
        password = b"BotanAiTESystem2025_SecureKey"
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt_api_key(self, api_key: str) -> str:
        """APIキーを暗号化"""
        if not api_key:
            return api_key

        # APIキーのパターンをチェック（各種サービスのAPIキー形式）
        api_patterns = [
            'sk_',      # OpenAI, ElevenLabs
            'sk-',      # OpenAI alternative format
            'key_',     # General API key
            'api_',     # General API key
            'pk_',      # Public key (should also be protected)
            'secret_',  # Secret key
            'token_',   # API token
        ]

        # 既に暗号化されている場合はそのまま返す
        if api_key.startswith('ENC_'):
            return api_key

        # APIキーパターンに該当するか、20文字以上の英数字記号の場合は暗号化
        should_encrypt = any(api_key.lower().startswith(pattern) for pattern in api_patterns)
        if not should_encrypt and len(api_key) >= 20 and not ' ' in api_key:
            # 長い文字列で空白を含まない場合もAPIキーの可能性が高い
            should_encrypt = True

        if not should_encrypt:
            return api_key

        encrypted = self.cipher.encrypt(api_key.encode())
        # Base64エンコードして保存しやすくする
        return f"ENC_{base64.urlsafe_b64encode(encrypted).decode()}"

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """APIキーを復号化"""
        if not encrypted_key or not encrypted_key.startswith('ENC_'):
            return encrypted_key  # 暗号化されていない場合はそのまま返す

        try:
            # ENC_プレフィックスを除去してBase64デコード
            encrypted_data = base64.urlsafe_b64decode(encrypted_key[4:])
            decrypted = self.cipher.decrypt(encrypted_data)
            return decrypted.decode()
        except Exception as e:
            print(f"[Warning] Failed to decrypt API key: {e}")
            return ""


def setup_encrypted_env():
    """既存の.envファイルのAPIキーを暗号化"""

    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        print("No .env file found")
        return

    manager = APIKeyManager()

    # .envファイルを読み込み
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    new_lines = []

    # APIキーとして扱う環境変数名のパターン
    api_key_patterns = [
        '_API_KEY',
        '_API_TOKEN',
        '_SECRET',
        '_TOKEN',
        '_KEY',
        'OPENAI_',
        'ANTHROPIC_',
        'CLAUDE_',
        'GEMINI_',
        'HUGGINGFACE_',
    ]

    for line in lines:
        if '=' in line and not line.startswith('#'):
            parts = line.strip().split('=', 1)
            if len(parts) == 2:
                key_name = parts[0].strip()
                value = parts[1].strip()

                # 環境変数名がAPIキーパターンに該当するかチェック
                is_api_key = any(pattern in key_name.upper() for pattern in api_key_patterns)

                if is_api_key and value and not value.startswith('ENC_'):
                    # 暗号化を試みる
                    original_value = value
                    encrypted = manager.encrypt_api_key(value)

                    # 実際に暗号化された場合のみ更新
                    if encrypted != original_value:
                        new_line = f"{key_name}={encrypted}\n"
                        new_lines.append(new_line)
                        modified = True
                        display_value = original_value[:10] if len(original_value) > 10 else original_value[:5]
                        print(f"Encrypted {key_name}: {display_value}...")
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    # 変更があった場合は保存
    if modified:
        # バックアップを作成
        backup_path = env_path.with_suffix('.env.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Backup created: {backup_path}")

        # 暗号化版を保存
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("API key encrypted in .env file")
    else:
        print("No changes needed (already encrypted or no API key found)")


def get_api_key(key_name: str) -> str:
    """環境変数からAPIキーを取得（自動復号化）

    Args:
        key_name: 環境変数名

    Returns:
        復号化されたAPIキー（暗号化されている場合）または元の値
    """
    encrypted_key = os.getenv(key_name)
    if not encrypted_key:
        return ""

    # 暗号化されている場合は復号化
    if encrypted_key.startswith('ENC_'):
        manager = APIKeyManager()
        return manager.decrypt_api_key(encrypted_key)

    return encrypted_key


def encrypt_all_api_keys():
    """すべてのAPIキーを一括暗号化"""
    setup_encrypted_env()


def get_secure_env(key_name: str, default: str = "") -> str:
    """環境変数を安全に取得（APIキーは自動復号化）

    Args:
        key_name: 環境変数名
        default: デフォルト値

    Returns:
        環境変数の値（APIキーの場合は復号化されたもの）
    """
    value = os.getenv(key_name, default)

    if value and value.startswith('ENC_'):
        manager = APIKeyManager()
        return manager.decrypt_api_key(value)

    return value


if __name__ == "__main__":
    # コマンドラインから実行された場合は暗号化セットアップ
    print("Setting up API key encryption...")
    setup_encrypted_env()

    # テスト
    print("\nTesting decryption...")
    test_key = get_api_key()
    if test_key and test_key.startswith('sk_'):
        print(f"Decryption successful: {test_key[:10]}...")
    else:
        print("Decryption failed or no key found")