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


async def clientSend(websocket):
    while True:
        input_text = input(
            "Accept commands [Q]uit [O]pened [Send] :")

        if re.search(r"^send\s\w+\s\w{7}\s\d{14}$", input_text):
            cmds = input_text.split(' ')
            report_status = cmds[1]
            pid = cmds[2]
            acc_num = cmds[3]
            command = do_send(pid, acc_num, report_status)
            await websocket.send(command)
            await websocket.recv()
            print("\033[32m发送成功\033[0m")
        elif input_text == "O":
            opened_command = do_opened()
            await websocket.send(opened_command)
            await websocket.recv()
            print("\033[32m发送成功\033[0m")
        elif input_text == "Q":
            print('\033[32m关闭 Fhir hub 连接\033[0m')
            await websocket.close(reason="exit")
            return False
        else:
            print("命令貌似有点问题 ex: send cancelled PKODB44 20230529164440")


async def clientRun(wss_endpoint):
    async with websockets.connect(wss_endpoint) as websocket:
        await clientSend(websocket)

# 发送回执


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


def do_send(patient_id, accession_number, report_status):
    templ = string.Template("""
            {
                "timestamp": "2023-04-13T06:49:14.5099622Z",
                "id": "PSOneFHIRProxy-1a92790327fa4c8594d3ab010cbdf2ee",
                "event": {
                    "hub.topic": "mockTopic",
                    "hub.event": "DiagnosticReport-close",
                    "context": [
                    {
                        "key": "patient",
                        "resource": {
                        "resourceType": "Patient",
                        "id": "28c7253298fd4aa9b92b4b6c9260036c",
                        "identifier": [
                            {
                            "use": "usual",
                            "type": {
                                "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                    "code": "MR"
                                }
                                ]
                            },
                            "value": "${patient_id}"
                            }
                        ]
                        }
                    },
                    {
                        "key": "study",
                        "resource": {
                        "resourceType": "ImagingStudy",
                        "id": "c097f4c76c2046439e7b52f364a01a38",
                        "identifier": [
                            {
                            "use": "usual",
                            "type": {
                                "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                    "code": "ACSN"
                                }
                                ]
                            },
                            "value": "${accession_number}"
                            }
                        ],
                        "subject": {
                            "reference": "Patient/28c7253298fd4aa9b92b4b6c9260036c"
                        }
                        }
                    },
                    {
                        "key": "report",
                        "resource": {
                        "resourceType": "DiagnosticReport",
                        "id": "99cdf7b82c3049a6be4bca227043aa64",
                        "meta": {
                            "versionId": "0"
                        },
                        "status": "${report_status}",
                        "imagingStudy": [
                            {
                            "reference": "ImagingStudy/c097f4c76c2046439e7b52f364a01a38"
                            }
                        ]
                        }
                    }
                    ]
                }
                }
            """)
    values = {"patient_id": patient_id,
              "accession_number": accession_number, "report_status": report_status}
    print("发送命令 状态[{}] patient_id : [{}] accession_number : [{}]".format(
        report_status, patient_id, accession_number))
    return templ.substitute(values)


if __name__ == '__main__':
    print("PS360 模拟器 接受如下命令 [Q]uit [O]pened [Send]")
    print("关闭命令 Ex : send cancelled PKODB44 20230529164440")
    token = get_token()
    wss = subscribe_hub_endpoint(token.access_token)
    print(f"\033[32m已经连接到 fhir hub [{wss}] \033[0m")
    asyncio.new_event_loop().run_until_complete(clientRun(wss))
