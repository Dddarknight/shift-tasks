from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class AddTaskModel(BaseModel):
    close_status: bool = Field(validation_alias='СтатусЗакрытия')
    name: str = Field(validation_alias='ПредставлениеЗаданияНаСмену')
    line: str = Field(validation_alias='Рабочий центр')
    shift: str = Field(validation_alias='Смена')
    brigade: str = Field(validation_alias='Бригада')
    consignment_number: int = Field(validation_alias='НомерПартии')
    consignment_date: date = Field(validation_alias='ДатаПартии')
    nomenclature: str = Field(validation_alias='Номенклатура')
    code: str = Field(validation_alias='КодЕКН')
    identifier: str = Field(validation_alias='ИдентификаторРЦ')
    started_at: datetime = Field(validation_alias='ДатаВремяНачалаСмены')
    completed_at: datetime = Field(validation_alias='ДатаВремяОкончанияСмены')

    @field_validator('started_at', 'completed_at')
    def convert(cls, value):
        return value.replace(tzinfo=None)


class AddProductModel(BaseModel):
    product_id: str = Field(validation_alias='УникальныйКодПродукта')
    consignment_number: int = Field(validation_alias='НомерПартии')
    consignment_date: date = Field(validation_alias='ДатаПартии')


class Task(BaseModel):
    close_status: bool
    name: str
    line: str
    shift: str
    brigade: str
    consignment_number: int
    consignment_date: date
    nomenclature: str
    code: str
    identifier: str
    started_at: datetime
    completed_at: datetime
    closed_at: datetime | None
    products: list[str]

    @classmethod
    def from_orm_task(cls, task):
        return cls(
            close_status=task.close_status,
            name=task.name,
            line=task.line,
            shift=task.shift,
            brigade=task.brigade,
            consignment_number=task.consignment.consignment_number,
            consignment_date=task.consignment.consignment_date,
            nomenclature=task.nomenclature,
            code=task.code,
            identifier=task.identifier,
            started_at=task.started_at,
            completed_at=task.completed_at,
            closed_at=task.closed_at,
            products=[
                product.product_id
                for product in task.consignment.products
            ]
        )


class UpdateTaskModel(BaseModel):
    close_status: bool | None = Field(default=None)
    name: str | None = Field(default=None)
    line: str | None = Field(default=None)
    shift: str | None = Field(default=None)
    brigade: str | None = Field(default=None)
    nomenclature: str | None = Field(default=None)
    code: str | None = Field(default=None)
    identifier: str | None = Field(default=None)
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)

    @field_validator('started_at', 'completed_at')
    def convert(cls, value):
        if value:
            return value.replace(tzinfo=None)
        return value
