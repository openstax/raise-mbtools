from mbtools import utils
from pathlib import Path


class TagReplacement:
    # search for content tags in xml.
    # check if content is already converted. maybe looking for class="os-raise-content"?
    # if not converted add <div class="os-raise-content" data-content-id="UUID"></div>
    def __init__(self, mbz_path):
        self.mbz_path = Path(mbz_path)
        self.output_html_files = {}

        # get activities from Etree
    def replace_tags(self):
        activities = utils.parse_backup_activities(self.mbz_path, ["lesson","page"])
        for activity in activities:
            self.output_html_files.update(activity.replace_tags())
        self.write_html_files(self.mbz_path)
        print(self.output_html_files)
        return self.output_html_files

    def write_html_files(self, file_path):
        for file_name, file_content in self.output_html_files.items():
            with open(f"{file_path}/{file_name}.html", "w") as file:
                file.write(file_content)



"""obj = TagReplacement(
    "../backup-moodle2-course-12-alg1_ww_(development)-20220321-0946-nu"
)
obj.replace_tags()"""