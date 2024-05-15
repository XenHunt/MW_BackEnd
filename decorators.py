from parser import parserId

from main import jwt
from orm import RevokedTokenModel


@jwt.token_in_blocklist_loader
def not_blacklisted_token(header, decrypted_token):
    # Создание файла - для теста
    # ic(decrypted_token)
    # with open("blacklist.txt", "a") as f:
    #     f.write(decrypted_token["jti"] + "\n")
    data = parserId.parse_args()
    return RevokedTokenModel.is_jwt_in_blacklisted(
        decrypted_token["jti"], data["uid"], data["system_string"]
    )
