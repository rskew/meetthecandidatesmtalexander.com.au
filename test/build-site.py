import csv
import os
import tomllib

import click
import chevron


NO_ANSWER = "(not answered)"
COMMENT_TYPE = "comment"
YES_NO_OTHER_TYPE = "yes_no_other"

def munge(data, row_dicts):
    candidates = {}
    for name, candidate in data["candidates"].items():
        answers_row = {}
        for row in row_dicts:
            if row[data["name"]] == name:
                answers_row = row
                break
        if "statement" in candidate:
            about = candidate["statement"]
        elif "didnt_respond" in candidate:
            about = "This candidate did not respond to the questionnaire"
        else:
            about = answers_row[data["about"]]
        name = fix_typos(name)
        munged_candidate = {
            "name": name,
            "ward": candidate["ward"],
            "ward_kebab": kebabify(candidate["ward"]),
            "uncontested": "uncontested" if candidate["uncontested"] else "",
            "about": paragraphify(about),
            "picture": candidate["photo"],
            "organisations": [
                {**org,
                 "blurb": paragraphify(org["blurb"]),
                 "questions": [render_question(question, answers_row)
                               for question in org["questions"]]}
                for org in data["organisations"]
            ] if "didnt_response" not in candidate else [],
        }
        if "statement" not in candidate and "didnt_respond" not in candidate:
            munged_candidate["has_answers"] = True
        candidates[name] = munged_candidate
    return candidates

def render_question(question, row):
    if question["answer_type"] == COMMENT_TYPE:
        rendered = {**question, "answer": row.get(question["text"]) or NO_ANSWER}
    elif question["answer_type"] == YES_NO_OTHER_TYPE:
        yes_no_other = row.get(question["text"], "")
        yes_no_other = f"<b>{yes_no_other}</b>" if yes_no_other in ["Yes", "No"] else paragraphify(yes_no_other)
        rendered = {**question,
                    "yes_no_other": yes_no_other,
                    "answer": row.get(question["comment_question"]) or (NO_ANSWER if yes_no_other == "" else "")}
        rendered["answer"] = fix_typos(rendered["answer"])
        rendered["answer"] = paragraphify(rendered["answer"])
    else:
        raise ValueError(f"Blarrgh! {question}")
    rendered["text"] = paragraphify(rendered["text"])
    return rendered

def kebabify(text):
    return "-".join(text.lower().split())

def paragraphify(text):
    return "".join([f"<p>{line}</p>" for line in text.split("\n")])

def fix_typos(text):
    text = text.replace("I 'm", "I'm")
    text = text.replace("Bill maltby", "Bill Maltby")
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
    for ward_name, candidates in data["contested_wards"].items():
        ward_data = {"ward_name": ward_name,
                     "candidates": [{"candidate_name": fix_typos(candidate_name),
                                     "candidate_name_kebab": kebabify(candidate_name),
                                     "picture": data["candidates"][candidate_name]["photo"]}
                                    for candidate_name in candidates]}
        rendered_output = chevron.render(ward_template, ward_data)
        name_kebab = "-".join(ward_name.lower().split())
        output_path = os.path.join(ward_output_dir, f"{name_kebab}.html")
        print(f"Writing {output_path}")
        open(output_path, "w").write(rendered_output)

    # Render candidate pages
    row_dicts = [row for row in csv.DictReader(open(csv_file))]
    candidate_template = open(candidate_template_file).read()
    candidates = munge(data, row_dicts)
    for name, candidate in candidates.items():
        rendered_output = chevron.render(candidate_template, candidate)
        name_kebab = "-".join(name.lower().split())
        output_path = os.path.join(candidate_output_dir, f"{name_kebab}.html")
        print(f"Writing {output_path}")
        open(output_path, "w").write(rendered_output)

if __name__ == "__main__":
    main()
