from datetime import datetime, timezone
import allure
import pytest
from pydantic import TypeAdapter

from src.api_client import PumpsApiClient
from src.models import (
    AlertLevel,
    AlertRequest,
    AlertResponse,
    BolusDeliverResponse,
    HTTPValidationError,
    PumpStateResponse,
    ResetBlockResponse,
)

AlertListAdapter = TypeAdapter(list[AlertResponse])


@allure.epic("Insulin Pump Simulator API")
@allure.feature("Pumps")
class TestPumpsAPI:

    @allure.story("Статус помпы")
    @allure.title("GET /status: успешное получение статуса помпы")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_pump_status_success(self, api_client: PumpsApiClient, pump_id: str) -> None:
        response = api_client.get_status(pump_id)

        assert response.status_code == 200, (
            f"Ожидался статус 200 при получении статуса помпы '{pump_id}', "
            f"получен {response.status_code}: {response.text}"
        )

        state = PumpStateResponse.model_validate(response.json())
        assert state.alerts_count >= 0, (
            f"Количество оповещений не может быть отрицательным, получено: {state.alerts_count}"
        )

    @allure.story("Оповещения помпы")
    @allure.title("GET /alerts: успешное получение списка оповещений")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_pump_alerts_success(self, api_client: PumpsApiClient, pump_id: str) -> None:
        response = api_client.get_alerts(pump_id)

        assert response.status_code == 200, (
            f"Ожидался статус 200 при получении оповещений помпы '{pump_id}', "
            f"получен {response.status_code}: {response.text}"
        )

        AlertListAdapter.validate_python(response.json())

    @allure.story("Оповещения помпы")
    @allure.title("DELETE /alerts: удаление оповещения с уровнем {level}")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "level",
        [
            AlertLevel.OFF,
            AlertLevel.NOTIFICATION,
            AlertLevel.WARNING,
            AlertLevel.CRITICAL,
        ],
    )
    def test_delete_single_alert_by_level(
        self, api_client: PumpsApiClient, pump_id: str, level: AlertLevel
    ) -> None:
        payload = AlertRequest(
            level=level,
            level_str=level.value,
            message="Тестовое оповещение",
            action_message="Проверить помпу",
            timestamp=datetime.now(timezone.utc),
        )

        response = api_client.delete_alert(pump_id, payload)

        assert response.status_code == 200, (
            f"Ожидался статус 200 при удалении оповещения уровня '{level.value}', "
            f"получен {response.status_code}: {response.text}"
        )

        AlertListAdapter.validate_python(response.json())

    @allure.story("Оповещения помпы")
    @allure.title("DELETE /alerts/all: удаление всех оповещений помпы")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_all_alerts_success(self, api_client: PumpsApiClient, pump_id: str) -> None:
        response = api_client.delete_all_alerts(pump_id)

        assert response.status_code == 200, (
            f"Ожидался статус 200 при удалении всех оповещений помпы '{pump_id}', "
            f"получен {response.status_code}: {response.text}"
        )

        AlertListAdapter.validate_python(response.json())

    @allure.story("Управление болюсом")
    @allure.title("POST /bolus/deliver: запрос подачи болюса")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_deliver_bolus_success(self, api_client: PumpsApiClient, pump_id: str) -> None:
        response = api_client.deliver_bolus(pump_id)

        assert response.status_code == 200, (
            f"Ожидался статус 200 при подаче болюса для '{pump_id}', "
            f"получен {response.status_code}: {response.text}"
        )
        result = BolusDeliverResponse.model_validate(response.json())
        assert result.status.strip() != "", "Поле 'status' в ответе bolus/deliver не должно быть пустым"
        assert result.message.strip() != "", "Поле 'message' в ответе bolus/deliver не должно быть пустым"

    @allure.story("Управление блокировкой")
    @allure.title("POST /block/reset: запрет сброса блокировки для незаблокированной помпы")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_reset_block_when_not_blocked(self, api_client: PumpsApiClient, pump_id: str) -> None:
        response = api_client.reset_block(pump_id)

        assert response.status_code == 403, (
            f"Ожидался статус 403 при попытке сброса блокировки незаблокированной помпы '{pump_id}', "
            f"получен {response.status_code}: {response.text}"
        )
        result = ResetBlockResponse.model_validate(response.json())
        assert result.status == "FAILED", (
            f"Ожидался status='FAILED', получен '{result.status}'"
        )
        assert result.message.strip() != "", "Поле 'message' в ответе block/reset не должно быть пустым"

    @allure.story("Негативные сценарии и валидация")
    @allure.title("DELETE /alerts: ошибка 422 при невалидном теле запроса ({case_name})")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "case_name, invalid_payload",
        [
            ("невалидный enum level", {"level": "invalid_level", "timestamp": "2026-11-18T10:00:00Z"}),
            ("невалидный формат timestamp", {"level": "off", "timestamp": "not-a-datetime"}),
            ("неверный тип поля message", {"level": "off", "message": 12345, "timestamp": "2026-11-18T10:00:00Z"}),
        ],
        ids=["invalid_level_enum", "invalid_timestamp", "invalid_message_type"],
    )
    def test_delete_alert_invalid_payload_returns_422(
        self,
        api_client: PumpsApiClient,
        pump_id: str,
        case_name: str,
        invalid_payload: dict,
    ) -> None:
        response = api_client.delete_alert(pump_id, invalid_payload)

        assert response.status_code == 422, (
            f"Для кейса '{case_name}' ожидался статус 422 Validation Error, "
            f"получен {response.status_code}: {response.text}"
        )
        error = HTTPValidationError.model_validate(response.json())
        assert len(error.detail) > 0, "Список ошибок валидации detail не должен быть пустым"

    @allure.story("Негативные сценарии и граничные значения")
    @allure.title("GET /status: обработка граничных значений pump_id ({case_name})")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.parametrize(
        "case_name, boundary_pump_id, expected_statuses",
        [
            ("пустая строка", "", {404, 405, 422}),
            ("пробелы", "   ", {200, 400, 422}),
            ("максимально длинный id (256 символов)", "p" * 256, {200, 400, 414, 422}),
            ("спецсимволы", "pump_!@$", {200, 400, 422}),
        ],
        ids=["empty_id", "spaces_id", "long_256_id", "special_chars_id"],
    )
    def test_get_status_boundary_pump_id(
        self,
        api_client: PumpsApiClient,
        case_name: str,
        boundary_pump_id: str,
        expected_statuses: set,
    ) -> None:
        response = api_client.get_status(boundary_pump_id)

        assert response.status_code < 500, (
            f"Сервер упал с 5xx ошибкой на граничном pump_id ({case_name}): "
            f"{response.status_code} {response.text}"
        )
        assert response.status_code in expected_statuses, (
            f"Для '{case_name}' ожидался один из статусов {expected_statuses}, "
            f"получен {response.status_code}: {response.text}"
        )

    @allure.story("Негативные сценарии и валидация")
    @allure.title("GET /status: неподдерживаемый HTTP-метод PUT возвращает 405")
    @allure.severity(allure.severity_level.MINOR)
    def test_status_unsupported_method_returns_405(self, api_client: PumpsApiClient, pump_id: str) -> None:
        response = api_client.session.put(
            f"{api_client.base_url}/api/v1/pumps/{pump_id}/status",
            timeout=api_client.timeout,
        )

        assert response.status_code == 405, (
            f"Ожидался статус 405 Method Not Allowed для PUT /status, "
            f"получен {response.status_code}: {response.text}"
        )