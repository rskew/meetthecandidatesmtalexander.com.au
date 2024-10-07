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
            org_sections(org, answers_row)
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
             "blurb": paragraphify(org["blurb"]),
             "questions": [render_question(question, answers_row)
                           for question in org["questions"]],
             "section_index": org_section_indices[org["title"]]}
            for org in data["organisations"]
        ]
        organisations_columns = [{"organisations": organisations[:6]}, {"organisations": organisations[6:]}]
        munged_candidate = {
            "name": fix_typos(candidate["name"]),
            "name_kebab": kebabify(candidate["name"]),
            "ward": candidate["ward"],
            "ward_kebab": kebabify(candidate["ward"]),
            "uncontested": "uncontested" if candidate["uncontested"] else "",
            "about": paragraphify(fix_typos(about)),
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

def org_sections(org, row):
    sections = [{"title": org["title"],
                 "blurb": paragraphify(fix_typos(org["blurb"])) + "<div style='text-align: center; margin-top: 50px; color: black;'><b>Use the < and > buttons to nagivate the question responses</b></div>"}]
    for question in org["questions"]:
        sections.append({"question": {"text": paragraphify(fix_typos(question["text"])),
                                      "answer": render_answer(question, row),
                                      "organisation_title": org["title"]}})
    return sections

def render_answer(question, row):
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
    answer = paragraphify(fix_typos(answer))
    return answer

def render_question(question, row):
    answer = render_answer(question, row)
    rendered = {}
    rendered["text"] = paragraphify(question["text"])
    rendered["answer"] = answer
    return rendered

def kebabify(text):
    return "-".join(text.lower().split())

def paragraphify(text):
    return "".join([f"<p>{line}</p>" for line in text.split("\n")])

def fix_typos(text):
    text = text.replace("I 'm", "I'm")
    text = text.replace("Bill maltby", "Bill Maltby")
    text = text.replace("Ken Price ", "Ken Price")
    text = text.replace("rep[resenting", "representing")
    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")
    text = text.replace("[1]", "\n[1]")
    text = text.replace("[2]", "\n[2]")
    text = text.replace("[3]", "\n[3]")
    text = text.replace("[4]", "\n[4]")
    text = text.replace("[5]", "\n[5]")
    text = text.replace("www.facebook.com/lucasmaddockgreens", "<a href=\"https://www.facebook.com/lucasmaddockgreens\">www.facebook.com/lucasmaddockgreens</a>")
    text = text.replace("if elected, I commit to working with you to continue", "If elected, I commit to working with you to continue")
    text = text.replace("""What are your attitudes to Forest fire management Victoria's flawed policy on planned burning in Victorian forests? 
For more information, check here:
Fire: paying attention to the detail | Friends of the Box-Ironbark Forests
fobif.org.au
and : 
https://theconversation.com/yes-climate-change-is-bringing-bushfires-more-often-but-some-ecosystems-in-australia-are-suffering-the-most-211683""",
                        """What are your attitudes to Forest fire management Victoria's flawed policy on planned burning in Victorian forests? 
For more information, check here:
<li><a href="https://www.fobif.org.au/2024/08/fire-paying-attention-to-the-detail/">Fire: paying attention to the detail | Friends of the Box-Ironbark Forests</a></li>
<li><a href="https://www.fobif.org.au/2024/08/fire-paying-attention-to-the-detail/">fobif.org.au</a></li>
and: 
<li><a href="https://theconversation.com/yes-climate-change-is-bringing-bushfires-more-often-but-some-ecosystems-in-australia-are-suffering-the-most-211683">https://theconversation.com/yes-climate-change-is-bringing-bushfires-more-often-but-some-ecosystems-in-australia-are-suffering-the-most-211683</a></li>""")
    text = text.replace("I also strongly believe that I would represent our ward through strong advocacy, transparency, whilst always maintaining our community values.",
                        "I also strongly believe that I would represent our ward through strong advocacy, transparency, whilst always maintaining our community values.\nYou can follow my campaign at <a href=\"https://www.facebook.com/kellyannforcoliban\" target=\"_blank\" rel=\"noopener noreferrer\">www.facebook.com/kellyannforcoliban</a>")
    return text

@click.command()
@click.argument("data-toml")
@click.argument("csv-file")
@click.argument("map-template-file")
@click.argument("map-output-dir")
@click.argument("candidate-template-file")
@click.argument("candidate-output-dir")
@click.argument("ward-template-file")
@click.argument("ward-output-dir")
def main(data_toml, csv_file, map_template_file, map_output_dir, candidate_template_file, candidate_output_dir, ward_template_file, ward_output_dir):
    data = tomllib.load(open(data_toml, "rb"))
    row_dicts = [row for row in csv.DictReader(open(csv_file))]
    data["candidates"] = munge(data, row_dicts)

    # Render map page
    map_template = open(map_template_file).read()
    wards_iter = iter(data["wards"])
    data["ward_groups"] = [{"wards": wards} for wards in zip(wards_iter, wards_iter)]
    rendered_output = chevron.render(map_template, data)
    output_path = os.path.join(map_output_dir, "index.html")
    print(f"Writing {output_path}")
    open(output_path, "w").write(rendered_output)

    # Render ward pages
    ward_template = open(ward_template_file).read()
    for ward_name in data["contested_wards"]:
        ward_candidates = [candidate for candidate in data["candidates"]
                           if candidate["ward"] == ward_name]
        ward_data = {"ward_name": ward_name,
                     "candidates": ward_candidates}
        rendered_output = chevron.render(ward_template, ward_data)
        name_kebab = kebabify(ward_name)
        output_path = os.path.join(ward_output_dir, f"{name_kebab}.html")
        print(f"Writing {output_path}")
        open(output_path, "w").write(rendered_output)

    # Render candidate pages
    candidate_template = open(candidate_template_file).read()
    for candidate in data["candidates"]:
        rendered_output = chevron.render(candidate_template, candidate)
        output_path = os.path.join(candidate_output_dir, f"{candidate['name_kebab']}.html")
        print(f"Writing {output_path}")
        open(output_path, "w").write(rendered_output)

if __name__ == "__main__":
    main()
