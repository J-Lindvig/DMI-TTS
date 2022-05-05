import logging
import requests
import json

from bs4 import BeautifulSoup as BS
import re

from .const import (
    BASE_URL,
    DMI_TTS_URLS,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


class dmi_tts:
    def __init__(self):
        self._session = requests.Session()
        self._forecasts = {"regions": {}}

    def fetch_data(self):
        for unique_id in DMI_TTS_URLS:
            r = self._session.get(BASE_URL + DMI_TTS_URLS[unique_id])
            if r.status_code == 200:
                json_r = r.json()
                json_r = self._list2dict(json_r)

                if "products" in json_r:
                    json_r["unique_id"] = unique_id
                    if json_r["products"]["text_type"] == "land":
                        self._forecasts["land"] = self._fill_land(json_r)
                    else:
                        self._forecasts["7_days"] = self._fill_7_days(json_r)
                else:
                    region_data = self._list2dict(json_r["regiondata"])
                    region_data["unique_id"] = unique_id
                    self._forecasts["regions"][region_data["name"]] = self._fill_region(
                        region_data
                    )

    def get_data(self):
        return self._forecasts

    def _fill_data_base(self, json_r, products):
        return {
            "name": json_r["name"],
            "unique_id": json_r["unique_id"],
            "timestamp": products["timestamp"],
        }

    def _fill_7_days(self, json_r):
        day_keys = ["et", "to", "tre", "fire", "fem", "sekssyv"]
        products = self._list2dict(json_r["products"])
        xml_soup = BS(products["text"], "xml")
        json_r["name"] = "7-døgnsudsigt"
        data = self._fill_data_base(json_r, products)
        data.update(
            {
                "date": xml_soup.find("dato").text.rstrip("."),
                "preface": "",
                "summary": xml_soup.find("oversigt").text,
                "days": [],
            }
        )
        preface = xml_soup.find("overskriftsyvdgn").text
        idx = preface.find(":") + 1
        data["preface"] = preface[idx:].strip()

        for day in day_keys:
            day_xml = xml_soup.find("dagnavn" + day).find_all("text")
            day_data = {
                "day_name": day_xml[0].text.strip().rstrip(":"),
                "day_forecast": day_xml[1].text.rstrip("."),
            }
            data["days"].append(day_data)

        return data

    def _fill_land(self, json_r):
        products = self._list2dict(json_r["products"])
        xml_soup = BS(products["text"], "xml")
        data = self._fill_data_base(json_r, products)
        data.update(
            {
                "date": xml_soup.find("dato").text.rstrip("."),
                "forecast": xml_soup.find("udsigt").text,
            }
        )

        return data

    def _fill_region(self, json_r):
        products = self._list2dict(json_r["products"])
        xml_soup = BS(products["text"], "xml")
        data = self._fill_data_base(json_r, products)
        data.update(
            {
                "date": xml_soup.find("dato").text.rstrip("."),
                "summary": xml_soup.find(re.compile("^overskrift")).text,
            }
        )

        forecast = xml_soup.find(re.compile("^region")).text
        idx = forecast.find(":") + 1
        data["forecast"] = forecast[idx:]

        return data

    def _list2dict(self, a_List, idx=0):
        if type(a_List) is list:
            return a_List[idx]
        else:
            return a_List
