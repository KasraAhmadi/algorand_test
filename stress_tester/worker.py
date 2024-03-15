from typing import Dict, Any
from algosdk import account,mnemonic,transaction
from utils import get_accounts, get_algod_client, get_kmd_client
import time
import csv
import multiprocessing 
from multiprocessing import Queue

def create_array(number):
    arr = []
    for i in range(number):
        arr.append(i)
    return arr
def read_file():
    addresses = []
    with open('Addresses.csv', mode='r') as file:
        address_reader = csv.reader(file)
        for item in address_reader:
            try:
                addresses.append(item[1])
            except Exception:
                pass
    return addresses
def sign(ip,algod_port,algod_token,kmd_port,kmd_token,address_receiver,total,wallet,password):
    #Initialization
    ALGOD_ADDRESS = "http://"+ip
    ALGOD_PORT = algod_port
    ALGOD_URL = f"{ALGOD_ADDRESS}:{algod_port}"
    ALGOD_TOKEN = algod_token
    KMD_URL = f"{ALGOD_ADDRESS}:{kmd_port}"
    algod_client = get_algod_client(ALGOD_URL,ALGOD_TOKEN)
    accts = get_accounts(KMD_URL,kmd_token,wallet,password)
    address_sender = accts[0].address
    print("worker address is {address}".format(address=address_sender))
    sk_sender = accts[0].private_key
    suggested_params = algod_client.suggested_params()
    stx_array = []
    start_time = time.time()
    #Create and Sign transactions
    for i in range(total):
        txn_1 = transaction.PaymentTxn(address_sender, suggested_params, address_receiver, i)
        stxn_1 = txn_1.sign(sk_sender)
        stx_array.append(stxn_1)
    return [algod_client,stx_array]
def send_trans_client(name,algod_client,stx_array,queue):
    faulty_transactions = 0
    #Send the transaction

    for item in stx_array:
        try:
            tx_id = algod_client.send_transaction(item)
        except Exception as e:
            print(e)
            faulty_transactions = faulty_transactions + 1
            pass
    print(name + " Finished")
    data = [len(stx_array)-faulty_transactions,faulty_transactions]
    queue.put(data)


if __name__ == "__main__": 
    transactions_number = 1000
    queue = Queue()
    # s0 = sign("8080","dd9b9c47a4a09df18976bc93237c99e3e3d2c4c26f60518572267e71dfe1d21d","7833","5e5051fe7357107a383f6bf14e710278a6ebaf151983b2e50872e6d52ad6663b","6DQ7JQN6T52CREL6PDXTKNECZTJBUN6H6T6FIMUBIOCG26PQC6QPE7D6HM",transactions_number,"Melodyes","Me1091372")
    s1 = sign("44.199.244.229","8080","4e831ee42bc9a01c6abf12044298c54d14fb3dbcdff283dd847d2054925ef39d","7833","a101bdf50463a1ae9d188c86c024b2e2ef8bb888f99a4f19d94b8a7abf348622","DO5KZDNFSNX24YBGHLQRPBVWIZM62FXZT2QD5V4CQ3H2QXDISKOBUGUL6M",transactions_number,"molud","molud")
    # s2 = sign("8082","1111111111111111111111111111111111111111111111111111111111111111","9092","caa0d763e906d90a3629fe0756e938f040ac2cb5b5d1b882fd8002dabfac2ff9","6DQ7JQN6T52CREL6PDXTKNECZTJBUN6H6T6FIMUBIOCG26PQC6QPE7D6HM",transactions_number,"molud","molud")
    # s3 = sign("8083","1111111111111111111111111111111111111111111111111111111111111111","9093","e14dd6ac2103b022ce2aa55cdfdbbde86b34715fa30a14b88d6b5e52b70fa2fe","6DQ7JQN6T52CREL6PDXTKNECZTJBUN6H6T6FIMUBIOCG26PQC6QPE7D6HM",transactions_number,"molud","molud")
    # p0 = multiprocessing.Process(target=send_trans_client,args=("p0",s0[0],s0[1],queue))
    p1 = multiprocessing.Process(target=send_trans_client,args=("p1",s1[0],s1[1],queue))
    # p2 = multiprocessing.Process(target=send_trans_client,args=("p2",s2[0],s2[1],queue))
    # p3 = multiprocessing.Process(target=send_trans_client,args=("p3",s3[0],s3[1],queue))

    # p0.start()
    p1.start()
    # p2.start()
    # p3.start()
    start_time = time.time()


    # p0.join()
    p1.join()
    # p2.join()
    # p3.join()
    end_time = time.time()
    whole_transactions = 0
    whole_faulty_transactions = 0
    while queue.empty() != True:
        data = queue.get()
        whole_transactions = whole_transactions + data[0]
        whole_faulty_transactions = whole_faulty_transactions + data[1]
    print("Number of transactions: %s\nWhole Time %s\nFaulty transaction number: %s\nTPS: %s" % (whole_transactions,end_time-start_time,whole_faulty_transactions,(whole_transactions)/(end_time-start_time)))




