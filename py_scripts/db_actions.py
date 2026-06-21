from __future__ import annotations

import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

load_dotenv()

DEFAULT_SQLITE_URL = "sqlite:///./vs_access_panel.sqlite3"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(64))
    password: Mapped[str] = mapped_column(String(64))


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    department_default: Mapped[str] = mapped_column(String(120), default="")
    ad_groups: Mapped[str] = mapped_column(Text, default="")
    onec_groups: Mapped[str] = mapped_column(Text, default="")
    vpn_profile: Mapped[str] = mapped_column(String(120), default="")
    need_email_default: Mapped[bool] = mapped_column(Boolean, default=True)
    need_vpn_default: Mapped[bool] = mapped_column(Boolean, default=False)
    need_onec_default: Mapped[bool] = mapped_column(Boolean, default=True)
    need_bitrix_default: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employees: Mapped[list["Employee"]] = relationship(back_populates="role")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    login: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(180), default="")
    department: Mapped[str] = mapped_column(String(120), default="")
    position: Mapped[str] = mapped_column(String(120), default="")
    manager: Mapped[str] = mapped_column(String(180), default="")
    start_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Новый")

    need_email: Mapped[bool] = mapped_column(Boolean, default=True)
    need_vpn: Mapped[bool] = mapped_column(Boolean, default=False)
    need_onec: Mapped[bool] = mapped_column(Boolean, default=True)
    need_bitrix: Mapped[bool] = mapped_column(Boolean, default=True)

    ad_status: Mapped[str] = mapped_column(String(50), default="Ожидает")
    mail_status: Mapped[str] = mapped_column(String(50), default="Ожидает")
    vpn_status: Mapped[str] = mapped_column(String(50), default="Не требуется")
    onec_status: Mapped[str] = mapped_column(String(50), default="Ожидает")
    bitrix_status: Mapped[str] = mapped_column(String(50), default="Ожидает")

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    role: Mapped[Role] = relationship(back_populates="employees")

    created_by: Mapped[str] = mapped_column(String(120), default="admin")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    disabled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="employee", cascade="all, delete-orphan")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), nullable=True)
    actor: Mapped[str] = mapped_column(String(120), default="admin")
    module: Mapped[str] = mapped_column(String(80), nullable=False)
    action: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employee: Mapped[Optional[Employee]] = relationship(back_populates="audit_logs")


def get_session() -> Session:
    return SessionLocal()


def init_db() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        admin_password = os.getenv("ADMIN_PASSWORD")
        admin_user = User(
            role="admin",
            password=admin_password
        )

        session.add(admin_user)
        session.commit()

    seed_roles()


def seed_roles() -> None:
    default_roles = [
        {
            "code": "storage_worker",
            "name": "Кладовщик",
            "description": "Складская роль: 1С склад, ТСД, без удалённого VPN по умолчанию.",
            "department_default": "Склад",
            "ad_groups": "GG_Sklad, GG_1C_Sklad, GG_TSD_Users",
            "onec_groups": "Склад, ТСД",
            "vpn_profile": "",
            "need_email_default": True,
            "need_vpn_default": False,
            "need_onec_default": True,
            "need_bitrix_default": True,
        },
        {
            "code": "sales_manager",
            "name": "Менеджер продаж",
            "description": "Продажи: 1С продажи, Bitrix24, почта и VPN.",
            "department_default": "Отдел продаж",
            "ad_groups": "GG_Sales, GG_1C_Sales, GG_Bitrix_Users",
            "onec_groups": "Продажи, CRM",
            "vpn_profile": "ovpn-office",
            "need_email_default": True,
            "need_vpn_default": True,
            "need_onec_default": True,
            "need_bitrix_default": True,
        },
        {
            "code": "accountant",
            "name": "Бухгалтер",
            "description": "Бухгалтерия: доступ к 1С Бухгалтерия/КА и удалённый VPN.",
            "department_default": "Бухгалтерия",
            "ad_groups": "GG_Buh, GG_1C_Buh, GG_Reports_Read",
            "onec_groups": "Бухгалтерия, Казначейство",
            "vpn_profile": "ovpn-finance",
            "need_email_default": True,
            "need_vpn_default": True,
            "need_onec_default": True,
            "need_bitrix_default": True,
        },
        {
            "code": "supervisor",
            "name": "Руководитель",
            "description": "Руководитель отдела: отчёты, согласования, расширенный Bitrix24.",
            "department_default": "Руководство",
            "ad_groups": "GG_Managers, GG_Reports, GG_Bitrix_Managers",
            "onec_groups": "Руководитель, Отчёты",
            "vpn_profile": "ovpn-managers",
            "need_email_default": True,
            "need_vpn_default": True,
            "need_onec_default": True,
            "need_bitrix_default": True,
        },
        {
            "code": "it",
            "name": "IT",
            "description": "IT-специалист: технические группы и административные инструменты.",
            "department_default": "IT",
            "ad_groups": "GG_IT, GG_Admin_Tools, GG_VPN_Admins",
            "onec_groups": "Администрирование",
            "vpn_profile": "ovpn-admin",
            "need_email_default": True,
            "need_vpn_default": True,
            "need_onec_default": True,
            "need_bitrix_default": True,
        },
    ]

    with SessionLocal() as session:
        for item in default_roles:
            exists = session.query(Role).filter(Role.code == item["code"]).first()
            if not exists:
                session.add(Role(**item))
        session.commit()

def add_employee(full_name, login, department, position, manager, start_date, email, role_id):
    with engine.connect() as conn:
        stmt = select(Role).where(Role.id == role_id)
        result = conn.execute(stmt).fetchone()
        
        with SessionLocal() as session:
            new_employee = Employee(
                full_name=full_name,
                login=login,
                email=email,
                department=department,
                position=position,
                manager=manager,
                start_date=start_date,
                status="Pending",
                need_email=result[9],
                need_vpn=result[10],
                need_onec=result[11],
                need_bitrix=result[12],
                role_id=role_id
            )

            session.add(new_employee)
            session.flush()
            
            role = session.get(Role, role_id)

            session.add(
                AuditLog(
                    employee_id=new_employee.id,
                    actor="admin",
                    module="Onboarding",
                    action="Создание карточки сотрудника",
                    status="Успешно",
                    message=f"Создана карточка. Логин: {login}. Роль: {role.name}.",
                )
            )

            session.commit()

            return role.name

init_db()