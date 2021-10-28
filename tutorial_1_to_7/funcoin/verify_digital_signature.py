import nacl.encoding
import nacl.signing

# from digital sinnature
bobs_public_key = b'db5816b1d9a70cb2cdd4afbc58f80fc99ba4f3e3ecf24bb8a17caacc84a45624'

# Generate the verify_key
verify_key = nacl.signing.VerifyKey(bobs_public_key, encoder=nacl.encoding.HexEncoder)

signed_messge = b'<%"\xa0\x855:\x85>q\xf4Z|>\xa1\xdd\xc8\xb3\x89I\x98k8\'\xf2>\\)}cNtpS\xf7L\r!\xf4\xb9\xb0\x1f^\xa7\x08\x0eT\x05\xb9\xa0\x8f\xf3~\xcb\x03;o^0\xabs\x8fu\x0eSend $37 to Alice'

okay = verify_key.verify(signed_messge)

print(okay)

