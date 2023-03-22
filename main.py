import asyncio


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection('minechat.dvmn.org', 5000)
    while True:
        try:
            print(f'Send: {message!r}')
            writer.write(message.encode())
            await writer.drain()
            data = await reader.read(100)
            print(data.strip().decode("utf-8-sig", "ignore"))
        except KeyboardInterrupt:
            writer.close()
            await writer.wait_closed()
            break


if __name__ == '__main__':
    asyncio.run(tcp_echo_client('Hello World!'))
