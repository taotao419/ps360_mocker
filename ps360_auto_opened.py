#!/usr/bin/python
import re
import string
import configparser
import requests
import json
import asyncio
import websockets


class Token:
    def __init__(self):
        self.access_token = ""
        self.refresh_token = ""
        self.id_token = ""


def parse_json_to_obj(jsonStr, objClass):
    parseData = json.loads(jsonStr.strip('\t\r\n'))

    result = objClass()
    result.__dict__ = parseData

    return result


def get_token():
    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config.get("connection", "username")
    print(f'username : {username}')
    password = config.get("connection", "password")
    url = config.get("connection", "url")

    payload = {"username": username, "password": password,
               "grant_type": "password", "client_id": "netboot", "scope": "openid"}
    header = {"content-type": "application/x-www-form-urlencoded"}
    res = requests.post(url, data=payload, headers=header)
    token = parse_json_to_obj(res.text, Token)
    return token


def subscribe_hub_endpoint(access_token):
    payload = {"hub.channel.type": "websocket", "hub.mode": "subscribe", "hub.topic": "mockTopic",
               "hub.events": "DiagnosticReport-open,DiagnosticReport-close,DiagnosticReport-update, sycnerror,DiagnosticReport-opened,DiagnosticReport-closed", "hub.leaase_seconds": "1800"}
    header = {"content-type": "application/x-www-form-urlencoded",
              "Authorization": "Bearer "+access_token}
    url = 'https://gfn666cs1.shrnd.agfahealthcare.com/fhircast-hub/'
    res = requests.post(url, data=payload, headers=header)
    result = json.loads(res.text)
    return result['hub.channel.endpoint']


async def clientRun(wss_endpoint):
    async with websockets.connect(wss_endpoint, ping_interval=None) as websocket:
        await wait_until_report_open(websocket)

# 发送回执


async def wait_until_report_open(websocket):
    while True:
        res = await websocket.recv()
        message_data = json.loads(res)
        print(f"message  : [{message_data}]")
        if 'event' in message_data:
            if message_data["event"]["hub.event"] == "DiagnosticReport-open":
                print("\033[32mXWF打开了一个报告\033[0m")
                opened_command = do_opened()
                await websocket.send(opened_command)
                print("\033[32m自动发送 已打开回执\033[0m")
                await websocket.recv()
                print("\033[32m发送成功\033[0m")


def do_opened():
    t = string.Template("""
            {
                "timestamp": "2023-05-12T05:57:45.5080302Z",
                "id": "PSOneFHIRProxy-b20fde0c7ca7446dab29b098fface9f4",
                "event": {
                    "hub.topic": "mockTopic",
                    "hub.event": "DiagnosticReport-opened",
                    "context.versionId": null,
                    "context.priorVersionId": null,
                    "context": [
                        {
                            "key": "OperationOutcome",
                            "reference": null,
                            "resource": {
                                "resourceType": "OperationOutcome",
                                "issue": [
                                    {
                                        "severity": "information",
                                        "diagnostics": "Report with accession(s) '20230512134135' opened."
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
            """)
    print("发送命令 [已打开]")
    return t.template


if __name__ == '__main__':
    print("PS360 模拟器 接受如下命令 [Q]uit [O]pened [Send]")
    print("PS360 模拟器 Send 接受如下状态 final | preliminary | cancelled | partial")
    print("关闭命令 Ex : send cancelled PKODB44 20230529164440")
    token = get_token()
    wss = subscribe_hub_endpoint(token.access_token)
    print(f"\033[32m已经连接到 fhir hub [{wss}] \033[0m")
    asyncio.new_event_loop().run_until_complete(clientRun(wss))
