import asyncio
from pyppeteer import launch
import time
import re

browser = None  # Глобальная переменная для хранения экземпляра браузера

async def get_browser():
    global browser
    if browser is None:
        browser = await launch(executablePath="/usr/bin/google-chrome", headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    return browser

async def cny_run():
    browser = await get_browser()
    page = await browser.newPage()
    await page.goto('https://www.gazprombank.ru/personal/courses/')


    await asyncio.sleep(1)

    # Получаем все тексты элементов
    elements = await page.querySelectorAllEval('div.courses_table__col-40b', 'nodes => nodes.map(n => n.textContent)')
    curce_now = 0
    for i in elements[19:20]:
        curce_now += (float(i))

    await page.close()
    return curce_now

asyncio.get_event_loop().run_until_complete(cny_run())