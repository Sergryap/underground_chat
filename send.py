import asyncio
import argparse
import logging
import json
import aiofiles

from environs import Env


logger = logging.getLogger('chat_logger')


async def authorise(reader, writer, token):
    data = await reader.read(200)
    logger.debug(data.decode())
    writer.write(f'{token}\n'.encode())
    await writer.drain()
    data = await reader.read(200)
    received_data = data.decode().split('\n')
    if not received_data or (len(received_data) > 0 and not received_data[0]):
        return await authorise(reader, writer, token)
    if len(received_data) < 2 or not received_data[1]:
        print('Welcome to chat! Post your message below. End it with an empty line.')
    else:
        print(received_data[1])
    return received_data


async def register_r(reader, writer, name):
    writer.write(f'{name}\n'.encode())
    await writer.drain()
    data = await reader.read(200)
    register_data = data.decode().split('\n')
    print(register_data)
    if (
            not register_data
            or (len(register_data) > 0 and not register_data[0])
            or 'Enter preferred nickname below:' in register_data
    ):
        return await register(reader, writer, name)
    new_token = json.loads(register_data[0])['account_hash']
    async with aiofiles.open('token.txt', mode='w') as f:
        await f.write(new_token)
    return new_token


async def register(reader, writer, name):
    while True:
        writer.write(f'{name}\n'.encode())
        await writer.drain()
        data = await reader.read(200)
        register_data = data.decode().split('\n')
        if (
                register_data
                and register_data[0]
                and 'Enter preferred nickname below:' not in register_data
                and json.loads(register_data[0]).get('account_hash')):
            break
    new_token = json.loads(register_data[0])['account_hash']
    async with aiofiles.open('token.txt', mode='w') as f:
        await f.write(new_token)
    return new_token


async def tcp_send_client(host, port, token):
    reader, writer = await asyncio.open_connection(host, port)
    received_data = await authorise(reader, writer, token)
    if json.loads(received_data[0]) is None:
        name = input().strip().replace(r'\n', '_')
        new_token = await register_r(reader, writer, name)
        writer.close()
        await writer.wait_closed()
        await tcp_send_client(host, port, new_token)
        return
    print('Отправляйте сообщения, нажимая "enter"')
    while True:
        try:
            message = input().strip().replace(r'\n', ' ')
            writer.write(f'{message}\n\n'.encode())
            await writer.drain()
            logger.debug(f'Сообщение "{message}" отправлено!')
        except ConnectionError:
            writer.close()
            await writer.wait_closed()
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
    logging.basicConfig(
        format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-5s [%(asctime)s]  %(message)s',
        level=logging.DEBUG
    )
    asyncio.run(tcp_send_client(connect_host, connect_port, connect_token))
