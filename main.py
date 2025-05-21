import asyncio
import datetime

import aiocqhttp

import xt_hero


async def main_xt() -> None:
    host = '0.0.0.0'
    port = 6199
    bot = aiocqhttp.CQHttp()

    def get_next_run_time(now):
        # 计算下一个运行时间点（即明天早上8点）
        next_run_time = datetime.datetime(now.year, now.month, now.day, 8, 0) + datetime.timedelta(days=1)
        return next_run_time

    async def schedule_daily_task():
        while True:
            now = datetime.datetime.now()
            next_run_time = get_next_run_time(now)
            wait_seconds = (next_run_time - now).total_seconds()
            # wait_seconds = 10

            print(f"下一次执行时间为: {next_run_time}, 等待 {wait_seconds} 秒")
            await asyncio.sleep(wait_seconds)

            # 执行任务
            news = xt_hero.get_news()
            try:
                await bot.send_group_msg(group_id=713970542, message=f'[CQ:image,file=base64://{news}]')
            except aiocqhttp.exceptions.ApiNotAvailable:
                pass

    @bot.on_message('group')
    async def message_group(event: aiocqhttp.Event):
        text = next((item['data']['text'] for item in event.message if item['type'] == 'text'), '')
        if xt_hero.contains_kana(text):
            lines = text.splitlines()
            for line in lines:
                cleaned_text = xt_hero.clean_text(line)
                title = xt_hero.hero(cleaned_text)
                await bot.send(event, title)
        keywords = ['新闻', 'news']
        if 'at,qq=2655223227' in event.raw_message and any(keyword in text for keyword in keywords):
            # 执行任务
            news = xt_hero.get_news()
            try:
                await bot.send_group_msg(group_id=713970542, message=f'[CQ:image,file=base64://{news}]')
            except aiocqhttp.exceptions.ApiNotAvailable:
                pass

    # 每天早上8点执行get_news函数
    asyncio.create_task(schedule_daily_task())

    await bot.run_task(host, port)


if __name__ == '__main__':
    asyncio.run(main_xt())
