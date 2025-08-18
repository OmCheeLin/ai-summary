from openai import OpenAI
from config.config import get_llm_api_key
from util.common.json_util import extract_json_from_text
from loguru import logger

client = OpenAI(
    api_key=get_llm_api_key(),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


summary_prompt = """你是智能视频总结助手。
请根据用户发来的视频文本，写【全文摘要】和【全文亮点】。
你的回答必须严格遵守以下JSON格式：
{
    "summary": "此处填写你的全文摘要",
    "highlights": [
        "全文亮点1...",
        "亮点2...",
        "亮点3...",
    ]
}
注意：全文摘要的字数根据视频文本长度控制在200到400字，全文亮点的个数根据视频文本的长度控制在5到8点。
"""

group_sentences_prompt = """你是智能视频分段总结助手。
请根据用户发来的视频json文本，写【分段总结】。
你的回答必须严格遵守以下JSON格式，例如：
{
    "分段总结": [
        {
            "sentence_ids": [1, 2, 3, 4],
            "title": "此处填写总结小标题",
            "summary": "此处填写你对这一部分连续语句段的总结"
        },
        {
            "sentence_ids": [5, 6, 7, 8, 9, 10],
            "title": "此处填写总结小标题",
            "summary": "此处填写你对这一部分连续语句段的总结"
        }
    ]
}
注意：
1. 每一段的总结部分字数控制在50到80字左右。
2. sentence_ids必须连续并且存在于用户发的内容中。
"""


def get_llm_summary(passage: str):
    completion = client.chat.completions.create(
        model="qwen3-235b-a22b",
        messages=[
            {'role': 'system', 'content': summary_prompt},
            {'role': 'user', 'content': passage}
        ],
        extra_body={"enable_thinking": False}
    )
    llm_summary = extract_json_from_text(completion.choices[0].message.content)
    logger.info(f"llm_summary: {llm_summary}")
    return llm_summary


def get_llm_group_sentences(passage: str):
    completion = client.chat.completions.create(
        model="qwen3-235b-a22b",
        messages=[
            {'role': 'system', 'content': group_sentences_prompt},
            {'role': 'user', 'content': passage}
        ],
        extra_body={"enable_thinking": False}
    )
    logger.info(f"llm_group_sentences: 完成！")
    return extract_json_from_text(completion.choices[0].message.content)


if __name__ == "__main__":
    passage = "真心希望各位观众老爷们不要白嫖，你的三连是我更新的动力。Mcp有哪3种传输方式呢？当然即将会变成两种，因为它会用s改, 用stream http的方式。那为什么要这样做呢？那现在去面试的话，或多或少都会问你一些AI的技术。那这里呢有一份100万字的面试资料，不仅包含了Java所有的高频面试题，最近还加入了50道AI面试题，需要的话点赞、关注、收藏、评论区回复666即可免费的来进领取。那第一种呢是首先客户端会和服务端建立一个的长链接。那它的本质呢依然是通过P的P通信方式会进行3。那么当长链接建立完之后，服务端就可以不断的向客户端向的去发送数据，而不用每一次通讯呢都进行三握手，从而提升了性能。那P客户端呢可以主动的去关闭s的长链接，那目前P协议已经把这种方式废弃了。主要的原因呢是因为啊这个长链接一旦建立完之后，整个通信过程都需要依赖这个长链接。一旦它出现了一些网络的毛刺，比如说短暂的中断，那么此时mp往客户端去发送数据的时候呢就会丢失。并且mp server呢短暂时间之内呢它是感受不到的那当连接恢复之后呢，之前发送的数据都已经丢失。所以在最新的P协议当中呢，它采用它同样的也会建立一个长链接。只不过这种方式呢我在发送数据的时候，如果出现了短暂的中断，P的在发送数据的时候呢，它是能够感知到的。直到连接的恢复之后呢，可以持续的将没有发送给客户端的数据呢再次发送过去，保证了长链接的一个高可用性。那第三种方式呢就是了也就是所谓的标准输入输出，它会在你的客户端程序当中，通过一个进程，用命令的方式去启动的一个包。那这个包呢可以是Java开发的包，也可以是Pyon开发的包，也可以是nogs开发的包。所以这种方式呢它需要依赖你的客户端，必须要有服务包对应的一个环境，否则呢就无法去启动它。那一旦启动完成之后呢，就可以通过命令的方式往这个包当中呢去写入信息。那这个包它就会去响应对应的信息，从而呢来达到数据的传输。所以stdio的方式呢它实际上是跟客户端一一对应的，一个客户端呢就会去hello喽大家，我是徐叔。现在面试题啊都是死磕场景，场景题就是八文业务结合。那我这里有一份80万面试资料，里面括了了所有的主流量的面题，业务场景开放案等你只要把结合的题。Server, 所以我们在开发mcp server的时候呢，就可以通过他们不同的特性来去选择不同的传输方式。那你像stdio，它就更加的适用于面向个人用户的客户端多命用。因为它需要绑定在你的客户端进程当中，所以呢它是本地运行的，不需要依赖H ttp的环境。当然如果你的server它需要通过网络来去调用一些第三方的接口，那还是需要有网络的环境的。但是如果你的server它是一个用来操作你的客户端的程序，比如说读取你的文件，那这种它是不依赖任何的网络环境的。所以呢它的成本比较低，它不需要单独的为M D server去部署一台web服务器，所以它就比较适用于开发一些辅助性的工具。那它如果要做权限控制呢，会基于环境变量的方式。所以呢它就不支持多个客户端的并发以及动态的切换，就不适用于开发基于浏览器的htb应用。因为假如你的应用程序是一个web应用，那你的p server会跟你的web应用呢部署在同一个服务器，同一个进程。那此时如果有多台客户端同时访问，你要动态的去切换用户的一个权限，它是做不到的。因为你的服务通过标准输入的方式去写入信息呢，它是通过初始的那个环境变量来传输用户的信息的。它是不支持多个客户端进行共享的。所以这点呢需要注意。如果你开发的是一个浏览器的web部应用，就不要选择stdio的传输方式。那另外还有一个问题呢，就是它的升级可能会麻烦一点，因为它是通过包的方式去启动的。那么一旦我这个P的的包有升级，我的客户端的程序呢也需要重新启动。并且呢需要重新获取更新之后的包，重新的启动才能获得更新。所以假如说我们需要开发基于浏览器的web服务，那我们肯定建议呢推荐使用最新的streamable这种行连接的传输方式。那么它的本质啊实际不是由客户端直接请求M4k server，而是呢由客户端去请求你的web服务器，再由web服务器呢去请求你的M4p server。然后整个通信过程呢通过hb的方式来进行通信。所以这种方式我们的M4p server它是面向于服务的，而不像我们的stl它是直接面向用户的，并且呢它支持高频发。那我们要做控制的话，也完全呢可以通过的认证机制，比如说这种方式在的请求当中传入对应的这个认证就行。并且这种方式呢你的的它是支持热更新的，一旦你的mcp server端有任何的更新，我只需要重新的进行部署即可。好，那这两种方式呢我就给大家介绍到这里，明白之后呢，你就可以根据他们对应的特性来选择对应的传输方式来进行开发。我就给大家介绍到这里。如果视频对你有帮助，记得给徐叔老师一键三连支持，我们下期见。"
    get_llm_summary(passage)