import asyncio
import os
import shutil
import socket
from datetime import datetime
from pyrogram.types import CallbackQuery
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters
import aiohttp
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from io import BytesIO
from pyrogram import filters
import config
from Lyka import app
from Lyka.misc import HAPP, SUDOERS, XCB
from Lyka.utils.database import (
    get_active_chats,
    remove_active_chat,
    remove_active_video_chat,
)
from Lyka.utils.decorators.language import language
from Lyka.utils.pastebin import LykaBin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def is_heroku():
    return "heroku" in socket.getfqdn()


async def make_carbon(code):
    url = "https://carbonara.solopov.dev/api/cook"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"code": code}) as resp:
            image = BytesIO(await resp.read())
    image.name = "carbon.png"
    return image

 
@app.on_message(
    filters.command(["get_log", "logs", "getlogs"]) & SUDOERS
)
@language
async def log_(client, message, _):
    try:
        await message.reply_document(document="log.txt")
    except:
        await message.reply_text(_["server_1"])


@app.on_message(filters.command(["update", "gitpull", "up"]) & SUDOERS)
@language
async def update_(client, message, _):
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["server_2"])
    response = await message.reply_text(_["server_3"])
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit(_["server_4"])
    except InvalidGitRepositoryError:
        return await response.edit(_["server_5"])
    to_exc = f"git fetch origin {config.UPSTREAM_BRANCH} &> /dev/null"
    os.system(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]
    for checks in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit(_["server_6"])
    updates = ""
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[(format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4],
    )
    for info in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"):
        updates += f"<b>➣ #{info.count()}: <a href={REPO_}/commit/{info}>{info.summary}</a> By -> {info.author}</b>\n\t\t\t\t<b>➥ Commited on :</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
    _update_response_ = "<b>A new update is available for the bot!</b>\n\n➣ Pushing updates now\n\n<b><u>Updates:</u></b>\n\n"
    _final_updates_ = _update_response_ + updates
    if len(_final_updates_) > 4096:
        url = await LykaBin(updates)
        nrs = await response.edit(
            f"<b>A new update is available for the bot</b>\n\n➣ Pushing updates now\n\n<u><b>Updates :</b></u>\n\n<a href={url}>Check updates</a>"
        )
    else:
        nrs = await response.edit(_final_updates_, disable_web_page_preview=True)
    os.system("git stash &> /dev/null && git pull")

    try:
        served_chats = await get_active_chats()
        for x in served_chats:
            try:
                await app.send_message(
                    chat_id=int(x),
                    text=_["server_8"].format(app.mention),
                )
                await remove_active_chat(x)
                await remove_active_video_chat(x)
            except:
                pass
        await response.edit(f"{nrs.text}\n\n{_['server_7']}")
    except:
        pass

    if await is_heroku():
        try:
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(f"{nrs.text}\n\n{_['server_9']}")
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=_["server_10"].format(err),
            )
    else:
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()


@app.on_message(filters.command(["restart"]) & SUDOERS)
async def restart_(_, message):
    response = await message.reply_text("Restarting...")
    ac_chats = await get_active_chats()
    for x in ac_chats:
        try:
            await app.send_message(
                chat_id=int(x),
                text=f"{app.mention} is restarting...\n\nYou can start playing again after 15-20 seconds.",
            )
            await remove_active_chat(x)
            await remove_active_video_chat(x)
        except:
            pass

    try:
        shutil.rmtree("downloads")
        shutil.rmtree("raw_files")
        shutil.rmtree("cache")
    except:
        pass
    await response.edit_text(
        "» Restart process started, Please wait for few seconds until the bot starts..."
    )
    os.system(f"kill -9 {os.getpid()} && bash start")
