import os
from time import sleep

import requests


class CrewaiClient:
    KICKOFF_ENDPOINT = "/kickoff"
    STATUS_ENDPOINT = "/status"

    def __init__(self):
        self._url = os.getenv("CREWAI_URL")
        self._token = os.getenv("CREWAI_TOKEN")

    @property
    def kickoff_url(self):
        return f"{self._url}{self.KICKOFF_ENDPOINT}"

    @property
    def status_url(self):
        return f"{self._url}{self.STATUS_ENDPOINT}/"

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self._token}"}

    def kickoff(self, inputs: dict):
        body = {"inputs": inputs}

        response = requests.post(
            self.kickoff_url,
            headers=self.headers,
            json=body,
        )
        response.raise_for_status()
        return response.json()["kickoff_id"]

    def status(self, kickoff_id: str):
        attempts = 0
        max_attempts = 240
        while attempts < max_attempts:
            response = requests.get(
                self.status_url + kickoff_id,
                headers=self.headers,
            )
            response.raise_for_status()
            response_json = response.json()
            if response_json["state"] == "SUCCESS":
                return response_json["result"]
            elif response_json["state"] == "FAILED":
                raise Exception(f"Request failed with status: {response_json}")
            sleep(0.2)
            attempts += 1
        raise Exception(f"Request timed out after {max_attempts} attempts")
