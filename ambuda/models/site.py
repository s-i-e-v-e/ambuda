"""Various site content unrelated to texts and proofing.

The idea is that a trusted user can edit site content by creating and modifyng
these objects. By doing so, they can update the site without waiting for a site
deploy.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy import Text as Text_

from ambuda.models.base import Base, pk





class ContributorInfo(Base):

    """Information about an Ambuda contributor.

    For now, we use this for just proofreaders. Long-term, we might include
    other types of contributors here as well.
    """

    __tablename__ = "contributor_info"

    #: Primary key.
    id = pk()
    #: The contributor's name.
    name = Column(String, nullable=False)
    #: The contributor's title, role, occupation, etc.
    title = Column(String, nullable=False, default="")
    #: A short description of this proofer.
    description = Column(Text_, nullable=False, default="")
