import requests as requests

# set LOCAL to localhost string on port 5000
LOCAL = 'http://127.0.0.1:5000'
LOCAL_PK = LOCAL + '/pk/'
LOCAL_SIGN = LOCAL + '/sign_random_document_for_students/'
SIGN_URL = 'http://localhost:5000/sign_random_document_for_students'
QUOTE_URL = 'http://localhost:5000/quote/'

TEST_MESSAGE = 'Hello, World!'
TEST_MESSAGE_ILLEGAL = 'grade, 12, twelve, tolv'

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


###########################   ERROR ABOVE  ###########################

# The hex_msg will inevitably contain a "12" somewhere in the big message.
# How is it possible to omit this? or is there a mistake with the assignment?

######################################################################

def sign_msg(msg: str): ## WORKS
    msg_hex = msg.encode('utf-8').hex()

    response = requests.get(LOCAL_SIGN + msg_hex + '/')
    if response.status_code != 200: return None
    if response.text == '<p>Haha, nope!</p>': return 'Haha, nope!'
    
    signature = response.json()['signature']
    if (msg_hex == response.json()['msg']):
        print('Messages match!')

    return signature


#print(sign_msg(TEST_MESSAGE))
#print(sign_msg(TEST_MESSAGE_ILLEGAL))

def create_M_prime(msg, r, e, N):  # compute M' = M*r^e mod N
    print("msg is of type: ", typeOf(msg), " and value: ", msg)
    M = int.from_bytes(msg.encode(), 'big')
    print("M is of type: ", typeOf(M), " and value: ", M)
    M_prime = (M * pow(r, e, N)) % N
    # make M_prime a type string
    M_prime = hex(M_prime)[2:]

    print("M_prime is of type: ", typeOf(M_prime), " and value: ", M_prime)
    return M_prime


def create_S(S_prime, r, N):  # compute S = S'*r^-1 mod N
    S = hex(int(S_prime, 16) * pow(r, N - 2, N) % N)[2:]
    return S


def launch_attack(message):
    # get public key
    N, e = get_public_key(LOCAL)
    #print('This is the publickey: N=', N, ' and e=', e)

    # compute r (random integer) between 0 and N
    r = secrets.randbelow(N)
    #print('This is r: ', r)

    # compute M'
    M_prime = create_M_prime(message, r, e, N)
    #print('This is M_prime: ', M_prime)

    # send M' to server and get signature S' for M'
    S_prime = sign_msg(M_prime)
    print('This is S_prime: ', S_prime)

    # compute S = S'*r^-1 mod N
    # Tried something else: S = pow(r, -1, N) * int(hex(S_prime), 16)
    S = hex(int(S_prime, 16) * pow(r, N - 2, N) % N)[2:]
    print('This is S: ', S)

    # send M and S to server and get the flag
    response = requests.get(
        LOCAL + '/quote/', cookies={'grade': json.dumps({'msg': M, 'signature': S})})

    # check if response is valid
    if response.status_code != 200:
        print('Error: Could not get flag something went wrong')
        return None

    # if response is valid return the flag
    return response.text


#launch_attack(TEST_VALID_MESSAGE)
# print('This is the publickey: ', get_public_key(LOCAL))
# print('This is the signed message: ', sign_msg("jeg er gud"))
