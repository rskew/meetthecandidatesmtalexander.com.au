import csv
import os

import click
import chevron


NO_ANSWER = "(not answered)"
COMMENT_TYPE = "comment"
YES_NO_OTHER_TYPE = "yes_no_other"

NAME_TO_PHOTO = {
    "Rosie Annear": "439336115_852369146929945_141540076818859956_n.jpg",
    "Bill maltby": "maltby_150x150.jpg",
    "Gavan Thomson": "Gavan Thomson jmp_240601_3522 RT .jpg",
    "Lucas Maddock": "451655473_122113545692372569_6059698426683280347_n.jpg",
    "Kerrie Allen": "Kerrie Allen_JPG_002.jpg",
    "Phillip Walker": "_ Walker, Phillip_3.jpeg",
    "Ken Price ": "Screenshot 2024-09-27 192503.png",
    "Rosalie Hastwell": "Screen Shot 2024-09-30 at 7.05.39 PM.png",
    "Kelly Ann Blake": "458351864_1181427559784219_6166558062636311547_n.jpg",
    "Tony Cordy": "Councillor_T_Cordy.jpg",
    "Toby Heydon": "Screen Shot 2024-09-30 at 7.06.08 PM.png",
    "Matt Driscoll": "mattd.jpg",
    "Max Lesser": "max01.jpg",
}

CONTESTED_WARDS = {
    "Calder": [
        "Kerrie Allen",
        "Tony Cordy",
        "Ken Price ",
    ],
    "Campbells Creek": [
        "Bill maltby",
        "Gavan Thomson",
    ],
    "Coliban": [
        "Kelly Ann Blake",
        "Phillip Walker",
        "Max Lesser",
    ],
}

COMMONS = {
    "title": "Castlemaine Commons",
    "blurb": """Formed during the early stages of COVID-19, the Castlemaine Commons collective works responsively and locally hosting events & discussions -  fostering new ways of communication, community connection, sense making, catalysing action and creating collective future visions. 

We are also part of the newly formed First Nations Solidarity Network - Liyanganyuk Banyul. As non-Indigenous community members we understand it is our responsibility to walk together in right relationship with a commitment to truth telling. We know that when First Peoples are supported to thrive, we all thrive.""",
    "questions": [
        {"text": "Since the referendum we have seen an increase in racism in schools and across our community. How will you address this division and ensure there is accountability and transparency about the learning and truth telling that is needed? ",
         "answer_type": COMMENT_TYPE},
        {"text": "To inform your leadership decisions, will you personally commit to ongoing learning about anti-racism, truth telling and colonisation? ",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about personally committing to ongoing learning about anti-racism, truth telling and colonisation here:"},
        {"text": "Would you support offering and increasing professional development for all Council staff in cultural awareness and anti-racism, and making this a requirement of both Councillors and the Executive team within Council? ",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about offering and increasing professional development for all Council staff in cultural awareness and anti-racism here:"},
        {"text": """Djaara (Dja Dja Wurrung Clans Aboriginal Corporation) and Nalderun Education Aboriginal Organisation provide an important contribution to this community. Will you commit to strengthening the collaborative relationships and support that has been built between MASC and these organisations as well as with other local First Nations led enterprises and organisations? 
This may be through increasing funding from MASC for programs run by Nalderun Education Aboriginal Organisation, such as the Me-Mandook Bush Tucker Education Place, increasing advocacy and in-kind support, increased partnerships and meaningful relationship building.""",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about strengthening the collaborative relationships and support that has been built between MASC and First Nations organisations/enterprises here:"},
        {"text": """As you are settling into your Council role later this year, the Victorian Treaty process will be entering into an important stage of Statewide Treaty negotiations, with local Traditional Owner Treaties commencing soon after. 
What role do you envision MASC playing in the Treaty process, and how can you support local Treaty negotiations in partnership with local Traditional Owners, Elders and First Nations Leaders? 
Preparing MASC for local Traditional Owner Treaty negotiations may include, for example, development of a discussion paper on how Council can engage with the Treaty Negotiation Framework.""",
         "answer_type": COMMENT_TYPE},
        {"text": "Will you write to the First Peoples’ Assembly of Victoria and the Treaty Authority, the independent body that oversees Treaty-making in Victoria, to express the Shire’s desire to be party to future Traditional Owner Treaties?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about writing to the First Peoples’ Assembly of Victoria and the Treaty Authority, the independent body that oversees Treaty-making in Victoria, to express the Shire’s desire to be party to future Traditional Owner Treaties here:"},
        #"Please provide any additional comments about supporting learning and truth telling in Mount Alexa"
    ],
}


COMMUNITY_HOUSE = {
    "title": "Castlemaine Community House",
    "blurb": """<p><a href="https://cch.org.au/">Castlemaine Community House</a> (CCH) provides programs and activities contributing to community development and supporting individuals and groups within the local community.</p>
<p>CCH is:</p>
<ul>
<li>a learning centre</li>
<li>a meeting place</li>
<li>a not-for-profit enterprise</li>
<li>a drop-in centre</li>
<li>a supportive, welcoming place</li>
<li>an information network</li></ul>""",
    "questions": [
        {"text": "How will you maintain strong connections and ensure you keep in touch with your constituents?",
         "answer_type": COMMENT_TYPE},
        {"text": "How effective are you at collaborating with people who may have different perspectives and values?",
         "answer_type": COMMENT_TYPE},
        {"text": "In your view, what contributes to a resilient community, and how can the council support that?",
         "answer_type": COMMENT_TYPE},
    ],
}

PRIDE = {
    "title": "Castlemaine Pride",
    "blurb": "<a href=\"https://castlemainepride.org.au/\">Castlemaine Pride</a> is a volunteer-led community group that organises the Pride Festival each year. The community grew out of the local grassroots movement in support of marriage equality. They continue to support and connect the local LGBTQIA+ community and advocate for the safety and inclusion of LGBTQIA+ people in the Mount Alexander Shire.",
    "questions": [
        {"text": """Things should be getting better for LGBTQIA+ young people but, alarmingly, in 2024 discrimination and hate speech is on the rise. 66% of LGBTQIA+ youth in Australia still experience discrimination just for being who they are. 

If elected to council, do you commit to engaging with and supporting LGBTQIA+ youth to create a Discrimination Action Plan in our Shire?""",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about creating a Discrimination Action Plan in our Shire here:"},
        {"text": """A key gap in Australia is the lack of population-level information and service data that adequately reflects trans and gender-diverse people. Ideally the whole Shire should be a safe space for our trans and gender diverse community. 

If elected to council, do you commit to ensure trans and gender diverse people receive equal opportunities, have access to safe spaces, and effective healthcare services? """,
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about ensuring trans and gender diverse people receive equal opportunities, have access to safe spaces, and effective healthcare services here:"},
        {"text": """Not one candidate in the Mt Alexander Shire elected in 2020, fully supported the ‘Rainbow Local Government’ pledge. Some candidates did not even take part in the survey. 
Will you vow to take the ‘Rainbow Pledge’ put forth by The Victorian Pride Lobby, and support the priorities of LGBTQIA+ people within our community?

Information about the Pledge and Survey can be found here: https://rainbowvotes.com.au/ """,
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about taking the 'Rainbow Pledge' and supporting the priorities of LGBTQIA+ people in our community here:"},
        #"Are there any further comments you would like to make about your position on supporting LGBTQIA+ Communities in Mount Alexander Shire?",
    ],
}

SAFE_SPACE = {
    "title": "Castlemaine Safe Space",
    "blurb": "<a href\"https://www.castlemainesafespace.org/\">Castlemaine Safe Space</a> is a non-clinical drop­ in Space for anyone in emotional distress, or experiencing loneliness or suicidal thoughts. We are community designed and led, and staffed by trained peer volunteers with lived experience.",
    "questions": [
        {"text": "Would you support and advocate for future funding to ensure the sustainability of Castlemaine Safe Space, and if so, how would you do this?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about supporting and advocating for future funding to ensure the sustainability of Castlemaine Safe Space here:"},
        {"text": "Would you prioritise emergency housing for people experiencing homelessness? If so, how would you do this?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about prioritising emergency housing for people experiencing homelessness here:"},
    ],
}

SCHOOL_STRIKE = {
    "title": "Castlemaine School Strike 4 Climate",
    "blurb": "School Strike For Climate is a network of school students united by our concern for the future of our planet and all life on it.",
    "questions": [
        {"text": "What role do you think that Council can play in fighting the climate crisis? And what do you think are its limitations?",
         "answer_type": COMMENT_TYPE},
        {"text": "Would you advocate at a State and Federal level to take stronger climate action if you were elected?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about advocating at a State and Federal level to take stronger climate action here:"},
        {"text": """Councils have a long history of influencing state and federal government issues, and they are uniquely placed to advocate on behalf of the communities they represent. 

With this in mind, what is your view on the current Council’s decision in early 2024 to adopt a policy which allows Council to abstain from international, national, and state issues, particularly on issues that impact members of our community?""",
         "answer_type": COMMENT_TYPE},
    ],
}

CLIMATE_ACTION = {
    "title": "Central Victoria Climate Action",
    "blurb": "<a href=\"https://www.facebook.com/centralvictoriaclimateaction\">Central Victoria Climate Action</a> is a grassroots community group made up of climate concerned citizens working together for climate action.",
    "questions": [
        {"text": "Given that MASC declared a climate emergency and the UN peak scientific climate body the IPCC said in March 2023 that there can be no new fossil fuel projects if we are to have even a chance of aligning with Paris, will you support council taking action to change its default super fund for its employees to an ethical fund that has ruled out investing in companies doing new fossil fuel projects?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about council taking action to change its default super fund for its employees to an ethical fund here:"},
        {"text": """What are your attitudes to Forest fire management Victoria's flawed policy on planned burning in Victorian forests? 
For more information, check here:
Fire: paying attention to the detail | Friends of the Box-Ironbark Forests
fobif.org.au
and : 
https://theconversation.com/yes-climate-change-is-bringing-bushfires-more-often-but-some-ecosystems-in-australia-are-suffering-the-most-211683""",
         "answer_type": COMMENT_TYPE},
        {"text": """Mount Alexander Shire Council declared a climate emergency in 2019 with the aim of reaching zero carbon emissions by 2030. 

If you are elected, will you ensure that all of Council's financial transactions and commitments are transparent in regard to climate and First Nations justice, human rights and the environment? If so, how will you do this?""",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about ensuring that all of Council's financial transactions and commitments are transparent in regard to climate and First Nations justice, human rights and the environment here:"},
        #"Are there any further comments you would like to make about your position on Climate and Environment in Mount Alexander Shire?"
    ],
}

FPCV = {
    "title": "Free Palestine Central Victoria",
    "blurb": "<a href=\"https://www.facebook.com/freepalestinecentralvic\">Free Palestine Central Victoria</a> is a Castlemaine-based community organising + action group, in solidarity with Palestine.",
    "questions": [
        #"If I am elected as a local Councillor at the October 2024 Local Government Elections, I pledge to support a Council Resolution denouncing Israel’s Occupation, Apartheid, and Genocidal War on Palestine.",
        {"text": "If elected as a local Councillor at the October 2024 Local Government Elections, do you commit to support a Council Resolution denouncing Israel’s Occupation, Apartheid, and Genocidal War on Palestine?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about supporting a Council Resolution denouncing Israel’s Occupation, Apartheid, and Genocidal War on Palestine here:"},
        {"text": "If elected as a local Councillor at the October 2024 Local Government Elections, do you commit to ensure the Council adopts an active and consistent position on human rights and demonstrates this by formally committing to Cultural Diversity and Inclusion within the first two years?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about Council formally committing to Cultural Diversity and Inclusion within the first two years here:"},
        {"text": "If elected as a local Councillor at the October 2024 Local Government Elections, do you commit to update the Council's procurement and investment policies to avoid and divest from companies that support or profit from internationally recognised human rights abuses, and increase the transparency of Council’s financial transactions and commitments?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about updating the Council's procurement and investment policies here:"},
        #"If I am elected as a local Councillor at the October 2024 Local Government Elections, I pledge to ensure the Council adopts an active and consistent position on human rights and demonstrates this commitment by implementing a Cultural Diversity and Inclusion policy within the first two years."
        #"If I am elected as a local Councillor at the October 2024 Local Government Elections, I pledge to update the Council's procurement and investment policies to avoid and divest from companies that support Apartheid practices or profit from it. Council must take action immediately wherever there is a question about their compliance with human rights and ethical standards."
    ],
}

MASARG = {
    "title": "Mount Alexander Shire Accommodation and Respite Group (MASARG)",
    "blurb": "MASARG is an independent, non political, not for profit charitable organisation working with people with intellectual disabilities and their carers in Castlemaine and surrounds. MASARG built a much needed respite house in Melissa CRT, McKenzies Hill Castlemaine that was opened in 2016. MASARG are now advocating for the right for people with an intellectual disability to have safe, secure and affordable long term housing in Castlemaine.",
    "questions": [
        {"text": "Do you acknowledge that the needs of people with disabilities, and particularly those with intellectual disabilities, are different to others and how will this be considered in decisions about social and affordable housing?",
         "answer_type": COMMENT_TYPE},
        #"Are there any further comments you would like to make about your position on supporting People Living with Disabilities, particularly Intellectual Disabilities,  in Mount Alexander Shire?"
    ],
}


MASDAG = {
    "title": "Mount Alexander Shire Disability Advocacy Group (MASDAG)",
    "blurb": "<a href=\"https://www.mountalexander.vic.gov.au/Community-and-Wellbeing/Community-directory/Mount-Alexander-Shire-Disability-Advocacy-Group-MASDAG\">Mount Alexander Shire Disability Advocacy Group (MASDAG)</a> is an independent volunteer advocate proudly auspiced by Castlemaine Community House. Our aim is to remove barriers and promote systemic change that supports equitable social participation for people with the wide range of disabilities in Mount Alexander Shire, their families and friends.",
    "questions": [
        {"text": """Are you aware of the Mount Alexander Disability and Inclusion Action Plan?  
Would you fully support all aspects of accessibility in the shire as outlined in this plan - removing barriers for employment, the built environment, public spaces including footpaths and toilets, transport, etc.?""",
         "answer_type": COMMENT_TYPE},
    ],
}

MHN = {
    "title": "My Home Network",
    "blurb": """<a href="https://dhelkayahealth.org.au/my-home-network/">My Home Network</a> is a local network made up of local people with lived experience of housing crisis and homelessness, community members with diverse expertise and community and government organisations. The network believes that everyone has a right to safe, affordable, secure, sustainable and appropriate housing that recognises their place in and connections to Community and Country.

Current work includes that of the  Homeshare community, tiny homes on wheels, tenants rights working group, vacant dwellings and advocacy working groups and rough sleeper action group and advocating for a Solar bank to ensure equitable access for all community members to affordable renewable energy.

The My Home Network works closely with Mount Alexander Shire Council across various departments and with the permanent full time housing solutions broker Clare Richards.

We support Council in their work to address the housing crisis -see Let's talk about affordable housing | Shape Mount Alexander which is essentially about bringing diverse social housing to Mount Alexander Shire (we need 600 more social housing units) and setting up a Mount Alexander Charitable  Affordable Housing Trust (MAAHT) .

They are also in the process of employing a Homelessness coordinator who will scope, support and coordinate formal and informal Homelessness supports in the Shire.""",
    "questions": [
        {"text": "If elected, would you join the My Home Network (MHN) and support our work?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about joining and supporting the My Home Network (MHN) here:"},
        {"text": "Would you support the improved integration of housing across different departments within Council?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about supporting the improved integration of housing across different departments within Council here:"},
        {"text": "Would you support MHN’s advocacy to Council to improve the Tiny Homes On Wheels (THOW) local law in having nationally approved onsite waste management systems as an option (currently waste management has to be off site) and allowing a financial exchange between the THOW owner or occupier and land owner?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about improving the Tiny Homes On Wheels (THOW) local law here:"},
        {"text": "Would you support MHN’s advocacy to Council to engage with the Shire’s residents to encourage the release of the over 1000 vacant dwellings (this doesn’t include primary and secondary Air BnBs) in our Shire as affordable rentals or transition housing?",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about engaging with the Shire’s residents to encourage the release of the over 1000 vacant dwellings as affordable rentals or transition housing here:"},
    ],
}

RAR = {
    "title": "Rural Australians for Refugees - Castlemaine",
    "blurb": "Rural Australians for Refugees Castlemaine is a grassroots, volunteer-led community group who are united in supporting a compassionate approach towards refugees and people seeking asylum.",
    "questions": [
#        """In 2014 Mount Alexander Shire made a statement of commitment to being a Refugee Welcome Zone. Council, in conjunction with Rural Australians for Refugees Castlemaine and Loddon Campaspe Multicultural Services, developed an action plan for the years 2018-2021.
#
#Would you support re-stating the commitment declaring Mount Alexander Shire a Refugee Free Zone and advocate for a review of the action plan?""",
        {"text": """In 2014 Mount Alexander Shire made a statement of commitment to being a Refugee Welcome Zone. Council, in conjunction with Rural Australians for Refugees Castlemaine and Loddon Campaspe Multicultural Services, developed an action plan for the years 2018-2021.

Would you support re-stating the commitment declaring Mount Alexander Shire a Refugee Welcome Zone and advocate for a review of the action plan?""",
         "answer_type": YES_NO_OTHER_TYPE,
         "comment_question": "Please provide any comments you have about re-stating the commitment declaring Mount Alexander Shire a Refugee Welcome Zone and advocating for a review of the action plan here:"},
        {"text": "What would you do to welcome refugees and promote inclusiveness and acceptance of cultural diversity in the Shire?",
         "answer_type": COMMENT_TYPE},
        #"Are there any further comments you would like to make about your position on supporting Refugees in Mount Alexander Shire?"
    ],
}

YOUNG_PEOPLE = {
    "title": "Young People of Mount Alexander Shire",
    "link": None,
    "blurb": "Billy Lister - Young Citizen of the Year 2022, representative of Mount Alexander Shire Youth Advisory Group and Castlemaine Secondary College Student representative council canvassed young people in the Mount Alexander Shire to present a series of questions for the candidates in the Mount Alexander Shire local council election.",
    "questions": [
        {"text": "The 2023-2026 Mount Alexander Shire Middle Years Plan was adopted last year, how would you ensure that those recommendations are implemented and delivered efficiently?",
         "answer_type": COMMENT_TYPE},
        {"text": "Young people across the world, country and shire are facing profound challenges when it comes to mental health and wellbeing. Council's Pillar of - a healthy, connected and inclusive community - strongly aligns with this issue. How will you ensure that this Pillar can promote the future and mental health of young people's mental health in the shire? ",
         "answer_type": COMMENT_TYPE},
        {"text": "Council's Pillar of - a resilient and growing local economy - also includes a community that is inclusive and connected (2021-2025 council plan). How will you as a councillor listen to the voices of young people and ensure they are connected to council and their community? ",
         "answer_type": COMMENT_TYPE},
    ],
}

TIMESTAMP = "Timestamp"
EMAIL = "Email Address"
NAME = "What is your full name?"
WARD = "Which Mount Alexander Shire Council Ward are you running for in the 2024 local Council election?"
ABOUT_CANDIDATE = "Please tell us about yourself, what makes you passionate about the Ward you are standing in, and why you chose to stand."
ABOUT = "Please tell us about yourself, what makes you passionate about the Ward you are standing in, and why you chose to stand."

ORGS = [
    COMMONS,
    COMMUNITY_HOUSE,
    PRIDE,
    SAFE_SPACE,
    SCHOOL_STRIKE,
    CLIMATE_ACTION,
    FPCV,
    MASARG,
    MASDAG,
    MHN,
    RAR,
    YOUNG_PEOPLE,
]

def munge(row_dicts):
    rows_out = []
    for row in row_dicts:
        if row[NAME] != "Tina Helm":
            munged_row = {
                "candidate_name": row[NAME],
                "about": row[ABOUT],
                "picture": NAME_TO_PHOTO[row[NAME]],
                "organisations": [
                    {**org,
                     "questions": [render_question(question, row)
                                   for question in org["questions"]]}
                    for org in ORGS
                ],
            }
            rows_out.append(munged_row)
    return rows_out

def render_question(question, row):
    if question["answer_type"] == COMMENT_TYPE:
        return {**question, "answer": row.get(question["text"]) or NO_ANSWER}
    elif question["answer_type"] == YES_NO_OTHER_TYPE:
        yes_no_other = row.get(question["text"], "")
        return {**question,
                "yes_no_other": yes_no_other,
                "answer": row.get(question["comment_question"]) or (NO_ANSWER if yes_no_other == "" else "")}
    else:
        raise ValueError(f"Blarrgh! {question}")

def kebabify(text):
    return "-".join(text.lower().split())

@click.command()
@click.argument("csv-file")
@click.argument("candidate-template-file")
@click.argument("candidate-output-dir")
@click.argument("ward-template-file")
@click.argument("ward-output-dir")
def main(csv_file, candidate_template_file, candidate_output_dir, ward_template_file, ward_output_dir):
    # Render ward pages
    ward_template = open(ward_template_file).read()
    for ward_name, candidates in CONTESTED_WARDS.items():
        data = {"candidates": [{"candidate_name": candidate,
                                "candidate_name_kebab": kebabify(candidate),
                                "picture": NAME_TO_PHOTO[candidate]}
                               for candidate in candidates]}
        rendered_output = chevron.render(ward_template, data)
        name_kebab = "-".join(ward_name.lower().split())
        output_path = os.path.join(ward_output_dir, f"{name_kebab}.html")
        print(f"Writing {output_path}")
        open(output_path, "w").write(rendered_output)
    # Render candidate pages
    row_dicts = [row for row in csv.DictReader(open(csv_file))]
    candidate_template = open(candidate_template_file).read()
    row_dicts = munge(row_dicts)
    for row in row_dicts:
        rendered_output = chevron.render(candidate_template, row)
        name_kebab = "-".join(row["candidate_name"].lower().split())
        output_path = os.path.join(candidate_output_dir, f"{name_kebab}.html")
        print(f"Writing {output_path}")
        open(output_path, "w").write(rendered_output)

if __name__ == "__main__":
    main()
