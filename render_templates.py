import csv
import os
import tomllib

import click
import chevron


NO_ANSWER = "<i>(not answered)</i>"
COMMENT_TYPE = "comment"
YES_NO_OTHER_TYPE = "yes_no_other"

def munge(data, row_dicts):
    candidates = []
    for candidate in data["candidates"]:
        answers_row = {}
        for row in row_dicts:
            if row[data["name"]] == candidate["name"]:
                answers_row = row
                break
        if "statement" in candidate:
            about = candidate["statement"]
        elif "didnt_respond" in candidate:
            about = "This candidate did not respond to the questionnaire."
        else:
            about = answers_row[data["about"]]
        sections_nested = [
            org_sections(org, answers_row, data["text_replacements"])
            for org in data["organisations"]
        ]

        sections = []
        section_index = 0
        org_section_indices = {}
        for inner_sections in sections_nested:
            org_section_indices[inner_sections[0]["title"]] = section_index
            for section in inner_sections:
                section["section_index"] = section_index
                sections.append(section)
                section_index = section_index + 1

        organisations = [
            {**org,
             "section_index": org_section_indices[org["title"]],
             "blurb": paragraphify(apply_replacements(org["blurb"], data["text_replacements"]))}
            for org in data["organisations"]
        ]
        organisations_columns = [{"organisations": organisations[:6]}, {"organisations": organisations[6:]}]
        munged_candidate = {
            "name": apply_replacements(candidate["name"], data["text_replacements"]),
            "name_kebab": kebabify(candidate["name"]),
            "ward": candidate["ward"],
            "ward_kebab": kebabify(candidate["ward"]),
            "uncontested": "uncontested" if candidate["uncontested"] else "",
            "about": paragraphify(apply_replacements(about, data["text_replacements"])),
            "picture": candidate["picture"],
            "sections": sections,
            "organisations_columns": organisations_columns,
            "organisations": organisations if "didnt_response" not in candidate else [],
        }
        if not candidate["uncontested"]:
            munged_candidate["back_to_ward_link"] = f"../wards/{kebabify(candidate['ward'])}.html"
        if "statement" not in candidate and "didnt_respond" not in candidate:
            munged_candidate["has_answers"] = True
        candidates.append(munged_candidate)
    return candidates

def org_sections(org, row, text_replacements):
    sections = [{"title": org["title"],
                 "blurb": paragraphify(apply_replacements(org["blurb"], text_replacements)) + "<div style='text-align: center; margin-top: 50px; color: black;'><b>Use the < and > buttons to nagivate the question responses</b></div>"}]
    for question in org["questions"]:
        sections.append({"question": {"text": paragraphify(apply_replacements(question["text"], text_replacements)),
                                      "answer": render_answer(question, row, text_replacements),
                                      "organisation_title": org["title"]}})
    return sections

def render_answer(question, row, text_replacements):
    if question["answer_type"] == COMMENT_TYPE:
        answer = row.get(question["text"]) or NO_ANSWER
    elif question["answer_type"] == YES_NO_OTHER_TYPE:
        yes_no_other = row.get(question["text"], "")
        if yes_no_other in ["Yes", "No"]:
            yes_no_other = f"<p><b>{yes_no_other}</b></p>"
        elif yes_no_other == "Refer below":
            yes_no_other = ""
        answer = row.get(question["comment_question"]) or (NO_ANSWER if yes_no_other == "" else "")
        answer = yes_no_other + "\n" + answer
    else:
        raise ValueError(f"Blarrgh! {question}")
    answer = paragraphify(apply_replacements(answer, text_replacements))
    return answer

def render_question(question, row, text_replacements):
    answer = render_answer(question, row, text_replacements)
    rendered = {}
    rendered["text"] = paragraphify(question["text"])
    rendered["answer"] = answer
    return rendered

def kebabify(text):
    return "-".join(text.lower().split())

def paragraphify(text):
    return "".join([f"<p>{line}</p>" for line in text.split("\n")])

def apply_replacements(text, text_replacements):
    for replacement in text_replacements:
        text = text.replace(replacement["old"], replacement["new"])
    return text

@click.command()
@click.argument("data-toml")
@click.argument("csv-file")
@click.argument("map-template-file")
@click.argument("media-template-file")
@click.argument("base-output-dir")
@click.argument("candidate-template-file")
@click.argument("candidate-output-dir")
@click.argument("ward-template-file")
@click.argument("ward-output-dir")
def main(data_toml, csv_file, map_template_file, media_template_file, base_output_dir, candidate_template_file, candidate_output_dir, ward_template_file, ward_output_dir):
    data = tomllib.load(open(data_toml, "rb"))
    row_dicts = [row for row in csv.DictReader(open(csv_file))]
    data["candidates"] = munge(data, row_dicts)
    for organisation in data["organisations"]:
        organisation["blurb"] = paragraphify(apply_replacements(organisation["blurb"], data["text_replacements"]))

    # Render map page
    map_template = open(map_template_file).read()
    wards_iter = iter(data["wards"])
    data["ward_groups"] = [{"wards": wards} for wards in zip(wards_iter, wards_iter)]
    rendered_output = chevron.render(map_template, data)
    map_output_path = os.path.join(base_output_dir, "index.html")
    print(f"Writing {map_output_path}")
    open(map_output_path, "w").write(rendered_output)

    # Render media page
    media_template = open(media_template_file).read()
    rendered_output = chevron.render(media_template, data["candidates"][0])
    media_output_path = os.path.join(base_output_dir, "media.html")
    print(f"Writing {media_output_path}")
    open(media_output_path, "w").write(rendered_output)

    # Render ward pages
    ward_template = open(ward_template_file).read()
    for ward_name in data["contested_wards"]:
        ward_candidates = [candidate for candidate in data["candidates"]
                           if candidate["ward"] == ward_name]
        ward_data = {"ward_name": ward_name,
                     "candidates": ward_candidates}
        rendered_output = chevron.render(ward_template, ward_data)
        name_kebab = kebabify(ward_name)
        ward_output_path = os.path.join(ward_output_dir, f"{name_kebab}.html")
        print(f"Writing {ward_output_path}")
        open(ward_output_path, "w").write(rendered_output)

    # Render candidate pages
    candidate_template = open(candidate_template_file).read()
    for candidate in data["candidates"]:
        rendered_output = chevron.render(candidate_template, candidate)
        candidate_output_path = os.path.join(candidate_output_dir, f"{candidate['name_kebab']}.html")
        print(f"Writing {candidate_output_path}")
        open(candidate_output_path, "w").write(rendered_output)

if __name__ == "__main__":
    main()
