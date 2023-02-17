import asyncio
import logging
import http3
logger = logging.getLogger(__name__)

class KoboldAIException(Exception):
    pass

class SimpleHorde:
    def __init__(self, url='https://koboldai.net/api/v2/', apikey='0'*10):
        self.apiurl = url
        self.apikey = apikey
        self.client = http3.AsyncClient()
    def _process_result(self, result):
        json = result.json()
        logger.info(json)
        if 'message' in json:
            raise KoboldAIException(json['message'], result)
        if 'errors' in json:
            raise KoboldAIException(json['errors'], result)
        else:
            return json
    async def _post(self, url, **params):
        result = await self.client.post(self.apiurl + url, headers = dict(apikey=self.apikey), json = params)
        return self._process_result(result)
    async def _get(self, url, *extras):
        result = await self.client.get(self.apiurl + url + '/'.join(extras), headers = dict(apikey=self.apikey))
        return self._process_result(result)
    async def status_models(self):
        return await self._get('status/models')
    async def workers(self):
        return await self._get('workers')
    async def generate_async(self, **kwparams):
        return await self._post('generate/async', **kwparams)
    async def generate_check(self, id):
        return await self._get('generate/check/', id)
    async def generate_status(self, id):
        return await self._get('generate/status/', id)
    async def generate(self, prompt, models = [], workers = [], trusted_workers = False, n = 1, max_length = 80, max_content_length = 1024, **kwparams):
        if models is None:
            available_models = await self.status_models()
            available_models.sort(key = lambda model: (model.get('queued'), -model.get('performance')))
            models = [model['name'] for model in available_models[:n]]
        id = (await self.generate_async(
            prompt = prompt,
            models = models,
            workers = workers,
            trusted_workers = trusted_workers,
            params = dict(
                n = n,
                max_length = max_length,
                max_content_length = max_content_length,
                **kwparams
            )
        ))['id']
        check = {}
        while not check.get('done'):
            await asyncio.sleep(0.1)
            check = await self.generate_check(id)
        status = await self.generate_status(id)
        return [generation['text'] for generation in status['generations']]
