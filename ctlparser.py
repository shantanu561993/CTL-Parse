import httpx
import asyncio
import base64
import ctl_parser_structures
from OpenSSL import crypto


async def main():
    
    async with httpx.AsyncClient() as client:
        for i in range(1, 50000):
            url = f"https://ct2025-b.trustasia.com/log2025b/ct/v1/get-entries?start={i}&end={i}"
            response = await client.get(url)
            response = response.json()
            entries = response['entries']
            leafs = entries[0]['leaf_input']
            extra_data = entries[0]['extra_data']
            leaf_cert = ctl_parser_structures.MerkleTreeHeader.parse(base64.b64decode(leafs))
            print("Leaf Timestamp: {}".format(leaf_cert.Timestamp))
            print("Entry Type: {}".format(leaf_cert.LogEntryType))
            # print(leaf_cert.Entry)
            if leaf_cert.LogEntryType == "X509LogEntryType":
            # We have a normal x509 entry
                cert_data_string = ctl_parser_structures.Certificate.parse(leaf_cert.Entry).CertData
                chain = [crypto.load_certificate(crypto.FILETYPE_ASN1, cert_data_string)]
                print(chain.pop().get_subject().commonName)



if __name__ == '__main__':
    asyncio.run(main())