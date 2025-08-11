from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity

from passkey_server.config import Config

rp_entity = PublicKeyCredentialRpEntity(id=Config.RP_ID, name=Config.RP_NAME)
server = Fido2Server(rp_entity)
