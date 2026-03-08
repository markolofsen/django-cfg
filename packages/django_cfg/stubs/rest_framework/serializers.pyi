# Stub override for rest_framework.serializers — bundled with django-cfg.
# Installed automatically into user project's typings/ via setup_types module.
#
# Key fix: @overload for is_valid(raise_exception=Literal[True]) -> Literal[True]
# so Pyright stops reporting false positives on validated_data access.
# validated_data -> dict[str, Any] for Serializer/ModelSerializer
# validated_data -> list[dict[str, Any]] for ListSerializer

from collections.abc import Iterable, Iterator, Mapping, MutableMapping, Sequence
from typing import Any, ClassVar, Literal, NoReturn, overload

from django.db import models
from django.utils.functional import cached_property
from rest_framework.exceptions import ErrorDetail as ErrorDetail
from rest_framework.exceptions import ValidationError as ValidationError
from rest_framework.fields import Field as Field
from rest_framework.fields import HiddenField as HiddenField
from rest_framework.fields import SerializerMethodField as SerializerMethodField
from rest_framework.fields import empty as empty
from rest_framework.utils.model_meta import FieldInfo, RelationInfo
from rest_framework.utils.serializer_helpers import BindingDict, BoundField, ReturnDict, ReturnList
from rest_framework.validators import BaseUniqueForValidator, UniqueTogetherValidator

LIST_SERIALIZER_KWARGS: Sequence[str]
LIST_SERIALIZER_KWARGS_REMOVE: Sequence[str]
ALL_FIELDS: str


class BaseSerializer:
    partial: bool
    many: bool
    instance: Any
    initial_data: Any
    _context: dict[str, Any]

    def __new__(cls, *args: Any, **kwargs: Any) -> Any: ...
    def __class_getitem__(cls, *args: Any, **kwargs: Any) -> Any: ...
    def __init__(
        self,
        instance: Any = ...,
        data: Any = ...,
        *,
        partial: bool = ...,
        many: bool = ...,
        allow_empty: bool = ...,
        context: dict[str, Any] = ...,
        read_only: bool = ...,
        write_only: bool = ...,
        required: bool | None = None,
        default: Any = ...,
        initial: Any = ...,
        source: str | None = None,
        label: Any = None,
        help_text: Any = None,
        style: dict[str, Any] | None = None,
        error_messages: dict[str, Any] | None = None,
        validators: Sequence[Any] | None = ...,
        allow_null: bool = ...,
    ) -> None: ...
    @classmethod
    def many_init(cls, *args: Any, **kwargs: Any) -> BaseSerializer: ...
    @overload
    def is_valid(self, *, raise_exception: Literal[True]) -> Literal[True]: ...
    @overload
    def is_valid(self, *, raise_exception: Literal[False] = ...) -> bool: ...
    @overload
    def is_valid(self, *, raise_exception: bool = ...) -> bool: ...
    @property
    def data(self) -> Any: ...
    @property
    def errors(self) -> Iterable[Any]: ...
    @property
    def validated_data(self) -> dict[str, Any]: ...
    def update(self, instance: Any, validated_data: Any) -> Any: ...
    def create(self, validated_data: Any) -> Any: ...
    def save(self, **kwargs: Any) -> Any: ...
    def to_representation(self, instance: Any) -> Any: ...


class SerializerMetaclass(type):
    def __new__(cls, name: Any, bases: Any, attrs: Any) -> Any: ...
    @classmethod
    def _get_declared_fields(cls, bases: Sequence[type], attrs: dict[str, Any]) -> dict[str, Field]: ...


def as_serializer_error(exc: Exception) -> dict[str, list[ErrorDetail]]: ...


class Serializer(BaseSerializer, metaclass=SerializerMetaclass):
    _declared_fields: dict[str, Field]
    default_error_messages: ClassVar[dict[str, Any]]

    def get_initial(self) -> Any: ...
    def set_value(self, dictionary: MutableMapping[str, Any], keys: Sequence[str], value: Any) -> None: ...
    @cached_property
    def fields(self) -> BindingDict: ...
    def get_fields(self) -> dict[str, Field]: ...
    def to_representation(self, instance: Any) -> dict[str, Any]: ...
    def validate(self, attrs: Any) -> Any: ...
    def __iter__(self) -> Iterator[BoundField]: ...
    def __getitem__(self, key: str) -> BoundField: ...
    def _read_only_defaults(self) -> dict[str, Any]: ...
    @property
    def _writable_fields(self) -> list[Field]: ...
    @property
    def _readable_fields(self) -> list[Field]: ...
    @property
    def data(self) -> ReturnDict: ...
    @property
    def errors(self) -> ReturnDict: ...
    @property
    def validated_data(self) -> dict[str, Any]: ...


class ListSerializer(BaseSerializer):
    child: Field | BaseSerializer | None
    many: bool
    default_error_messages: ClassVar[dict[str, Any]]
    allow_empty: bool | None

    def __init__(
        self,
        instance: Any = ...,
        data: Any = ...,
        partial: bool = ...,
        context: dict[str, Any] = ...,
        allow_empty: bool = ...,
        child: Any = ...,
        read_only: bool = ...,
        write_only: bool = ...,
        required: bool | None = None,
        default: Any = ...,
        initial: Any = ...,
        source: str | None = None,
        label: Any = None,
        help_text: Any = None,
        style: dict[str, Any] | None = None,
        error_messages: dict[str, Any] | None = None,
        validators: Sequence[Any] | None = ...,
        allow_null: bool = ...,
        min_length: int | None = ...,
        max_length: int | None = ...,
    ) -> None: ...
    def run_child_validation(self, data: Any) -> Any: ...
    def to_representation(self, data: Any) -> list[Any]: ...
    def get_initial(self) -> list[Mapping[Any, Any]]: ...
    def validate(self, attrs: Any) -> Any: ...
    @property
    def data(self) -> ReturnList: ...
    @property
    def errors(self) -> ReturnList: ...
    @property
    def validated_data(self) -> list[dict[str, Any]]: ...


def raise_errors_on_nested_writes(method_name: str, serializer: BaseSerializer, validated_data: Any) -> None: ...


class ModelSerializer(Serializer):
    serializer_field_mapping: ClassVar[dict[type[models.Field], type[Field]]]
    serializer_related_field: ClassVar[type[Any]]
    serializer_related_to_field: ClassVar[type[Any]]
    serializer_url_field: ClassVar[type[Any]]
    serializer_choice_field: ClassVar[type[Field]]
    url_field_name: ClassVar[str | None]

    class Meta:
        model: ClassVar[type[Any]]
        fields: ClassVar[Sequence[str] | Literal["__all__"]]
        read_only_fields: ClassVar[Sequence[str] | None]
        exclude: ClassVar[Sequence[str] | None]
        depth: ClassVar[int | None]
        extra_kwargs: ClassVar[dict[str, dict[str, Any]]]

    def __init__(
        self,
        instance: Any = ...,
        data: Any = ...,
        *,
        partial: bool = ...,
        many: bool = ...,
        context: dict[str, Any] = ...,
        read_only: bool = ...,
        write_only: bool = ...,
        required: bool | None = None,
        default: Any = ...,
        initial: Any = ...,
        source: str | None = None,
        label: Any = None,
        help_text: Any = None,
        style: dict[str, Any] | None = None,
        error_messages: dict[str, Any] | None = None,
        validators: Sequence[Any] | None = ...,
        allow_null: bool = ...,
        allow_empty: bool = ...,
    ) -> None: ...
    def update(self, instance: Any, validated_data: Any) -> Any: ...
    def create(self, validated_data: Any) -> Any: ...
    def save(self, **kwargs: Any) -> Any: ...
    def get_field_names(self, declared_fields: Mapping[str, Field], info: FieldInfo) -> list[str]: ...
    def get_default_field_names(self, declared_fields: Mapping[str, Field], model_info: FieldInfo) -> list[str]: ...
    def build_field(self, field_name: str, info: FieldInfo, model_class: type, nested_depth: int) -> tuple[type[Field], dict[str, Any]]: ...
    def build_standard_field(self, field_name: str, model_field: models.Field) -> tuple[type[Field], dict[str, Any]]: ...
    def build_relational_field(self, field_name: str, relation_info: RelationInfo) -> tuple[type[Field], dict[str, Any]]: ...
    def build_nested_field(self, field_name: str, relation_info: RelationInfo, nested_depth: int) -> tuple[type[Field], dict[str, Any]]: ...
    def build_property_field(self, field_name: str, model_class: type) -> tuple[type[Field], dict[str, Any]]: ...
    def build_url_field(self, field_name: str, model_class: type) -> tuple[type[Field], dict[str, Any]]: ...
    def build_unknown_field(self, field_name: str, model_class: type) -> NoReturn: ...
    def include_extra_kwargs(self, kwargs: MutableMapping[str, Any], extra_kwargs: MutableMapping[str, Any]) -> MutableMapping[str, Any]: ...
    def get_extra_kwargs(self) -> dict[str, Any]: ...
    def get_unique_together_constraints(self, model: Any) -> Iterator[tuple[set[tuple[str, ...]], Any]]: ...
    def get_uniqueness_extra_kwargs(self, field_names: Iterable[str], declared_fields: Mapping[str, Field], extra_kwargs: dict[str, Any]) -> tuple[dict[str, Any], dict[str, HiddenField]]: ...
    def _get_model_fields(self, field_names: Iterable[str], declared_fields: Mapping[str, Field], extra_kwargs: MutableMapping[str, Any]) -> dict[str, models.Field]: ...
    def get_unique_together_validators(self) -> list[UniqueTogetherValidator]: ...
    def get_unique_for_date_validators(self) -> list[BaseUniqueForValidator]: ...


class HyperlinkedModelSerializer(ModelSerializer): ...
