import asyncio
from environs import Env
import argparse


async def connect(host, port, token):
    reader, writer = await asyncio.open_connection(host, port)
    data = await reader.read(200)
    print(data.decode())
    writer.write(f'{token}\n'.encode())
    await writer.drain()
    data = await reader.read(200)
    print(data.decode())
    return reader, writer


async def tcp_send_client(host, port, token):
    reader, writer = await connect(host, port, token)
    while True:
        try:
            message = input('Сообщение: ')
            writer.write(f'{message}\n\n'.encode())
            await writer.drain()
        except ConnectionError:
            writer.close()
            await writer.wait_closed()
            reader, writer = await connect(host, port, token)
            continue
        except KeyboardInterrupt:
            writer.close()
            await writer.wait_closed()
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
        default=env.int('SENDING_PORT')
    )
    parser.add_argument(
        '-t', '--token',
        required=False,
        action='store_true',
        help='TOKEN для подключения',
        default=env.str('TOKEN')
    )
    parser_args = parser.parse_args()
    connect_host = parser_args.host
    connect_port = parser_args.port
    connect_token = env.str('TOKEN')
    asyncio.run(tcp_send_client(connect_host, connect_port, connect_token))
