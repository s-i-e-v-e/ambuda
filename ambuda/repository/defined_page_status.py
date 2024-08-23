from enum import Enum


class SitePageStatus(str, Enum):
    """
    Defines page statuses.
    """

    #: Needs more work
    R0 = "reviewed-0"
    #: Proofread once.
    R1 = "reviewed-1"
    #: Proofread twice.
    R2 = "reviewed-2"
    #: Not relevant.
    SKIP = "skip"
