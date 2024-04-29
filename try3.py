import httpx
import asyncio
from httpxlib import make_request
import locale
import pickle
from temp_worker import process_worker
CTL_LISTS = 'https://www.gstatic.com/ct/log_list/v3/all_logs_list.json'



async def get_info_from_ctls(client:httpx.AsyncClient,ctl:dict):
    url=ctl['url']+"/ct/v1/get-sth"
    try:
        response = await client.get(url=url)
        ctl['tree_size'] = response.json()['tree_size']
        response = await client.get(url=ctl['url']+"/ct/v1/get-entries?start=0&end=10000")
        response = response.json()
        entries = response['entries']
        ctl['block_size'] = len(entries)
    except Exception as e:
        ctl['error'] = "yes"
        return ctl        
    return ctl        


async def retrieve_all_ctls():
    async with httpx.AsyncClient() as session:
        ctl_lists = await session.get(CTL_LISTS)
        ctl_lists = ctl_lists.json()

        logs = []
        for operator in ctl_lists['operators']:
            owner = operator['name']
            for log in operator['logs']:
                log['url'] = log['url']
                if log['url'].endswith('/'):
                    log['url'] = log['url'][:-1]        
                log['operated_by'] = owner
                logs.append(log)

        return logs


async def main():
    all_ctls = await retrieve_all_ctls()
    async with httpx.AsyncClient() as client:
        tasks = [get_info_from_ctls(client,ctl) for ctl in all_ctls]
        results = await asyncio.gather(*tasks)
        # results = []
        # for task in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Progress"):
        #     result = await task
        #     results.append(result)

        
    for result in results:
        if "error" not in result.keys():
            print(result['description'])
            print("    \\- URL:            {}".format(result['url']))
            print("    \\- Owner:          {}".format(result['operated_by']))
            print("    \\- Cert Count:     {}".format(result['tree_size']-1, grouping=True))
            print("    \\- Max Block Size: {}\n".format(result['block_size']))
    
    # Save results to pickle
    with open('results.pkl', 'wb') as f:
        pickle.dump(results, f)

    # Load results from pickle
    with open('results.pkl', 'rb') as f:
        loaded_results = pickle.load(f)

    # # Print loaded results
    # for result in loaded_results:
    #     if "error" not in result.keys():
    #         print(result['description'])
    #         print("    \\- URL:            {}".format(result['url']))
    #         print("    \\- Owner:          {}".format(result['operated_by']))
    #         print("    \\- Cert Count:     {}".format(result['tree_size']-1, grouping=True))
    #         print("    \\- Max Block Size: {}\n".format(result['block_size']))
    
    for result in loaded_results:
        if "error" not in result.keys():
            await process_worker(result)
            break


            
    


if __name__ == '__main__':
    asyncio.run(main())