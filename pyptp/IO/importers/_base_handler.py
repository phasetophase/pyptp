"""Declarative handler pattern for parsing GNF/VNF format elements into network components.

Provides a generic, configuration-driven approach to convert file format sections
into PyPtP network elements using class annotations and custom deserializers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

from pyptp.ptp_log import logger

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

NetworkModel = TypeVar("NetworkModel")
ParsedSection = dict[str, list[str]]


@dataclass
class SectionConfig:
    """Configuration mapping between file format tags and component attributes.

    Defines how file sections map to component constructor parameters,
    enabling declarative specification of parsing behavior.
    """

    kwarg_name: str  # Component constructor parameter name
    gnf_tag: str  # File format section tag (e.g., "#General ", "#Presentation ")
    required: bool = False


class DeclarativeHandler(Generic[NetworkModel]):
    """Base handler implementing declarative parsing pattern for GNF/VNF formats.

    Converts file format sections into network components using configuration-driven
    approach. Subclasses declare their parsing requirements through COMPONENT_CONFIG,
    enabling automatic deserialization and network registration.

    The declarative pattern separates parsing logic from element structure,
    allowing handlers to focus on format-specific concerns while leveraging
    shared deserialization and validation infrastructure.
    """

    COMPONENT_CLS: ClassVar[type[Any]]
    COMPONENT_CONFIG: ClassVar[list[SectionConfig]] = []
    ADD_METHOD: ClassVar[Callable]
    SECTION_REGEX: ClassVar[str] = r"#General.+?(?=\n#General|\#END|\n\[\]|$)"

    _compiled_section_regex: ClassVar[re.Pattern[str]] | None = None
    _logged_missing_classes: ClassVar[set[str]] = set()

    @classmethod
    def _get_section_regex(cls) -> re.Pattern[str]:
        """Get or create compiled regex pattern for section parsing optimization."""
        if cls._compiled_section_regex is None:
            cls._compiled_section_regex = re.compile(cls.SECTION_REGEX, re.DOTALL)
        return cls._compiled_section_regex

    def parse_sections(self, raw: str) -> Iterable[ParsedSection]:
        """Parse file content into structured sections for component construction.

        Args:
            raw: File content containing multiple component sections.

        Yields:
            Parsed section data organized by configuration tags.

        """
        tag_lookup = {config.gnf_tag for config in self.COMPONENT_CONFIG}
        section_regex = self._get_section_regex()

        for section_text in section_regex.findall(raw):
            parsed: ParsedSection = {tag: [] for tag in tag_lookup}

            lines = [line.strip() for line in section_text.splitlines() if line.strip()]

            for line in lines:
                for gnf_tag in tag_lookup:
                    if line.startswith(gnf_tag):
                        payload = line[len(gnf_tag) :].strip()
                        parsed[gnf_tag].append(payload)
                        break

            yield parsed

    def _parse_gnf_line_to_dict(self, payload: str) -> dict[str, Any]:
        """Parse property line into key-value dictionary with type coercion.

        Handles quoted strings, numeric values, boolean literals, and special
        text content while supporting electrical engineering property names.

        Args:
            payload: Property string from file format line.

        Returns:
            Dictionary with parsed and type-converted properties.

        """
        parsed_dict = {}

        # Support electrical protection property names with special characters
        key_value_pattern = re.compile(r"([\w><,/]+):(?:'([^']*)'|([^\s]+))")

        for match in key_value_pattern.finditer(payload):
            key = match.group(1)
            # Value is either the quoted group (2) or the unquoted group (3)
            val_str = match.group(2) if match.group(2) is not None else match.group(3)

            if match.group(2) is None:
                if val_str == "true":
                    parsed_dict[key] = True
                    continue
                if val_str == "false":
                    parsed_dict[key] = False
                    continue

                if val_str.isdigit():
                    parsed_dict[key] = int(val_str)
                else:
                    try:
                        # Handle European decimal separator
                        parsed_dict[key] = float(val_str.replace(",", "."))
                    except (ValueError, TypeError):
                        parsed_dict[key] = val_str
            else:
                parsed_dict[key] = val_str

        return parsed_dict

    def resolve_target_class(self, kwarg_name: str) -> type[Any] | None:  # noqa: ARG002
        """Override in subclasses to provide custom target class resolution.

        Args:
            kwarg_name: Component field name requiring class resolution.

        Returns:
            Target class for deserialization, or None if not found.

        """
        return None

    def _process_section_data(self, section: ParsedSection, config: SectionConfig) -> object | list[object] | None:  # noqa: C901, PLR0911, PLR0912
        """Process raw section data into component objects using appropriate deserializers.

        Args:
            section: Parsed section data organized by tags.
            config: Section configuration defining processing requirements.

        Returns:
            Deserialized object, list of objects, or None based on configuration.

        Raises:
            ValueError: If required section is missing or target class unavailable.

        """
        raw_data = section.get(config.gnf_tag, [])

        # Check component annotations to determine if field expects list values
        is_list = False
        component_cls = self.COMPONENT_CLS
        if hasattr(component_cls, "__annotations__") and config.kwarg_name in component_cls.__annotations__:
            ann = component_cls.__annotations__[config.kwarg_name]
            # Handle string annotations from future imports
            if isinstance(ann, str):
                is_list = ann.startswith("list[")
            elif hasattr(ann, "__origin__") and ann.__origin__ is list:
                is_list = True

        if not raw_data:
            if is_list:
                return []
            if config.required:
                msg = f"Required GNF section '{config.gnf_tag}' is missing"
                raise ValueError(msg)
            return None

        # Process text-based sections with format-specific handling
        if config.gnf_tag in (
            "#Note Text:",
            "#Extra Text:",
            "#Comment",
            "#Comment Text:",
            "#Line Text:",
        ):
            if config.kwarg_name == "notes":
                from pyptp.elements.mixins import Note

                return [Note(text=text) for text in raw_data]
            if config.kwarg_name == "extras":
                from pyptp.elements.mixins import Extra

                return [Extra(text=text) for text in raw_data]
            if config.kwarg_name == "lines":
                # Return plain strings for lines
                return list(raw_data)
            if config.kwarg_name == "comment":
                # Convert raw text to Comment-compatible format
                if raw_data:
                    text = " ".join(raw_data) if len(raw_data) > 1 else raw_data[0]
                    return {"Text": text}
                return {"Text": ""}
            return raw_data

        parsed_data = [self._parse_gnf_line_to_dict(line) for line in raw_data]
        target_cls = self._get_target_class(config.kwarg_name)

        # Import shared classes dynamically to avoid circular dependencies
        if target_cls is None and config.kwarg_name in [
            "efficiencyType",
            "Qcontrol",
            "InverterRendement",
        ]:
            from pyptp.elements.mv.shared import EfficiencyType, QControl

            if config.kwarg_name in ["efficiencyType", "InverterRendement"]:
                target_cls = EfficiencyType
            elif config.kwarg_name == "Qcontrol":
                target_cls = QControl
        elif target_cls is None and config.kwarg_name in [
            "cableType",
            "cablepart_geography",
            "fields",
            "fuse1_h1",
            "fuse1_h2",
            "fuse1_h3",
            "fuse1_h4",
            "fuse2_h1",
            "fuse2_h2",
            "fuse2_h3",
            "fuse2_h4",
            "current1_h1",
            "current1_h2",
            "current1_h3",
            "current1_h4",
            "current2_h1",
            "current2_h2",
            "current2_h3",
            "current2_h4",
        ]:
            from pyptp.elements.lv.shared import (
                CableType,
                CurrentType,
                Fields,
                FuseType,
                GeoCablePart,
            )

            if config.kwarg_name == "cableType":
                target_cls = CableType
            elif config.kwarg_name == "cablepart_geography":
                target_cls = GeoCablePart
            elif config.kwarg_name == "fields":
                target_cls = Fields
            elif config.kwarg_name.startswith("fuse"):
                target_cls = FuseType
            elif config.kwarg_name.startswith("current"):
                target_cls = CurrentType

        if target_cls is None:
            # Prevent duplicate logging for missing class resolution
            log_key = f"{component_cls.__name__}:{config.kwarg_name}"
            if log_key not in self._logged_missing_classes:
                self._logged_missing_classes.add(log_key)
                logger.debug(
                    "No target class found for %r in handler for %s",
                    config.kwarg_name,
                    component_cls.__name__,
                )
            if is_list:
                return []
            if config.required:
                msg = f"No target class found for required field '{config.kwarg_name}' in {component_cls.__name__}"
                raise ValueError(msg)
            return None

        # Prefer deserialize method over direct constructor for complex objects
        if hasattr(target_cls, "deserialize"):
            if is_list:
                return [target_cls.deserialize(data) for data in parsed_data]
            return target_cls.deserialize(parsed_data[0]) if parsed_data else None
        if is_list:
            return [target_cls(**data) for data in parsed_data]
        return target_cls(**parsed_data[0]) if parsed_data else None

    def _get_target_class(self, kwarg_name: str) -> type[Any] | None:
        """Resolve target class for field deserialization using multiple strategies.

        Args:
            kwarg_name: Component field name requiring class resolution.

        Returns:
            Target class for deserialization, or None if resolution fails.

        """
        # Allow handler-specific class resolution logic
        result = self.resolve_target_class(kwarg_name)
        if result is not None:
            return result

        # Primary resolution through component type annotations
        annotation_result = self._get_class_from_annotations(kwarg_name)
        if annotation_result is not None:
            return annotation_result

        # Handle presentation classes requiring special logic
        if kwarg_name == "presentations":
            return self._get_presentation_class()

        # Use fallback mappings for common field patterns
        return self._get_fallback_class(kwarg_name)

    def _get_class_from_annotations(self, kwarg_name: str) -> type[Any] | None:
        """Extract target class from component type annotations.

        Args:
            kwarg_name: Field name to resolve from annotations.

        Returns:
            Class extracted from annotations, or None if not found.

        """
        component_cls = self.COMPONENT_CLS
        if not hasattr(component_cls, "__annotations__"):
            return None

        annotations = component_cls.__annotations__
        if kwarg_name not in annotations:
            return None

        target_type = annotations[kwarg_name]
        # Handle string annotations from future imports
        if isinstance(target_type, str):
            # Resolve nested class names by convention
            nested = getattr(component_cls, kwarg_name.capitalize(), None)
            return nested if nested is not None else None

        # Extract base type from generic annotations
        if (hasattr(target_type, "__origin__") and target_type.__origin__ is list) or (
            hasattr(target_type, "__origin__") and target_type.__origin__ is type
        ):
            return target_type.__args__[0]
        return target_type

    def _get_presentation_class(self) -> type[Any] | None:
        """Resolve presentation class based on component type and voltage level.

        Returns:
            Appropriate presentation class for LV or MV networks.

        """
        component_cls = self.COMPONENT_CLS
        class_name = component_cls.__name__

        # Map component classes to their presentation types by voltage level
        presentation_mappings = {
            "TNodeLS": ("lv", "NodePresentation"),
            "TNodeMS": ("mv", "NodePresentation"),
            "TCableLS": ("lv", "BranchPresentation"),
            "TCableMS": ("mv", "BranchPresentation"),
            "TTransformerLS": ("lv", "ElementPresentation"),
            "TTransformerMS": ("mv", "ElementPresentation"),
            "TPropertiesMS": ("mv", "SecondaryPresentation"),
        }

        if class_name in presentation_mappings:
            module_type, presentation_type = presentation_mappings[class_name]
            if module_type == "lv":
                from pyptp.elements.lv.presentations import (
                    BranchPresentation,
                    ElementPresentation,
                    NodePresentation,
                )

                mapping = {
                    "NodePresentation": NodePresentation,
                    "BranchPresentation": BranchPresentation,
                    "ElementPresentation": ElementPresentation,
                }
                return mapping[presentation_type]
            from pyptp.elements.mv.presentations import (
                BranchPresentation,
                ElementPresentation,
                NodePresentation,
                SecondaryPresentation,
            )

            mapping = {
                "NodePresentation": NodePresentation,
                "BranchPresentation": BranchPresentation,
                "ElementPresentation": ElementPresentation,
                "SecondaryPresentation": SecondaryPresentation,
            }
            return mapping[presentation_type]

        # Fallback to voltage-level appropriate default presentation
        try:
            module_name = component_cls.__module__
            if "lv" in module_name:
                from pyptp.elements.lv.presentations import ElementPresentation

                return ElementPresentation
            if "mv" in module_name:
                from pyptp.elements.mv.presentations import ElementPresentation

                return ElementPresentation
        except ImportError:
            pass
        return None

    def _get_fallback_class(self, kwarg_name: str) -> type[Any] | None:
        """Resolve target class using fallback mappings for common patterns.

        Args:
            kwarg_name: Field name requiring class resolution.

        Returns:
            Class from fallback mappings, or None if not found.

        """
        component_cls = self.COMPONENT_CLS

        # Common field name to nested class mappings
        fallback_mappings = {
            "general": getattr(component_cls, "General", None),
            "extras": None,  # Handled in _process_section_data
            "notes": None,  # Handled in _process_section_data
        }

        # PV-specific mappings for complex nested structures
        if component_cls.__name__ == "TPvMS":
            pv_mappings = {
                "inverter": getattr(component_cls, "Inverter", None),
                "efficiencyType": None,  # Imported dynamically in _process_section_data
                "Qcontrol": None,  # Imported dynamically in _process_section_data
                "PUcontrol": getattr(component_cls, "PUControl", None),
                "PFcontrol": getattr(component_cls, "PFControl", None),
                "PIcontrol": getattr(component_cls, "PIControl", None),
                "InverterRendement": None,  # Imported dynamically in _process_section_data
                "restrictions": getattr(component_cls, "Capacity", None),
            }
            fallback_mappings.update(pv_mappings)

        result = fallback_mappings.get(kwarg_name)
        return None if isinstance(result, str) else result

    def handle(self, model: NetworkModel, raw: str) -> None:
        """Parse file content and register components in the network model.

        Args:
            model: Target network for component registration.
            raw: File content containing component sections.

        Raises:
            NotImplementedError: If subclass doesn't define COMPONENT_CLS.
            ValueError: If component processing fails.
            TypeError: If component construction fails.
            KeyError: If required configuration is missing.

        """
        handler_name = type(self).__name__
        if not self.COMPONENT_CLS:
            msg = f"Subclass '{handler_name}' must define COMPONENT_CLS"
            raise NotImplementedError(msg)

        sections = list(self.parse_sections(raw))
        if not sections:
            return

        for section in sections:
            kwargs: dict[str, Any] = {}
            try:
                for config in self.COMPONENT_CONFIG:
                    value = self._process_section_data(section, config)
                    kwargs[config.kwarg_name] = value

                # Initialize list fields to prevent None values in component construction
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

                if kwargs.get("general") is None and handler_name not in {
                    "PropertiesHandler",
                    "CommentHandler",
                }:
                    continue

                component_to_add = self.COMPONENT_CLS(**kwargs)
                if hasattr(component_to_add, "register"):
                    component_to_add.register(model)
                else:
                    logger.warning(
                        "Component from %s does not have a register method.",
                        handler_name,
                    )

            except (ValueError, TypeError, KeyError) as e:
                msg = f"Failed to process component in handler {handler_name}: {e}"
                logger.exception(msg)
                logger.debug("Component data that caused failure: %s", kwargs)
                raise type(e)(msg) from e

    def handle_batch(self, model: NetworkModel, raw: str) -> None:
        """Optimized batch processing for multiple components of the same type.

        Provides performance optimization for files with many components
        by processing sections in batches and continuing on individual failures.

        Args:
            model: Target network for component registration.
            raw: File content containing component sections.

        Raises:
            NotImplementedError: If subclass doesn't define COMPONENT_CLS.

        """
        handler_name = type(self).__name__
        if not self.COMPONENT_CLS:
            msg = f"Subclass '{handler_name}' must define COMPONENT_CLS"
            raise NotImplementedError(msg)

        # Batch parse all sections for improved performance
        sections = list(self.parse_sections(raw))
        if not sections:
            return

        # Filter and prepare valid sections for component creation
        valid_sections = []
        for section in sections:
            kwargs: dict[str, Any] = {}
            try:
                for config in self.COMPONENT_CONFIG:
                    kwargs[config.kwarg_name] = self._process_section_data(section, config)

                if kwargs.get("general") is None and handler_name not in {
                    "PropertiesHandler",
                    "CommentHandler",
                }:
                    continue

                valid_sections.append(kwargs)

            except (ValueError, TypeError, KeyError) as e:
                msg = f"Failed to process component in handler {handler_name}: {e}"
                logger.exception(msg)
                logger.debug("Component data that caused failure: %s", kwargs)
                # Continue with remaining sections on individual failures
                continue

        # Create and register components from validated sections
        for kwargs in valid_sections:
            try:
                component_to_add = self.COMPONENT_CLS(**kwargs)
                if hasattr(component_to_add, "register"):
                    component_to_add.register(model)
                else:
                    logger.warning(
                        "Component from %s does not have a register method.",
                        handler_name,
                    )
            except (TypeError, ValueError, AttributeError):
                # Continue processing remaining components on individual creation failures
                logger.exception("Failed to create component in %s", handler_name)
                continue
