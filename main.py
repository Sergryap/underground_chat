import asyncio
import aiofiles
from environs import Env
from datetime import datetime
import argparse


async def tcp_receiving_client(host, port, file):
    reader, __ = await asyncio.open_connection(host, port)
    while True:
        try:
            data = await reader.read(100)
            now_time = datetime.now().strftime("[%d.%m.%Y %H:%M:%S]")
            msg = data.strip().decode("utf-8-sig", "ignore")
            async with aiofiles.open(file, mode='a') as f:
                await f.write(f'{now_time} {msg}\n')
            print(f'{now_time} {msg}')
        except ConnectionError:
            reader, __ = await asyncio.open_connection(host, port)
            continue
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    env = Env()
    env.read_env()
    parser = argparse.ArgumentParser(prog='UndegroundChat', description='Подключение к чату')
    parser.add_argument(
        '-hs', '--host',
        required=False,
        action='store_true',
        help='HOST для подключения',
        default=env.str('HOST')
    )
    parser.add_argument(
        '-p', '--port',
        required=False,
        action='store_true',
        help='PORT для подключения',
        default=env.int('RECEIVING_PORT')
    )
    parser.add_argument(
        '-f', '--file_path',
        required=False,
        action='store_true',
        help='Путь к файлу с историей переписки',
        default=env.str('FILE_PATH')
    )
    parser_args = parser.parse_args()
    connect_host = parser_args.host
    connect_port = parser_args.port
    file_path = parser_args.file_path
    asyncio.run(tcp_receiving_client(connect_host, connect_port, file_path))
