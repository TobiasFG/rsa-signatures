import requests as requests
import secrets
import base64
import json

# set LOCAL to localhost string on port 5000
LOCAL = 'http://127.0.0.1:5000'
LOCAL_PK = LOCAL + '/pk/'
LOCAL_SIGN = LOCAL + '/sign_random_document_for_students/'
LOCAL_QUOTE = LOCAL + '/quote/'

TEST_MESSAGE = 'Hello, World!'
TEST_MESSAGE_ILLEGAL = 'You got a 12 because you are an excellent student! :)'

# find the Type of any variable
def typeOf(var):
    return type(var).__name__

# HOW TO DO THE TASK
# 1. Get the public key (e,N) from server.
# 2. Compute r (random integer) between 0 and N.
# 3. Create your actual message M you want to hide from server.
# 4. Create M' such that M' = M*r^e mod N
# 5. Send M' to server and get signature S' for M'
# 6. Compute S = S'*r^-1 mod N


def get_public_key():
    response = requests.get(LOCAL_PK)
    if response.status_code != 200:
        print('Error: Could not get public key something went wrong')
        return None
    return response.json()['N'], response.json()['e']

def sign_hex(hex): ## WORKS
    response = requests.get(LOCAL_SIGN + hex + '/')
    if response.status_code != 200: return None
    if response.text == '<p>Haha, nope!</p>': return 'Haha, nope!'
    
    print(response.json())
    signature = response.json()['signature']
    if (hex == response.json()['msg']):
        print('Messages match!')

    return signature

def sign_string(msg: str): ## WORKS
    msg_hex = msg.encode('utf-8').hex()
    return sign_hex(msg_hex)

print(sign_string(TEST_MESSAGE))

def string_to_hex(string):
    return string.encode('utf-8').hex()

def create_r(n):
    return secrets.randbelow(n)

def create_M_prime(msg: str, r, e, N):  # compute M' = M*r^e mod N
    M = int.from_bytes(msg.encode(), 'big')
    M_prime = (M * pow(r, e, N)) % N
    return hex(M_prime)[2:]

def json_to_cookie(j: str) -> str:
    """Encode json data in a cookie-friendly way using base64."""
    # The JSON data is a string -> encode it into bytes
    json_as_bytes = j.encode()
    # base64-encode the bytes
    base64_as_bytes = base64.b64encode(json_as_bytes, altchars=b'-_')
    # b64encode returns bytes again, but we need a string -> decode it
    base64_as_str = base64_as_bytes.decode()
    return base64_as_str

def get_quote(msg, S):
    reee = json.dumps({'msg': msg, 'signature': S})
    cookie = {'grade': json_to_cookie(reee)}

    response = requests.get(LOCAL_QUOTE, cookies=cookie)
    if response.status_code != 200: return None
    if response.text.__contains__("<quote>"): return response.text
    return "Haha, nope!"
    

def launch_attack():
    keys = get_public_key()
    N = keys[0]
    e = keys[1]
    r = create_r(N)
    M_prime_hex = create_M_prime(TEST_MESSAGE_ILLEGAL, r, e, N)
    S_prime = sign_hex(M_prime_hex)
    S_prime = bytes.fromhex(S_prime)
    S_prime = int.from_bytes(S_prime, 'big')
    S = S_prime*pow(r, -1, N) % N
    S = hex(S)[2:]

    print(get_quote(string_to_hex(TEST_MESSAGE_ILLEGAL), S))
    


launch_attack()