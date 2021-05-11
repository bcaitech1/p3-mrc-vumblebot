import os
import json
import datetime
from pathlib import Path

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# TODO: 토큰을 GitHub에 올리면 토큰이 자동으로 재생성되므로 Github에 올리면 안됩니다.

BASE_DIR = Path(__file__).resolve().parent.parent
# TODO : input아래에 keys 디렉토리를 만들고, secrets.json 파일을 생성하세요.
# TODO : json 파일 내에서 세팅을 설정하세요.
_secret_file_path = os.path.join(BASE_DIR, 'input/keys/secrets.json')
with open(_secret_file_path, 'r') as secret_file:
    secrets = json.loads(secret_file.read())

token = secrets["SLACK"]["TOKEN"]
channel_id = secrets["SLACK"]["CHANNEL_ID"]
client = WebClient(token)

USER_NAME = secrets["SLACK"]["USER_NAME"]
COLOR = secrets["SLACK"]["COLOR"]
EMOJI = secrets["SLACK"]["EMOJI"]


def get_format_datas(args, run_type, eval_results):
    pretext = f"Module: {run_type} {EMOJI}"
    author_name = f"전략: {args.strategy} 모델: {args.model.reader_name}"
    title = f"별칭: {args.alias}"
    text = f"*EM*: {eval_results['exact_match']}\n *F1*: {eval_results['f1']}"
    timestamp = int(datetime.datetime.now().timestamp() // 1)

    attachments = [
        {
            "fallback": "Plain-text summary of the attachment.",
            "color": COLOR,
            "pretext": pretext,
            "author_name": author_name,
            "title": title,
            "text": text,
            "footer": f"{USER_NAME}",
            "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
            "ts": timestamp,
        }
    ]

    return attachments


def report_reader_to_slack(args, run_type, eval_results):
    """report_reader_to_slack.
    Args:
        run_type: [run_mrc.py or run.py], 모듈 구분을 위한 인자
        eval_results: dict, {'exact_match': '00.00%', 'f1': '00.00%'}
    """

    attachments = get_format_datas(args, run_type, eval_results)

    try:
        result = client.chat_postMessage(channel=channel_id, attachments=attachments)
        print(result)
    except SlackApiError as e:
        print("Error uploading file: {}".format(e))


def report_retriever_to_slack(fig):
    """retriever 결과를 slack 으로 전송합니다.
    Args:
        fig : plt.Figure, retriever 성능을 비교한 figure
    """
    file_path = "./temp.png"
    fig.savefig(file_path)

    try:
        result = client.files_upload(
            file=file_path,
            channels=channel_id,
            filename="fig_image.png",
            initial_comment="Retrieval Results! :smile:",
            title="_".join([USER_NAME, "Retrievers Results"]),
        )
        print(result)
    except SlackApiError as e:
        print("Error uploading file: {}".format(e))
    finally:
        os.remove(file_path)


if __name__ == "__main__":
    #  fig = plt.figure(figsize=(12, 12))
    #  plt.plot([1, 2, 3, 4])
    #  report_image_to_slack(fig)

    from argparse import Namespace

    eval_results = {"exact_match": "18.75%", "f1": "28.08%"}

    args = Namespace()
    args.strategy = "ST01"
    args.reader_name = "DPR"
    args.alias = "테스트 중입니다!"

    report_reader_to_slack(args, "run.py", eval_results)
