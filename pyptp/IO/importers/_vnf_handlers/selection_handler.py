"""Handler for parsing VNF Selection sections using a declarative recipe."""

from __future__ import annotations

from typing import Any, ClassVar

from pyptp.elements.mv.selection import SelectionMV
from pyptp.IO.importers._base_handler import DeclarativeHandler, SectionConfig
from pyptp.network_mv import NetworkMV as TNetworkMSType
from pyptp.ptp_log import logger


class SelectionHandler(DeclarativeHandler[TNetworkMSType]):
    """Parses VNF Selection components using a declarative recipe."""

    COMPONENT_CLS = SelectionMV

    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = [
        SectionConfig("general", "#General ", required=True),
        SectionConfig("objects", "#Object ", required=False),
    ]

    def resolve_target_class(self, kwarg_name: str) -> type | None:
        """Resolve target class for Selection-specific fields."""
        if kwarg_name == "objects":
            # Return the nested Object class from TSelectionMS
            return SelectionMV.Object
        return None

    def handle(self, model: TNetworkMSType, raw: str) -> None:
        """Parse and add selections to the model."""
        handler_name = type(self).__name__
        sections = list(self.parse_sections(raw))
        if not sections:
            return

        for section in sections:
            kwargs: dict[str, Any] = {}
            try:
                for config in self.COMPONENT_CONFIG:
                    value = self._process_section_data(section, config)
                    kwargs[config.kwarg_name] = value

                # Ensure all list fields are set to [] if None
                component_cls = self.COMPONENT_CLS
                if hasattr(component_cls, "__annotations__"):
                    for field, ann in component_cls.__annotations__.items():
                        is_list_ann = False
                        if (hasattr(ann, "__origin__") and ann.__origin__ is list) or (
                            isinstance(ann, str) and ann.lower().startswith("list[")
                        ):
                            is_list_ann = True
                        if is_list_ann and kwargs.get(field) is None:
                            kwargs[field] = []

                if kwargs.get("general") is None:
                    continue

                component_to_add = self.COMPONENT_CLS(**kwargs)
                if hasattr(component_to_add, "register"):
                    component_to_add.register(model)
                else:
                    logger.warning("Component from %s does not have a register method.", handler_name)

            except (ValueError, TypeError, KeyError) as e:
                msg = f"Failed to process component in handler {handler_name}: {e}"
                logger.exception(msg)
                logger.debug("Component data that caused failure: %s", kwargs)
                raise type(e)(msg) from e
