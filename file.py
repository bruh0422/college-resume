import asyncio, aiofiles, os, json

lock = {}

class Data:
    @staticmethod
    def get_lock(path: str) -> asyncio.Lock: # 取得 File Lock
        if path not in lock: # 若不存在則創建
            lock[path] = asyncio.Lock()
        return lock[path]

    @staticmethod
    async def load_file(category: str, filename: str) -> dict: # 讀取檔案
        path = os.path.join('data', category, filename)

        async with Data.get_lock(path): # 呼叫 File Lock
            async with aiofiles.open(path, mode='r', encoding='utf8') as file:
                content = await file.read()
                data = json.loads(content)

        return data

    @staticmethod
    async def save_file(category, filename, data) -> None: # 寫入檔案
        temp_file_path = os.path.join('data', 'temp', filename) + '.tmp'
        path = os.path.join('data', category, filename)

        async with Data.get_lock(path): # 呼叫 File Lock
            async with aiofiles.open(temp_file_path, mode='w', encoding='utf8') as file:
                await file.write(json.dumps(data, ensure_ascii=False, indent=4)) # 寫入暫存檔

            os.replace(temp_file_path, path) # 取代原始檔案
