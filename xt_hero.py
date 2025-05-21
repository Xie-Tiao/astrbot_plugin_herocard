import base64
import re

import httpx


def hero(text):
    # text = test_text
    pattern = r"(?<=\])(.*?)(?=\[|\(|\.|\【|\。)"
    pattern2 = r"(?<=\))(.*?)(?=\[|\.|\【|\。)"
    pattern3 = r"(?<=\.)(.*?)(?=\[|\.|\【|\。|\()"
    pattern4 = r"(?<=\。)(.*?)(?=\[|\.|\【|\。|\()"

    patterns = [pattern, pattern2, pattern3, pattern4]

    for p in patterns:
        result = re.search(p, text)
        if result and result.group() != ' ':
            return result.group().strip()


def contains_kana(text):
    """
    检测字符串中是否包含日语假名（平假名或片假名）。
    :param text: 输入的字符串
    :return: 如果包含假名，返回 True；否则返回 False
    """
    # 正则表达式：匹配平假名或片假名
    kana_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]')
    return bool(kana_pattern.search(text))


def clean_text(text):
    # 使用正则表达式去掉#(某些文字)部分
    try:
        cleaned_text = re.sub(r'#\([^)]*\) ', '', text)
        return cleaned_text
    except:
        return text


def get_news():
    # API的URL，假设API返回图片内容
    url = "https://api.southerly.top/api/60s?format=image"

    try:
        # 使用httpx.Client上下文管理器来发送请求
        with httpx.Client() as client:
            response = client.get(url)

            # 检查状态码是否为200（HTTP OK）
            if response.status_code == 200:
                # 确保响应内容是字节类型
                image_bytes = response.content

                # 将图片数据编码为Base64
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')

                print("图片已成功转换为Base64编码")
                return image_base64
            else:
                print(f"请求失败，状态码：{response.status_code}")
                return None
    except Exception as e:
        print(f"发生异常：{e}")
        return None


if __name__ == '__main__':
    # 测试
    # text1 = "(2020 Summer)テーマ(subtitle) [中国翻訳] (31P)(完)"  # 平假名
    # text2 = "コンニチハ"  # 片假名
    # text3 = "Hello, 世界"  # 不含假名
    # text4 = "[作者さん]テーマ[中国翻訳] [DL版]"  # 混合
    #
    # # print(contains_kana(text1))  # 输出: True
    # # print(contains_kana(text2))  # 输出: True
    # # print(contains_kana(text3))  # 输出: False
    # # print(contains_kana(text4))  # 输出: True
    # # 原始字符串
    # text = "。100回フラれた#(哈哈) 絶望的にモテない俺を憐れんだ彼氏あり女友達#(太开心) が何でもエロい事ヤら#(捂嘴笑) せてくれた！！(107P)(完)"
    # lines = text.splitlines()
    # # print(lines)
    # for line in lines:
    #     cleaned_text = clean_text(line)
    #     title = hero(cleaned_text)
    #     # print(title)
    #     print(title)
    # # print(clean_text(text))
    get_news()
