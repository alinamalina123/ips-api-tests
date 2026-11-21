from typing import Any, Dict, Union
import allure
import requests

from src.models import AlertRequest


class PumpsApiClient:
    """API-клиент для раздела Pumps сервиса Insulin Pump Simulator."""

    def __init__(self, base_url: str = "https://ips.alexgallax-edu.ru", timeout: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    @allure.step("GET /api/v1/pumps/{pump_id}/status — получение статуса помпы")
    def get_status(self, pump_id: str) -> requests.Response:
        return self.session.get(
            f"{self.base_url}/api/v1/pumps/{pump_id}/status",
            timeout=self.timeout,
        )

    @allure.step("GET /api/v1/pumps/{pump_id}/alerts — получение списка оповещений")
    def get_alerts(self, pump_id: str) -> requests.Response:
        return self.session.get(
            f"{self.base_url}/api/v1/pumps/{pump_id}/alerts",
            timeout=self.timeout,
        )

    @allure.step("DELETE /api/v1/pumps/{pump_id}/alerts — удаление конкретного оповещения")
    def delete_alert(self, pump_id: str, payload: Union[AlertRequest, Dict[str, Any]]) -> requests.Response:
        json_body = payload.model_dump(mode="json") if isinstance(payload, AlertRequest) else payload
        return self.session.delete(
            f"{self.base_url}/api/v1/pumps/{pump_id}/alerts",
            json=json_body,
            timeout=self.timeout,
        )

    @allure.step("DELETE /api/v1/pumps/{pump_id}/alerts/all — удаление всех оповещений")
    def delete_all_alerts(self, pump_id: str) -> requests.Response:
        return self.session.delete(
            f"{self.base_url}/api/v1/pumps/{pump_id}/alerts/all",
            timeout=self.timeout,
        )

    @allure.step("POST /api/v1/pumps/{pump_id}/bolus/deliver — подача болюса")
    def deliver_bolus(self, pump_id: str) -> requests.Response:
        return self.session.post(
            f"{self.base_url}/api/v1/pumps/{pump_id}/bolus/deliver",
            timeout=self.timeout,
        )

    @allure.step("POST /api/v1/pumps/{pump_id}/block/reset — сброс блокировки помпы")
    def reset_block(self, pump_id: str) -> requests.Response:
        return self.session.post(
            f"{self.base_url}/api/v1/pumps/{pump_id}/block/reset",
            timeout=self.timeout,
        )