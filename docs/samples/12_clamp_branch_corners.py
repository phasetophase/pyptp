"""Clamp branch corners to node connection points.

Use NodePresentation.clamp_point() to snap imprecise coordinates to valid
connection points. This is useful when importing data with slightly off
coordinates or programmatically generating layouts.
"""

from pyptp import NetworkLV, configure_logging
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.ptp_log import logger

configure_logging(level="INFO")

network = NetworkLV()

sheet = SheetLV(SheetLV.General(name="Clamp Example"))
sheet.register(network)
sheet_guid = sheet.general.guid

# Two nodes we want to connect
substation = NodeLV(
    NodeLV.General(name="Substation"),
    presentations=[NodePresentation(sheet=sheet_guid, x=100, y=100)],
)
substation.register(network)

load = NodeLV(
    NodeLV.General(name="Load"),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=100)],
)
load.register(network)

# Imagine these coordinates came from an external source with slight errors
# They should connect at (100, 100) and (300, 100) but are a few pixels off
imported_first_corners = [(105, 98), (200, 100)]
imported_second_corners = [(295, 102)]

# Clamp the first point of each corner list to the node's connection point
substation_pres = substation.presentations[0]
load_pres = load.presentations[0]

first_corners = [
    substation_pres.clamp_point(imported_first_corners[0]),
    *imported_first_corners,
]
second_corners = [
    load_pres.clamp_point(imported_second_corners[0]),
    *imported_second_corners,
]

feeder = LinkLV(
    LinkLV.General(name="Feeder", node1=substation.general.guid, node2=load.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=first_corners,
            second_corners=second_corners,
        )
    ],
)
feeder.register(network)

network.save("clamp_corners_example.gnf")
logger.info("Saved clamp_corners_example.gnf")
