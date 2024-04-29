import httpx
import json 
import re
import asyncio


async def main():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://www.gstatic.com/ct/log_list/v3/log_list.json')
        data = response.json()
        total_certs = 0
        operators = data['operators']
        for operator in operators:
            print(operator['name'])
            for log in operator['logs']:
                response = await client.get(f"{log['url']}ct/v1/get-sth")
                try:
                    response = response.json()
                    size = response['tree_size']
                except Exception as e:
                    print(response.text)
                total_certs += size
                print(log['url'],size)
        print("================")
        print("Total certs: ",total_certs)
 

if __name__ == '__main__':

    asyncio.run(main())