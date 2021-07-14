import httpx
import asyncio
import json

async def req(url, data_list):
    async with httpx.AsyncClient() as client:
         tasks = (client.post(url, data=data) for data in data_list)
         reqs = await asyncio.gather(*tasks)

    return [json.json() for json in reqs]


url = 'http://0.0.0.0:5000'
endpoint = '/translate'

data = [{
    'q': 'text1',
    'source': 'en',
    'target': 'es',
    },
    {
        'q': 'text2',
        'source': 'en',
        'target': 'es',
        },
    {
        'q': 'text3',
        'source': 'en',
        'target': 'es',
        },
    {
        'q': 'text4',
        'source': 'en',
        'target': 'es',
        },]
url = url + endpoint
r = asyncio.run(req(url, data))


for j in r:
    print(json.dumps(j, indent=2))
