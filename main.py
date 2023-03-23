import asyncio
import aiofiles
from datetime import datetime


async def tcp_echo_client(message, file):
    reader, writer = await asyncio.open_connection('minechat.dvmn.org', 5000)
    while True:
        try:
            # print(f'Send: {message!r}')
            # writer.write(message.encode())
            # await writer.drain()
            data = await reader.read(100)
            now_time = datetime.now().strftime("[%d.%m.%Y %H:%M:%S]")
            msg = data.strip().decode("utf-8-sig", "ignore")
            async with aiofiles.open(file, mode='a') as f:
                await f.write(f'{now_time} {msg}\n')
            print(f'{now_time} {msg}')
        except ConnectionError:
            writer.close()
            reader, writer = await asyncio.open_connection('minechat.dvmn.org', 5000)
            continue
        except KeyboardInterrupt:
            writer.close()
            await writer.wait_closed()
            break


if __name__ == '__main__':
    asyncio.run(tcp_echo_client('Hello World!', 'chat.txt'))
