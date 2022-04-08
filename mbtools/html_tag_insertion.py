from mbtools import utils
from hashlib import sha256
from lxml import etree
from pathlib import Path

class TagReplacement:
    # search for content tags in xml.
    # check if content is already converted. maybe looking for class="os-raise-content"?
    # if not converted add <div class="os-raise-content" data-content-id="UUID"></div>
    # UUID is sha256 of html.
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.activities = utils.parse_backup_activities(mbz_path)
        print(self.activities[0].activity_filename)
        print(self.activities[0].activity_filename)


        # get activities from Etree
    def find_content_tags(self):
        for activity in self.activities:
            for element in activity.etree.iter():
                if element.find("content") is not None:
                    for children in element.getchildren():
                        print(children.text)
                        print("----------------------------------------------")


    def replace_tags(self):
        pass



obj = TagReplacement(
    "../backup-moodle2-course-12-alg1_ww_(development)-20220321-0946-nu"
)
obj.find_content_tags()