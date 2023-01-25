import os
from pathlib import Path
from mbtools import inject_ib_ids


def test_inject_ib_ids_input_and_cta(
    tmp_path, mocker, autogenerated_user_uuid
):
    page_1_html = """
<div class="os-raise-ib-cta" data-button-text="ButtonText"
data-fire-event="eventnameX" data-schema-version="1.0">
  <div class="os-raise-ib-cta-content">
    Here is a content that's worth seeing for the CTA button
  </div>
  <div class="os-raise-ib-cta-prompt">
    Here is a prompt for a CTA button
  </div>
</div>
<p>Here is some intermediary text</p>
<div class="os-raise-ib-content" data-wait-for-event="eventnameX"
data-schema-version="1.0">
  Here is some conditional content that waits on the CTA button.
</div>
<div class="os-raise-ib-input" data-button-text="Submit"
data-schema-version="1.0">
  <div class="os-raise-ib-input-content">
    This is the question for an IB input block (5+6)
  </div>
  <div class="os-raise-ib-input-prompt">
    Here is the prompt for the submission of the IB Input Block
  </div>
  <div class="os-raise-ib-input-ack">
    This is the ack for the input block - Answer was 12
  </div>
</div>
""".strip()

    page_2_html = """
<h1>This is the second page</h1>
<div class="os-raise-ib-pset" data-fire-success-event="eventnameX"
data-fire-learning-opportunity-event="eventnameY" data-retry-limit="3"
data-button-text="Check" data-schema-version="1.0">
  <div class="os-raise-ib-pset-problem" data-problem-type="input"
  data-solution="42" data-problem-comparator="integer">
    <div class="os-raise-ib-pset-problem-content">
      <p>Here is content for an input problem</p>
    </div>
  </div>
  <div class="os-raise-ib-pset-problem" data-problem-type="dropdown"
  data-solution="red" data-solution-options='["red", "blue", "green"]'>
    <div class="os-raise-ib-pset-problem-content">
      <p>Here is content for a dropdown problem</p>
    </div>
  </div>
  <div class="os-raise-ib-pset-problem" data-problem-type="multiplechoice"
  data-solution="red" data-solution-options='["red", "blue", "green"]'>
    <div class="os-raise-ib-pset-problem-content">
      <p>Here is content for a multiple choice problem</p>
    </div>
  </div>
  <div class="os-raise-ib-pset-problem" data-problem-type="multiselect"
  data-solution='["red", "blue"]'
  data-solution-options='["red", "blue", "green"]'>
    <div class="os-raise-ib-pset-problem-content">
      <p>Here is content for a multiselect problem</p>
    </div>
  </div>
  <div class="os-raise-ib-pset-correct-response">
    <p>If you got an answer right you'll see this response</p>
  </div>
  <div class="os-raise-ib-pset-encourage-response">
    <p>If you got an answer wrong you'll see this prompt</p>
  </div>
</div>
""".strip()

    os.mkdir(tmp_path / "html")
    html_dir = f"{tmp_path}/html"
    fp1 = Path(html_dir) / "page_1.html"
    fp2 = Path(html_dir) / "page_2.html"
    fp1.write_text(page_1_html)
    fp2.write_text(page_2_html)

    mocker.patch(
        "mbtools.models.uuid4",
        lambda: autogenerated_user_uuid
    )

    mocker.patch(
        "sys.argv",
        ["", html_dir]
    )

    inject_ib_ids.main()

    with open(fp1, 'r') as f:
        assert(f.read().count("data-content-id") == 1)

    with open(fp2, 'r') as f:
        assert(f.read().count("data-content-id") == 5)


def test_inject_ib_ids_variant(tmp_path, mocker, autogenerated_user_uuid):
    page_1_html = """
<div class="os-raise-ib-input" data-button-text="Submit"
data-schema-version="1.0">
  <div class="os-raise-ib-input-content">
    This is the question for an IB input block (5+6)
  </div>
  <div class="os-raise-ib-input-prompt">
    Here is the prompt for the submission of the IB Input Block
  </div>
  <div class="os-raise-ib-input-ack">
    This is the ack for the input block - Answer was 12
  </div>
</div>
""".strip()

    page_1_variant = """
<div class="os-raise-ib-input" data-button-text="Submit"
data-schema-version="1.0">
  <div class="os-raise-ib-input-content">
    This is the VARIANT question for an IB input block (5+6)
  </div>
  <div class="os-raise-ib-input-prompt">
    Here is the prompt for the submission of the IB Input Block
  </div>
  <div class="os-raise-ib-input-ack">
    This is the ack for the input block - Answer was 12
  </div>
</div>
""".strip()

    html_dir = f"{tmp_path}/html"
    os.mkdir(html_dir)
    os.mkdir(html_dir + "/page_1")
    fp1 = Path(html_dir) / "page_1.html"
    fp2 = Path(html_dir) / "page_1" / "page_1.html"
    fp1.write_text(page_1_html)
    fp2.write_text(page_1_variant)

    mocker.patch(
        "mbtools.models.uuid4",
        lambda: autogenerated_user_uuid
    )

    mocker.patch(
        "sys.argv",
        ["", html_dir]
    )

    inject_ib_ids.main()

    with open(fp1, 'r') as f:
        assert(f.read().count("data-content-id") == 1)

    with open(fp2, 'r') as f:
        assert(f.read().count("data-content-id") == 1)
