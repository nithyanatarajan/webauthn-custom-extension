from pydantic import BaseModel


class RegisterBeginRequest(BaseModel):
    username: str


class RegisterCompleteRequest(BaseModel):
    attestation: dict
    challenge_token: str


class AuthBeginRequest(BaseModel):
    username: str


class AuthCompleteRequest(BaseModel):
    assertion: dict
    challenge_token: str


class BeginResponse(BaseModel):
    publicKey: dict
    challenge_token: str


class CompleteResponse(BaseModel):
    status: str
