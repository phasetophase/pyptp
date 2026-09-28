"""Move connections from an overloaded cable onto a new cable laid alongside it.

The old cable in the Lindelaan feeds four connections, on both sides of the street. A
heavier cable is laid along the south side and takes over at the corner. The connections
on the south side then move onto the new cable, each at a new joint of its own.
"""

from pyptp import NetworkLV, configure_logging
from pyptp.elements.color_utils import CL_BLUE, CL_RED, DelphiColor
from pyptp.elements.element_utils import SIDE_NODE2
from pyptp.elements.enums import NodePresentationSymbol as Symbol
from pyptp.elements.lv.cable import CableLV
from pyptp.elements.lv.connection import ConnectionLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, ElementPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.helpers.lv import move_connections_to_cable
from pyptp.ptp_log import logger
from pyptp.type_reader import Types

configure_logging(level="INFO")

network = NetworkLV()
types = Types()
sheet = network.add(SheetLV(SheetLV.General(name="Lindelaan"))).general.guid


def add_joint(x: int, y: int, symbol: Symbol = Symbol.CLOSED_TRIANGLE) -> NodeLV:
    """Add a joint on the old cable."""
    presentation = NodePresentation(sheet=sheet, x=x, y=y, symbol=symbol, color=CL_BLUE)
    return network.add(NodeLV(NodeLV.General(), presentations=[presentation]))


def add_cable(name: str, cable_type: str, color: DelphiColor, node1: NodeLV, node2: NodeLV, metres: float) -> CableLV:
    """Add a cable of ``metres`` between two nodes."""
    presentation = BranchPresentation.between(node1, node2, sheet)
    presentation.color = color
    cable = CableLV(
        CableLV.General(node1=node1.general.guid, node2=node2.general.guid, name=name),
        presentations=[presentation],
        cable_part=CableLV.CablePart(length=metres),
    )
    cable.set_cable_type(types, cable_type)
    return network.add(cable)


def add_connection(name: str, joint: NodeLV, x: int, y: int) -> ConnectionLV:
    """Add a connection on a joint, drawn at (x, y)."""
    connection = ConnectionLV(
        ConnectionLV.General(node=joint.general.guid, name=name),
        presentations=[ElementPresentation(sheet=sheet, x=x, y=y)],
        gms=[],
    )
    return network.add(connection)


# The substation
rail = network.add(
    NodeLV(
        NodeLV.General(name="MSR Lindelaan"),
        presentations=[NodePresentation(sheet=sheet, x=200, y=400, symbol=Symbol.VERTICAL_LINE, size=6)],
    )
)

# The old cable runs along the north side of the street, with a joint for every connection
joint_1 = add_joint(400, 360)
joint_2 = add_joint(520, 360)
joint_3 = add_joint(640, 360)
joint_4 = add_joint(760, 360)
corner = add_joint(880, 360, Symbol.CLOSED_CIRCLE)

old_type = "4* 50 VMvK/Alk"
add_cable("Lindelaan", old_type, CL_BLUE, rail, joint_1, 10)
add_cable("Lindelaan", old_type, CL_BLUE, joint_1, joint_2, 6)
add_cable("Lindelaan", old_type, CL_BLUE, joint_2, joint_3, 6)
add_cable("Lindelaan", old_type, CL_BLUE, joint_3, joint_4, 6)
last_old_section = add_cable("Lindelaan", old_type, CL_BLUE, joint_4, corner, 6)

# Odd numbers on the north side, even numbers across the street on the south side
lindelaan_1 = add_connection("Lindelaan 1", joint_1, 400, 240)
lindelaan_2 = add_connection("Lindelaan 2", joint_2, 520, 560)
lindelaan_3 = add_connection("Lindelaan 3", joint_3, 640, 240)
lindelaan_4 = add_connection("Lindelaan 4", joint_4, 760, 560)

# The old cable is overloaded. A heavier cable is laid along the south side, from the
# substation to the corner, and the old cable is opened at the corner.
new_cable = CableLV(
    CableLV.General(node1=rail.general.guid, node2=corner.general.guid, name="Lindelaan nieuw"),
    presentations=[BranchPresentation.between(rail, corner, sheet, via=[(880, 440)])],
    cable_part=CableLV.CablePart(length=38),
)
new_cable.presentations[0].color = CL_RED
new_cable.set_cable_type(types, "4*150 VVMvKsas/Alk")
network.add(new_cable)

last_old_section.general.set_switches(SIDE_NODE2, closed=False)

# Lindelaan 2 and 4 are on the side of the new cable, so they move onto it
result = move_connections_to_cable(network, new_cable, [lindelaan_2, lindelaan_4])

# one section per stretch between joints
for section in result.sections:
    logger.info("Section of the new cable: %.1f m", section.cable_part.length)

network.save("lv_parallel_cable.gnf")
logger.info("Saved lv_parallel_cable.gnf")
