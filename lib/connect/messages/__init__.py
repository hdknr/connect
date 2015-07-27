from connect.messages import (
    discovery, reg, auth, token, id_token, userinfo,
)
from jose.base import BaseObject

BaseObject = BaseObject
ProviderMeta = discovery.ProviderMeta
ClientMeta = reg.ClientMeta
ClientReg = reg.ClientReg
AuthReq = auth.AuthReq
AuthRes = auth.AuthRes
TokenRes = token.TokenRes
IdToken = id_token.IdToken
UserInfo = userinfo.UserInfo
