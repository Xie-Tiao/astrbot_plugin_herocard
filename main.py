from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import random
import asyncio
import datetime

from . import xt_hero  # 使用相对导入


@register("xt_hero_plugin", "YourName", "一个展示新闻和处理消息的插件", "1.0.0")
class XtHeroPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.scheduled_task = None

    async def on_load(self):
        # 插件加载时启动定时任务
        self.scheduled_task = asyncio.create_task(self.schedule_daily_task())

    async def on_unload(self):
        # 插件卸载时取消定时任务
        if self.scheduled_task:
            self.scheduled_task.cancel()

    def get_next_run_time(self, now):
        # 计算下一个运行时间点（即明天早上8点）
        next_run_time = datetime.datetime(now.year, now.month, now.day, 8, 0)
        if now.hour >= 8:  # 如果当前时间已过8点，则安排到明天
            next_run_time += datetime.timedelta(days=1)
        return next_run_time

    async def schedule_daily_task(self):
        while True:
            now = datetime.datetime.now()
            next_run_time = self.get_next_run_time(now)
            wait_seconds = (next_run_time - now).total_seconds()

            logger.info(f"下一次执行时间为: {next_run_time}, 等待 {wait_seconds} 秒")
            await asyncio.sleep(wait_seconds)

            # 执行任务
            try:
                news = xt_hero.get_news()
                # 使用yield返回消息结果而不是直接发送
                yield event.plain_result(f'[CQ:image,file=base64://{news}]')
                logger.info("定时新闻发送成功")
            except Exception as e:
                logger.error(f"定时新闻发送失败: {e}")

    @filter.command("新闻", "news")
    async def handle_news_command(self, event: AstrMessageEvent):
        """处理用户主动请求新闻的命令"""
        try:
            news = xt_hero.get_news()
            # 使用yield返回消息结果
            yield event.plain_result(f'[CQ:image,file=base64://{news}]')
        except Exception as e:
            yield event.plain_result("获取新闻失败，请重试")

    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def handle_message(self, event: AstrMessageEvent):
        """处理群消息中的关键词和日文检测"""
        text = event.message_str

        # 检测消息中是否包含日文假名
        if event.is_admin() and xt_hero.contains_kana(text):
            lines = text.splitlines()
            for line in lines:
                cleaned_text = xt_hero.clean_text(line)
                title = xt_hero.hero(cleaned_text)
                if title:
                    # 使用yield返回消息结果
                    yield event.plain_result(title)

        # 检测是否@机器人并包含关键词
        if event.is_admin() and any(keyword in text for keyword in ['新闻', 'news']):
            try:
                news = xt_hero.get_news()
                # 使用yield返回消息结果
                yield event.plain_result(f'[CQ:image,file=base64://{news}]')
            except Exception as e:
                logger.error(f"响应@新闻请求失败: {e}")
                yield event.plain_result("获取新闻失败，请稍后再试")