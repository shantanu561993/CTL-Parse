import httpx
import asyncio
import pickle

async def get_leaves(client:httpx.AsyncClient,url: str, start: int, end: int)->dict:
    print (f"Getting leaves from {start} to {end}")
    response = await client.get(url=f"{url}/ct/v1/get-entries?start={start}&end={end}")
    return response.json()

async def process_worker(result:dict):
    print(f"Processing {result['description']}")
    print("    \\- URL:            {}".format(result['url']))
    print("    \\- Owner:          {}".format(result['operated_by']))
    print("    \\- Cert Count:     {}".format(result['tree_size']-1, grouping=True))
    print("    \\- Max Block Size: {}\n".format(result['block_size']))
    cert_count = result['tree_size']
    block_size = result['block_size']
    print (f"Cert count: {cert_count}")
    print (f"Block size: {block_size}")
    client = httpx.AsyncClient()
    for i in range(0, cert_count, block_size*10):
        file_name = f"results/{result['description']}-{i}-{i+block_size*10}.pkl"
        tasks = [get_leaves(client, result['url'], j, j+block_size) for j in range(i, i+block_size*10, block_size)]
        results = await asyncio.gather(*tasks)
        # Store results in a file
        with open(file_name, 'wb') as file:
            pickle.dump(results, file)
    await client.aclose()
   