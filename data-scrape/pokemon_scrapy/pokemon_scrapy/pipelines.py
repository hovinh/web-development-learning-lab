# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class DropIncompletePokemonPipeline:
    """Drop any item missing a field the rest of this stage relies on.

    This is the "pipeline" half of "a spider + a pipeline": the spider's
    only job is to yield an item per page it parses, and this pipeline
    is a separate place - decoupled from the parsing code - to enforce
    "is this item actually usable" before it reaches FEEDS export or
    ImagesPipeline. Raising DropItem here stops the item at this stage;
    it never reaches the pipelines configured after this one in
    ITEM_PIPELINES (see settings.py).
    """

    REQUIRED_FIELDS = ("name", "national_number", "species", "image_urls")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        missing = [field for field in self.REQUIRED_FIELDS if not adapter.get(field)]
        if missing:
            raise DropItem(
                f"Dropping {adapter.get('name', '<unknown>')!r}: "
                f"missing required field(s) {missing}"
            )
        return item
