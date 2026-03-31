"""Validate branch corner coordinates with grid-aware tolerance.

The validator compares coordinates after rounding to the 20-pixel grid.
Small differences that round to the same grid point pass validation.
Only mismatches that persist after rounding are flagged.

IMPORTANT: A small raw difference can still cause a mismatch if values
straddle a grid boundary. Example: 109 rounds to 100, 111 rounds to 120.
Raw difference is only 2 pixels, but grid difference is 20 pixels.
"""

from pyptp import NetworkLV, configure_logging
from pyptp.elements.lv.link import LinkLV
from pyptp.elements.lv.node import NodeLV
from pyptp.elements.lv.presentations import BranchPresentation, NodePresentation
from pyptp.elements.lv.sheet import SheetLV
from pyptp.ptp_log import logger
from pyptp.validator import CheckRunner, Severity

configure_logging(level="INFO")

network = NetworkLV()

sheet = SheetLV(SheetLV.General(name="Validation Demo"))
sheet.register(network)
sheet_guid = sheet.general.guid

# Example 1: Exact match (passes)
node1 = NodeLV(
    NodeLV.General(name="A"),
    presentations=[NodePresentation(sheet=sheet_guid, x=100, y=100)],
)
node1.register(network)

node2 = NodeLV(
    NodeLV.General(name="B"),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=100)],
)
node2.register(network)

link1 = LinkLV(
    LinkLV.General(node1=node1.general.guid, node2=node2.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[(100, 100)],
            second_corners=[(300, 100)],
        )
    ],
)
link1.register(network)

# Example 2: Small offset within same grid cell (passes)
# Corner (108, 195) and node (100, 200) both round to (100, 200)
node3 = NodeLV(
    NodeLV.General(name="C"),
    presentations=[NodePresentation(sheet=sheet_guid, x=100, y=200)],
)
node3.register(network)

node4 = NodeLV(
    NodeLV.General(name="D"),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=200)],
)
node4.register(network)

link2 = LinkLV(
    LinkLV.General(node1=node3.general.guid, node2=node4.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[(108, 195)],
            second_corners=[(292, 205)],
        )
    ],
)
link2.register(network)

# Example 3: Large offset causes mismatch (fails)
# Corner (130, 300) rounds to (140, 300), node (100, 300) rounds to (100, 300)
node5 = NodeLV(
    NodeLV.General(name="E"),
    presentations=[NodePresentation(sheet=sheet_guid, x=100, y=300)],
)
node5.register(network)

node6 = NodeLV(
    NodeLV.General(name="F"),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=300)],
)
node6.register(network)

link3 = LinkLV(
    LinkLV.General(node1=node5.general.guid, node2=node6.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[(130, 300)],
            second_corners=[(300, 300)],
        )
    ],
)
link3.register(network)

# Example 4: Tiny difference at grid boundary causes mismatch (fails)
# Corner (111, 400) rounds to (120, 400), node (109, 400) rounds to (100, 400)
# Only 2 pixels apart in raw coordinates, but 20 pixels apart on grid!
node7 = NodeLV(
    NodeLV.General(name="G"),
    presentations=[NodePresentation(sheet=sheet_guid, x=109, y=400)],
)
node7.register(network)

node8 = NodeLV(
    NodeLV.General(name="H"),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=400)],
)
node8.register(network)

link4 = LinkLV(
    LinkLV.General(node1=node7.general.guid, node2=node8.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[(111, 400)],
            second_corners=[(300, 400)],
        )
    ],
)
link4.register(network)

# Example 5: Another boundary case with Y coordinate (fails)
# Corner (100, 490) rounds to (100, 480), node (100, 509) rounds to (100, 500)
# Only 19 pixels apart in raw coordinates, but 20 pixels apart on grid!
node9 = NodeLV(
    NodeLV.General(name="I"),
    presentations=[NodePresentation(sheet=sheet_guid, x=100, y=509)],
)
node9.register(network)

node10 = NodeLV(
    NodeLV.General(name="J"),
    presentations=[NodePresentation(sheet=sheet_guid, x=300, y=500)],
)
node10.register(network)

link5 = LinkLV(
    LinkLV.General(node1=node9.general.guid, node2=node10.general.guid),
    presentations=[
        BranchPresentation(
            sheet=sheet_guid,
            first_corners=[(100, 490)],
            second_corners=[(300, 500)],
        )
    ],
)
link5.register(network)

# Run validation
runner = CheckRunner(network)
report = runner.run()

logger.info("Validation complete: %s", report.summary())

for issue in report.issues:
    if issue.severity == Severity.WARNING:
        logger.warning("%s: %s", issue.code, issue.message)

# Expected: 3 warnings (link3, link4, link5)
# link1 and link2 should pass
