import asyncio
import argparse
import logging
import json
import aiofiles

from time import sleep
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


async def register(reader, writer, name):
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


async def send_message(host, port, token, msg=None, login=None):
    first_reconnection = True
    while True:
        reader, writer = await asyncio.open_connection(host, port)
        try:
            received_data = await authorise(reader, writer, token)
            if json.loads(received_data[0]) is None:
                name = login if login else input().strip().replace(r'\n', '_')
                new_token = await register(reader, writer, name)
                writer.close()
                await writer.wait_closed()
                await send_message(host, port, new_token, msg, login)
                return
            if not msg:
                print('Отправляйте сообщения, нажимая "enter"')
            while True:
                message = msg if msg else input()
                message = message.strip().replace(r'\n', ' ')
                writer.write(f'{message}\n\n'.encode())
                await writer.drain()
                logger.debug(f'Сообщение "{message}" отправлено!')
                if msg:
                    break
            break
        except KeyboardInterrupt:
            break
        except (ConnectionError, TimeoutError):
            second = 0 if first_reconnection else 5
            sleep(second)
            first_reconnection = False
            continue
        finally:
            writer.close()
            await writer.wait_closed()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    parser = argparse.ArgumentParser(prog='UndegroundChat', description='Отправка сообщений в чат')
    parser.add_argument(
        '-hs', '--host',
        required=False,
        help='HOST для подключения',
        default=env.str('HOST')
    )
    parser.add_argument(
        '-p', '--port',
        required=False,
        help='PORT для подключения',
        default=env.int('SENDING_PORT')
    )
    parser.add_argument(
        '-t', '--token',
        required=False,
        help='TOKEN для подключения',
        default=env.str('TOKEN')
    )
    parser.add_argument(
        '-n', '--name',
        required=False,
        help='Желаемый логин, если нет токена',
    )
    parser.add_argument(
        '-m', '--msg',
        required=False,
        help='Отправляемое сообщение. Если не указано, то сообщения будут запрошены через ввод',
    )
    logging.basicConfig(
        format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-5s [%(asctime)s]  %(message)s',
        level=logging.DEBUG
    )
    parser_args = parser.parse_args()

    asyncio.run(send_message(
        host=parser_args.host,
        port=parser_args.port,
        token=env.str('TOKEN'),
        msg=parser_args.msg,
        login=parser_args.name
    ))
