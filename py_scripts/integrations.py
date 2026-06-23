from __future__ import annotations

from db import AuditLog, Employee, SessionLocal

MODULE_STATUS_FIELD = {
    "ad": "ad_status",
    "mail": "mail_status",
    "vpn": "vpn_status",
    "onec": "onec_status",
    "bitrix": "bitrix_status",
}

MODULE_TITLE = {
    "ad": "Active Directory",
    "mail": "Почта",
    "vpn": "MikroTik / OpenVPN",
    "onec": "1С",
    "bitrix": "Bitrix24",
}


def run_demo_step(employee_id: int, module: str, actor: str = "admin") -> None:
    if module not in MODULE_STATUS_FIELD:
        raise ValueError("Unknown module")

    with SessionLocal() as session:
        employee = session.get(Employee, employee_id)
        if not employee:
            raise ValueError("Employee not found")

        setattr(employee, MODULE_STATUS_FIELD[module], "Готово")
        employee.status = _calculate_employee_status(employee)
        session.add(
            AuditLog(
                employee_id=employee.id,
                actor=actor,
                module=MODULE_TITLE[module],
                action="Демо-выполнение этапа",
                status="Успешно",
                message="Интеграция пока работает в демо-режиме. Реальное подключение добавляется отдельным сервисным модулем.",
            )
        )
        session.commit()


def disable_employee(employee_id: int, actor: str = "admin") -> None:
    with SessionLocal() as session:
        employee = session.get(Employee, employee_id)
        if not employee:
            raise ValueError("Employee not found")

        employee.status = "Уволен / отключен"
        employee.ad_status = "Отключен"
        if employee.need_email:
            employee.mail_status = "Отключен"
        if employee.need_vpn:
            employee.vpn_status = "Отключен"
        if employee.need_onec:
            employee.onec_status = "Отключен"
        if employee.need_bitrix:
            employee.bitrix_status = "Отключен"

        session.add(
            AuditLog(
                employee_id=employee.id,
                actor=actor,
                module="Access Lifecycle",
                action="Отключение сотрудника",
                status="Успешно",
                message="В MVP статус отключения выставлен в панели. Боевые действия AD/VPN/1С подключаются через интеграционные модули.",
            )
        )
        session.commit()


def _calculate_employee_status(employee: Employee) -> str:
    required_statuses = [employee.ad_status]
    if employee.need_email:
        required_statuses.append(employee.mail_status)
    if employee.need_vpn:
        required_statuses.append(employee.vpn_status)
    if employee.need_onec:
        required_statuses.append(employee.onec_status)
    if employee.need_bitrix:
        required_statuses.append(employee.bitrix_status)

    if all(status == "Готово" for status in required_statuses):
        return "Готово"
    if any(status == "Готово" for status in required_statuses):
        return "Частично готово"
    return "Новый"
