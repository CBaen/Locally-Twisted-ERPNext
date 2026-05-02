"""Shared LT CRM pipeline constants."""

PIPELINE_FIELD = "custom_pipeline_stage"
ARCHIVE_STAGE = "Archive"

PIPELINE_OPTIONS = [
    "New Inquiry",
    "Quote Sent/Awaiting Approval",
    "Approved",
    "In Production",
    "Event/Post Event",
    ARCHIVE_STAGE,
]

PIPELINE_COLUMNS = [
    ("New Inquiry", "Blue", "Active"),
    ("Quote Sent/Awaiting Approval", "Cyan", "Active"),
    ("Approved", "Green", "Active"),
    ("In Production", "Orange", "Active"),
    ("Event/Post Event", "Purple", "Active"),
    (ARCHIVE_STAGE, "Gray", "Archived"),
]
