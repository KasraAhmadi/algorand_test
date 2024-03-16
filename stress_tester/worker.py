from typing import Dict, Any
from algosdk import account,mnemonic,transaction
from utils import get_accounts, get_algod_client, get_kmd_client
import time
import csv
import multiprocessing 
from multiprocessing import Queue
import sys

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
def sign(algod_port,algod_token,kmd_port,kmd_token,address_receiver,total,wallet,password):
    #Initialization
    ALGOD_ADDRESS = "http://localhost"
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
    kmd_token = ""
    algod_token = ""
    with open('/var/lib/algorand/algod.token', 'r') as file:
        algod_token = file.read()
    with open('/home/ubuntu/.algorand/testnet-v1.0/kmd-v0.5/kmd.token', 'r') as file:
        kmd_token = file.read()
    transactions_number = int(sys.argv[1])
    queue = Queue()
    s1 = sign("8080",algod_token,"7833",kmd_token,"DO5KZDNFSNX24YBGHLQRPBVWIZM62FXZT2QD5V4CQ3H2QXDISKOBUGUL6M",transactions_number,"molud","molud")
    p1 = multiprocessing.Process(target=send_trans_client,args=("p1",s1[0],s1[1],queue))
    p1.start()
    start_time = time.time()
    p1.join()
    end_time = time.time()
    whole_transactions = 0
    whole_faulty_transactions = 0
    while queue.empty() != True:
        data = queue.get()
        whole_transactions = whole_transactions + data[0]
        whole_faulty_transactions = whole_faulty_transactions + data[1]
    print("Number of transactions: %s\nWhole Time %s\nFaulty transaction number: %s\nTPS: %s" % (whole_transactions,end_time-start_time,whole_faulty_transactions,(whole_transactions)/(end_time-start_time)))




