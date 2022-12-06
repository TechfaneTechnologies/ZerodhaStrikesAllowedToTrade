# -*- coding: utf-8 -*-
"""
    :description: A Python Script To Fetch The Nifty, Bank Nifty & Fin Nifty Contracts Allowed For Trading At Zerodha Kite Platform.
    :license: MIT.
    :author: Dr June Moone
    :created: On Monday November 28, 2022 11:17:53 GMT+05:30
"""
__author__ = "Dr June Moone"
__webpage__ = "https://github.com/MooneDrJune"
__license__ = "MIT"

try:
    import json
    import requests
    from lxml import html
    from typing import Tuple, List, Dict, Union
except (ImportError, ModuleNotFoundError):
    __import__("os").system(
        f"{__import__('sys').executable} -m pip install -U requests lxml json"
    )
    import json
    import requests
    from lxml import html
    from typing import Tuple, List, Dict, Union


def fetchAllowedLists(
    url: str = "https://zerodha.com/margin-calculator/SPAN/",
) -> Tuple[List[str], List[str], List[str]]:
    table_data = [
        item.strip()
        for item in html.fromstring(requests.get(url=url).content)
        .xpath('//*[@id="remove_container"]/section[2]/div[2]')[0]
        .text_content()
        .strip()
        .splitlines()
        if item.strip() != ""
    ]

    sec_under_ban = table_data[
        table_data.index("Securities under ban")
        + 1 : table_data.index("Bank Nifty contracts allowed for trading")
    ]
    sec_under_ban = (
        sec_under_ban[: sec_under_ban.index("More information")]
        if "More information" in sec_under_ban
        else sec_under_ban
    )
    bnf_allowed = table_data[
        table_data.index("Bank Nifty contracts allowed for trading")
        + 1 : table_data.index("Nifty contracts allowed for trading")
    ]
    bnf_allowed = (
        bnf_allowed[: bnf_allowed.index("More information")]
        if "More information" in bnf_allowed
        else bnf_allowed
    )
    nf_allowed = table_data[
        table_data.index("Nifty contracts allowed for trading")
        + 1 : table_data.index("Finnifty contracts allowed for trading")
    ]
    nf_allowed = (
        nf_allowed[: nf_allowed.index("More information")]
        if "More information" in nf_allowed
        else nf_allowed
    )
    fnf_allowed = table_data[
        table_data.index("Finnifty contracts allowed for trading") + 1 :
    ]
    fnf_allowed = (
        fnf_allowed[: fnf_allowed.index("More information")]
        if "More information" in fnf_allowed
        else fnf_allowed
    )
    return bnf_allowed, nf_allowed, fnf_allowed


def updateDict(
    allowedList: List[str], FinNifty: bool = False
) -> Dict[str, Dict[str, Union[List[float], str]]]:
    StrikesAllowed = {}
    if len(allowedList) == 1:
        if "More information" in allowedList[0]:
            text = allowedList[0].split("More information")[0].strip()
        else:
            text = allowedList[0]
        allowedList = [
            "Ne" + i if i.startswith("xt") else "Cu" + i if i.startswith("rrent") else i
            for i in [
                _item
                for item in [item.split(" Ne") for item in text.split(" Cu")]
                for _item in item
            ]
        ]
    if not FinNifty:
        for item in allowedList:
            ((nrml, mis,), prd,) = (
                tuple(
                    [
                        item.split(" to ") if " to " in item else item
                        for item in item.split("NRML:")[-1].split("MIS:")
                    ]
                ),
                item.split("-")[0].strip(),
            )
            StrikesAllowed[prd] = {
                "NRML": (
                    {"from": float(nrml[0]), "to": float(nrml[-1])}
                    if isinstance(nrml, list)
                    else nrml.title()
                ),
                "MIS": (
                    {"from": float(mis[0]), "to": float(mis[-1])}
                    if isinstance(mis, list)
                    else mis.title()
                ),
            }
    else:
        for item in allowedList:
            prd = item.split("-")[0].strip()
            prd_data = item.split("-")[-1].strip()
            nrml = prd_data.split(" to ") if " to " in prd_data else prd_data
            StrikesAllowed[prd] = {
                "NRML": (
                    {"from": float(nrml[0]), "to": float(nrml[-1])}
                    if isinstance(nrml, list)
                    else nrml.title()
                ),
                "MIS": (
                    {"from": float(nrml[0]), "to": float(nrml[-1])}
                    if isinstance(nrml, list)
                    else nrml.title()
                ),
            }
    return StrikesAllowed


if __name__ == "__main__":
    (
        bnf_allowed,
        nf_allowed,
        fnf_allowed,
    ) = fetchAllowedLists()
    StrikesAllowed = {
        "BankNifty": updateDict(allowedList=bnf_allowed),
        "Nifty": updateDict(allowedList=nf_allowed),
        "FinNifty": updateDict(allowedList=fnf_allowed, FinNifty=True),
    }
    with open("StrikesAllowed.json", "w") as jsonFile:
        jsonFile.write(json.dumps(StrikesAllowed))
