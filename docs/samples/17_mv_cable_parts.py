"""Build an MV cable out of parts, each with its own length and cable type.

``add_part()`` looks the cable type up in the type library and adds the part.
"""

from pyptp import NetworkMV, configure_logging
from pyptp.elements.enums import NodePresentationSymbol as Symbol
from pyptp.elements.mv.cable import CableMV
from pyptp.elements.mv.node import NodeMV
from pyptp.elements.mv.presentations import BranchPresentation, ElementPresentation, NodePresentation
from pyptp.elements.mv.sheet import SheetMV
from pyptp.elements.mv.source import SourceMV
from pyptp.ptp_log import logger
from pyptp.type_reader import Types

configure_logging(level="INFO")

network = NetworkMV()
types = Types()
sheet = network.add(SheetMV(SheetMV.General(name="Kerkplein - Molenweg"))).general.guid


def add_rail(name: str, x: int, y: int) -> NodeMV:
    """Add a 10 kV substation rail."""
    presentation = NodePresentation(sheet=sheet, x=x, y=y, symbol=Symbol.VERTICAL_LINE, size=4)
    return network.add(NodeMV(NodeMV.General(name=name, unom=10.0), presentations=[presentation]))


kerkplein = add_rail("MSR Kerkplein", 300, 500)
molenweg = add_rail("MSR Molenweg", 1100, 500)

network.add(
    SourceMV(
        SourceMV.General(node=kerkplein.general.guid, name="Voeding", sk2nom=500.0),
        presentations=[ElementPresentation(sheet=sheet, x=200, y=350)],
    )
)

cable = CableMV(
    CableMV.General(name="Kerkplein - Molenweg", node1=kerkplein.general.guid, node2=molenweg.general.guid),
    presentations=[BranchPresentation.between(kerkplein, molenweg, sheet)],
)

# The original aluminium run, with the stretch under the Molenweg renewed in copper XLPE
cable.add_part(types, "3*150 AL Kudi 6/10", length=340)
cable.add_part(types, "3*150 CU XLPE   6/10", length=120)
network.add(cable)

for part in cable.cable_parts:
    logger.info("%s m of %s", part.length, part.cable_type)

network.save("mv_cable_parts.vnf")
logger.info("Saved mv_cable_parts.vnf")
