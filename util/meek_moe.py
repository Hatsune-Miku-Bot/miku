from os.path import join
from pathlib import Path
from random import choice

import aiohttp
import discord


async def meek_api(ctx, name):
    session = aiohttp.ClientSession()

    l = choice(['https://api.meek.moe/', 'https://mikuapi.predeactor.net/random',
               False]) if name.lower() == 'miku' else 'https://api.meek.moe/'
    e = discord.Embed(title=name.capitalize(), color=discord.Color.random())
    try:
        if name == 'miku' and l:
            data = await session.get(l + name if l == 'https://api.meek.moe/' else 'https://mikuapi.predeactor.net/random')
        else:
            data = await session.get(l + name)
            url = await data.json()
        e.set_image(url=url['url'])
    except:
        imageslistdir = Path(__file__).resolve(
            strict=True).parent / join('images_list.txt')
        filepointer = open(imageslistdir)
        imageslist = filepointer.readlines()
        if name == 'miku':
            e.set_image(url=choice(imageslist))
        else:
            e = discord.Embed(
                title='Sorry but currently there is some problem!', color=discord.Color.red())
            e.set_image(url=choice(imageslist))
    await session.close()
    return e
