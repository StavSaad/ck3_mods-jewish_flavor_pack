# Generates the Mishpacha contract events (events/jip_mishpacha_contract_events.txt), the contract scheme types
# (common/schemes/scheme_types/jip_mishpacha_contract_schemes.txt), their approach modifiers
# (common/modifiers/jip_contract_scheme_modifiers.txt) and the event and scheme part of jip_mishpacha_contracts_l_english.yml.
# Contracts with a 'scheme' entry run as contract schemes; the rest resolve in two events. See the events file header.
import os
import re

os.chdir(r'C:\Users\stavs\OneDrive\Documents\Paradox Interactive\Crusader Kings III\mod\jewitup')

# Option fields: approach flag, skill, bonus, trigger (or None), gold cost as share of the stake (or 0), name, tooltip,
# result text for this approach. A 'special' option completes the contract directly with that reward (no roll).
C = [
    dict(n=10, key='loan', theme='stewardship_wealth_focus', left='steward', right='employer', right_anim='worry', lower=None,
         t='The Debt Falls Due',
         desc="The term of the loan to [employer.GetTitledFirstName] has run out. [employer.GetSheHe|U] receives my letter graciously, speaks warmly of our friendship, and says nothing about the money.\\n\\nThe family's silver will not come home on its own.",
         opts=[
             dict(a='courtesy', skill='diplomacy', bonus=0, name='A courteous reminder, and then another',
                  tt='Whatever comes of it, [employer.GetTitledFirstName] keeps a #P warmer opinion#! of the family',
                  res="I wrote as one friend to another, then again, and then a third time, each letter warmer than the last and each a little more pointed."),
             dict(a='goods', skill='stewardship', bonus=10, name='Rents and goods will do in place of coin',
                  tt='#P Easier#!, and the goods sell on at a #P profit#!, but [employer.GetTitledFirstName] #N resents#! what is taken',
                  res="Rather than wait for coin that may never come, I asked for the rents of a few villages and a share of the next harvest, to be sold on in the markets."),
             dict(a='pressure', skill='intrigue', bonus=0, name="Buy up [employer.GetHerHis] other debts, and call them all in",
                  tt='On success, a #P hold#! over [employer.GetTitledFirstName]; on failure, #N an enemy#!',
                  res="Quietly, the family bought up what [employer.GetTitledFirstName] owed to others, until there was no creditor left in the land but us."),
             dict(a='forgive', special='jip_contract_loan_forgiven', name='Forgive it. A ruler in our debt is worth more',
                  tt='No repayment, but a #P favor#! owed'),
         ],
         out=dict(critical=("Every coin came back, with interest and an apology, and [employer.GetTitledFirstName] spoke of the family to [employer.GetHerHis] whole court.", "The family's word is its credit"),
                  success=("The debt was paid at last, with the interest agreed. Not a coin more.", "Paid in full"),
                  failure=("In the end [employer.GetTitledFirstName] paid back what [employer.GetSheHe] could, which was half, and swore that the rest was the fault of the times.", "Half is better than nothing"))),
    dict(n=20, key='tolls', theme='stewardship_domain_focus', left='steward', right='employer', right_anim='personality_greedy', lower=None,
         t="The Season's Tolls",
         desc="The caravans have come and gone through the gates of [employer.GetPrimaryTitle.GetNameNoTier], and the family's clerks have stood at every one. Now the reckoning: what was taken, what [employer.GetTitledFirstName] is owed, and what is left for us.",
         opts=[
             dict(a='strict', skill='stewardship', bonus=0, name='Strict ledgers at every gate',
                  tt='On success, a #P larger take#!',
                  res="I had every bale weighed and every coin entered twice. The merchants grumbled, and paid."),
             dict(a='lenient', skill='diplomacy', bonus=10, name='Go easy on the merchants, and they will come back',
                  tt='#P Easier#! and wins #P prestige#! and [employer.GetTitledFirstName]\'s #P favor#!, but a #N smaller take#!',
                  res="I let the small traders through for a token and kept the gates moving. Word spread that the tolls of [employer.GetPrimaryTitle.GetNameNoTier] were fair."),
             dict(a='books', skill='intrigue', bonus=15, name='The books need not record everything',
                  tt='#P Easier#!, and on success #P twice the take#!; on failure, a #N scandal#!',
                  res="Two sets of books, and the clerks who kept them well paid for their silence."),
         ],
         out=dict(critical=("The season was the best the city had seen in years, and [employer.GetTitledFirstName] was so pleased with [employer.GetHerHis] share that [employer.GetSheHe] never asked to see the family's.", "A season to remember"),
                  success=("The tolls were gathered, [employer.GetTitledFirstName] was paid, and the family kept its share.", "A fair season's work"),
                  failure=("The take fell short. Merchants took other roads, clerks went missing, and [employer.GetTitledFirstName] wants to know where [employer.GetHerHis] money went.", "The gates were not kind to us"))),
    dict(n=30, key='caravan', theme='silk_road', left='thinking', right='employer', right_anim='interested', lower=None,
         t='Fitting Out the Caravan',
         desc="The caravan of [employer.GetTitledFirstName] is being fitted out for the eastern markets, and the family's share is aboard. The roads are long: storms, bandits, a toll-keeper with a new idea. How it travels, and who goes with it, is ours to decide.",
         scheme=dict(target='employer', illustration='ep2_travel_desert', success=['agent_bookkeeper', 'agent_outrider', 'agent_scout'], speed=['agent_supplier', 'agent_planner'],
                     action='Send a caravan for', blurb="A caravan takes months to reach the markets and come home. The family's agents see to its cargo, its guards and its road."),
         opts=[
             dict(a='spread', skill='stewardship', bonus=15, pace='slow', mix='success', name='Spread the cargo over many beasts and many hands',
                  tt='#P Safer#! but #N slower#!, and a #N smaller return#!',
                  res="I had the family's share split among a dozen traders, so that no one loss could ruin us."),
             dict(a='communities', skill='diplomacy', bonus=0, mix='balanced', name='Write ahead to the communities along the road',
                  tt='On success, the communities\' thanks bring #P piety#!',
                  res="Letters went ahead to every Jewish community on the road, asking them to shelter the caravan, feed its beasts and warn it of trouble."),
             dict(a='desert', skill='stewardship', bonus=-15, pace='fast', mix='speed', name='Send it across the desert, the short way',
                  tt='#P Faster#! but #N riskier#!, and on success a #P much larger return#!',
                  res="I sent word to turn the caravan off the long road and across the desert, where there are no tolls and few wells."),
             dict(a='radhanite', skill='stewardship', bonus=25, mix='balanced', trigger='culture = culture:radhanite', name='Send it by the old Radhanite roads',
                  tt='The Radhanites know these roads #P better than anyone#!',
                  res="The old Radhanite roads are known to few but our own people, and the caravan took them from well to well and from community to community."),
         ],
         out=dict(critical=("The caravan came home heavy with silk, pepper and paper, and the family's share sold for twice what it cost.", "Twice over"),
                  success=("The caravan came home late and footsore, but whole, and the family's share sold at a good price.", "A profitable venture"),
                  failure=("Of the caravan, a few beasts and fewer men came home. What was saved barely covers a quarter of the family's share.", "The road took its toll"))),
    dict(n=40, key='envoy', theme='diplomacy_foreign_affairs_focus', left='personality_rational', right='target', right_anim='thinking', lower='employer',
         t='Carrying the Terms',
         desc="[employer.GetTitledFirstName] has given the family terms to carry to [jip_contract_target.GetTitledFirstName], a ruler of another faith who will trust them no more than [jip_contract_target.GetSheHe] trusts [employer.GetTitledFirstName].\\n\\nHow they are carried, and how they are argued, is up to us.",
         scheme=dict(target='target', illustration='councilchamber', success=['agent_diplomat', 'agent_scribe', 'agent_cleric_success'], speed=['agent_herald', 'agent_socialite'],
                     action='Carry terms to', blurb="Terms carried between two courts of different faiths need going over many times before anyone will sign. The family's agents carry the letters and sound out the other side."),
         opts=[
             dict(a='argue', skill='diplomacy', bonus=0, mix='balanced', name='Argue the terms point by point',
                  tt='A plain negotiation, without side effects',
                  res="I went through the terms clause by clause, conceding the small points to win the large ones."),
             dict(a='law', skill='learning', bonus=0, mix='success', name='Cite the treaties and the law of nations',
                  tt='On success, #P prestige#! for the family\'s learning; on failure, [jip_contract_target.GetTitledFirstName] feels #N lectured#!',
                  res="I laid out the old treaties between the two realms, and what the scholars of both faiths have written on keeping faith with neighbours."),
             dict(a='gifts', skill='diplomacy', bonus=25, mix='speed', cost=0.25, name='Sweeten the letters with gifts',
                  tt='#P Much easier#!, at a #N cost#! in gold',
                  res="The terms arrived with a gift for [jip_contract_target.GetTitledFirstName]: fine cloth, a book, and a horse worth more than the messenger."),
             dict(a='leverage', skill='intrigue', bonus=-10, mix='speed', name='Hint at what each court would rather the other did not know',
                  tt='#N Harder#!; on success, a #P hold#! over [jip_contract_target.GetTitledFirstName]; on failure, #N both courts#! distrust the family',
                  res="Between the clauses I let it be known that the family hears a great deal, from both courts, and could be persuaded to forget some of it."),
         ],
         out=dict(critical=("Both sides signed, both thanked the family, and [jip_contract_target.GetTitledFirstName] asked whether we might carry [jip_contract_target.GetHerHis] letters too.", "Peace made, and friends of both"),
                  success=("The terms were accepted, with a few changes that [employer.GetTitledFirstName] can live with.", "The terms are agreed"),
                  failure=("[jip_contract_target.GetTitledFirstName] tore up the terms, and [employer.GetTitledFirstName] blames the messenger.", "No agreement"))),
    dict(n=50, key='ransom', theme='prison', left='personality_compassionate', right='employer', right_anim='personality_greedy', lower='target',
         t='The Price of a Captive',
         desc="[employer.GetTitledFirstName] has named the price of [jip_contract_target.GetFirstName]'s freedom, and named it high, knowing that [ROOT.Char.Custom('JipFaithfulMany')] will pay for their own. [ROOT.Char.Custom('JipRansomWarning')]\\n\\nAnd yet [jip_contract_target.GetSheHe] is still in the dark.",
         scheme=dict(target='employer', illustration='dungeon', success=['agent_diplomat', 'agent_cleric_success', 'agent_scribe'], speed=['agent_herald', 'agent_socialite'],
                     action='Redeem a captive from', blurb="Captors are in no hurry, and a ransom is argued over for months. The family's agents carry the offers and keep the captive fed in the meantime."),
         opts=[
             dict(a='haggle', skill='diplomacy', bonus=0, mix='balanced', name='Haggle the price down',
                  tt='A plain bargain: half the price on success, nothing on the best outcome',
                  res="I haggled as if over a bale of cloth, as [ROOT.Char.Custom('JipFaithTeachers')] advise, so that the captor would not think a [ROOT.Char.Custom('JipFaithfulOne')]'s life worth a fortune."),
             dict(a='mercy', skill='learning', bonus=10, mix='success', name="Appeal to the captor's mercy and to [employer.GetHerHis] own faith",
                  tt='#P Easier#!; on success, extra #P piety#!; on failure, [employer.GetTitledFirstName] is #N insulted#!',
                  res="I reminded [employer.GetTitledFirstName] what [employer.GetHerHis] own scriptures say of mercy to the prisoner, and of the reward that awaits it."),
             dict(a='pay', special='jip_contract_ransom_paid', trigger='gold >= scope:task_contract.var:jip_contract_stake', name='Pay what is asked. A life is not for bargaining',
                  tt='The captive goes free #P for certain#!, at the #N full price#!'),
         ],
         out=dict(critical=("[employer.GetTitledFirstName] let [jip_contract_target.GetFirstName] go for nothing at all, and [jip_contract_target.GetSheHe] wept at our door.", "Redeemed"),
                  success=("A price was agreed, half of what was asked, and [jip_contract_target.GetFirstName] walked out into the light.", "Redeemed, at a price"),
                  failure=("[employer.GetTitledFirstName] would not move, and [jip_contract_target.GetFirstName] remains in the dark.", "We could not free them"))),
    dict(n=60, key='physician', theme='learning_medicine_focus', left='physician', right='target', right_anim='sick', lower='employer',
         t='At the Bedside',
         desc="[jip_contract_target.GetTitledFirstName] lies pale and feverish, while the court physicians argue over bleeding and the priests over prayers. They make way, not gladly, for the [ROOT.Char.Custom('JipFaithfulOne')].",
         opts=[
             dict(a='galen', skill='learning', bonus=0, name='Treat by Hippocrates and Galen',
                  tt='The learned course, without side effects',
                  res="I treated by the books of Hippocrates and Galen: the humours weighed, the pulse taken morning and night, the remedies measured to the grain."),
             dict(a='regimen', skill='stewardship', bonus=15, name='Order the household: diet, rest and clean air',
                  tt='#P Safer#!, but a #N smaller fee#!',
                  res="As [ROOT.Char.Custom('JipPhysicianMaster')] taught, I began with the household: plain food, clean water, open windows and quiet, and no more bleeding."),
             dict(a='bold', skill='learning', bonus=-15, name='Try a bold remedy the court physicians would not dare',
                  tt='#N Riskier#!; on success, a #P large fee#! and #P prestige#!; on failure, the patient is #N worse#!',
                  res="I gave a remedy from the Arabic books that the court physicians had never seen, and would not have dared."),
             dict(a='own_hand', skill='learning', bonus=20, trigger='has_trait = lifestyle_physician', name='Trust my own practised hand',
                  tt='A trained physician does #P much better#!',
                  res="I have treated this illness before, and I treated it again."),
         ],
         out=dict(critical=("Within a week [jip_contract_target.GetFirstName] was sitting up and asking for food, and the court physicians were asking for my books.", "A remarkable recovery"),
                  success=("The fever broke slowly, and [jip_contract_target.GetFirstName] is on the mend.", "On the mend"),
                  failure=("Nothing I did seemed to help, and [employer.GetTitledFirstName] has sent for other physicians.", "Beyond my skill"))),
    dict(n=70, key='translate', theme='learning_scholarship_focus', left='writing', right='employer', right_anim='reading', lower=None,
         t='A Book to Render',
         desc="The book from [employer.GetTitledFirstName] lies open on the table, its margins crowded with notes. Some words have no equal in [employer.GetCulture.GetNameNoTooltip], and the meaning of the whole may hang on how they are rendered.",
         scheme=dict(target='employer', illustration='study', success=['agent_scribe', 'agent_tutor', 'agent_theologian_success'], speed=['agent_theologian', 'agent_planner'],
                     action='Translate a book for', blurb="A book is not translated in a week. The family's scribes copy, check and copy again, page by page."),
         opts=[
             dict(a='literal', skill='learning', bonus=0, mix='success', name='Word for word, as the author wrote it',
                  tt='On success, a faithful text brings #P piety#!',
                  res="I rendered it word for word, as faithfully as the two tongues allow, and let the reader do the rest."),
             dict(a='courtly', skill='diplomacy', bonus=0, mix='balanced', name='Rendered to please the ear of the court',
                  tt='On success, [employer.GetTitledFirstName] is #P delighted#!',
                  res="I rendered it as a poet would, smoothing the hard passages and flattering the patron where the author allowed."),
             dict(a='commentary', skill='learning', bonus=-15, mix='success', name='Add a commentary of our own',
                  tt='#N Harder#!; on success, the family\'s name is made (#P prestige#!, #P renown#!); on failure, #N mocked#!',
                  res="I added a commentary of my own, explaining the hard passages and answering the author where I thought him wrong."),
             dict(a='language', skill='learning', bonus=20, mix='speed', trigger='knows_language_of_culture = scope:employer.culture', name="I know the patron's tongue well enough to do it justice",
                  tt="Knowing [employer.GetCulture.GetNameNoTooltip] makes it #P much easier#!",
                  res="I know [employer.GetCulture.GetNameNoTooltip] as well as I know [ROOT.Char.Custom('JipFaithTongue')], and it shows on every page."),
         ],
         out=dict(critical=("[employer.GetTitledFirstName] had the translation copied for every scholar at court, and the family's name on every copy.", "A book for the ages"),
                  success=("[employer.GetTitledFirstName] has the book [employer.GetSheHe] wanted, and has paid for it.", "The work is delivered"),
                  failure=("[employer.GetTitledFirstName]'s scholars found errors on the first page, and more on the second.", "A poor translation"))),
    dict(n=80, key='responsum', theme='learning_theology_focus', left='page_flipping', right='employer', right_anim='thinking', lower=None,
         t='A Question of Law',
         desc="The question from [employer.GetTitledFirstName] has been read and read again. The sources disagree, the local custom is unclear, and whatever answer goes back will be copied and cited for years.",
         opts=[
             dict(a='strict', skill='learning', bonus=0, name='Rule strictly, by the letter of the law',
                  tt='On success, extra #P piety#!; [employer.GetTitledFirstName] is #N displeased#! either way',
                  res="I ruled by the letter of the law, as the sources most plainly read, whatever it costs the asker."),
             dict(a='lenient', skill='diplomacy', bonus=10, name='Rule leniently, for the sake of peace in the community',
                  tt='#P Easier#!, and on success [employer.GetTitledFirstName] is #P grateful#!, but #N less piety#!',
                  res="I found the lenient reading, as the House of Hillel would, for the sake of peace in the community."),
             dict(a='beit_din', skill='learning', bonus=20, trigger='domicile ?= { OR = { has_domicile_parameter = jip_estate_beit_din_1 has_domicile_parameter = jip_estate_beit_din_2 } }',
                  name='Put it before our Beit Din',
                  tt='A ruling of the family\'s court is #P much likelier#! to stand, and adds to its #P renown#!',
                  res="I put the question before the judges of our own Beit Din, and sent their ruling under all three seals."),
         ],
         out=dict(critical=("The responsum is already being copied in other cities, and scholars cite it by the family's name.", "Cited far and wide"),
                  success=("The answer was received and accepted, and [employer.GetTitledFirstName] has sent thanks.", "The question is settled"),
                  failure=("Other scholars have written to dispute the ruling, and [employer.GetTitledFirstName] is left more confused than before.", "A disputed ruling"))),
    dict(n=90, key='news', theme='intrigue_skulduggery_focus', left='scheme', right='employer', right_anim='interested', lower='target',
         t='Whom to Ask',
         desc="[employer.GetTitledFirstName] wants to know what [jip_contract_target.GetTitledFirstName] is planning. The family's correspondents write from every market and community, and read more than they are shown. The question is whom to ask.",
         scheme=dict(target='target', illustration='corridor', success=['agent_scribe', 'agent_bookkeeper', 'agent_diplomat'], speed=['agent_infiltrator', 'agent_socialite'],
                     action='Gather news on', blurb="Letters take weeks to come and go, and the best news takes several. The family's agents keep the correspondence moving and sift what comes back."),
         opts=[
             dict(a='merchants', skill='stewardship', bonus=0, mix='balanced', name="Ask the merchants who trade at the rival's court",
                  tt="On success, the merchants' gossip sells for #P extra gold#!; on failure, [jip_contract_target.GetTitledFirstName] #N learns who asked#!",
                  res="I asked the merchants who sell at [jip_contract_target.GetTitledFirstName]'s court what they had seen and heard, and paid for the answers."),
             dict(a='communities', skill='diplomacy', bonus=0, mix='success', name="Ask the [ROOT.Char.Custom('JipFaithfulMany')] of the rival's realm",
                  tt='They will #P never give the family away#!, whatever comes of it',
                  res="I wrote to the [ROOT.Char.Custom('JipFaithfulMany')] of [jip_contract_target.GetTitledFirstName]'s realm, who see much and are asked little."),
             dict(a='clerk', skill='intrigue', bonus=15, mix='speed', cost=0.25, name="Pay a clerk to copy the rival's letters",
                  tt='#P Easier#!, at a #N cost#! in gold; on failure, a #N scandal#!',
                  res="A clerk in [jip_contract_target.GetTitledFirstName]'s chancery was paid to copy what crossed his desk."),
         ],
         out=dict(critical=("The letters told [employer.GetTitledFirstName] everything [employer.GetSheHe] wanted, and the family something more besides.", "More than we were asked for"),
                  success=("[employer.GetTitledFirstName] has the news [employer.GetSheHe] wanted, and has paid for it.", "The news is delivered"),
                  failure=("The letters held nothing of use, and [employer.GetTitledFirstName] has paid for nothing.", "Nothing worth knowing"))),
    dict(n=100, key='horoscope', theme='learning_scholarship_focus', left='reading', right='employer', right_anim='interested', lower=None,
         t='What the Stars Foretell',
         desc="[employer.GetTitledFirstName] wants [employer.GetHerHis] horoscope cast: the hour of [employer.GetHerHis] birth, the houses of the planets, the conjunctions of the years to come. The court astrologers have already given one answer; [employer.GetSheHe] wants a Harranian's.\n\nThe heavens say what they say. What [employer.GetSheHe] hears is another matter.",
         opts=[
             dict(a='tables', skill='learning', bonus=0, name='Cast it from the tables, line by line',
                  tt='The learned course, without side effects',
                  res="I worked from the tables of the Zij, the ascendant and the twelve houses, and set down only what the reckoning gave."),
             dict(a='flatter', skill='diplomacy', bonus=15, name='Read the stars as [employer.GetSheHe] would wish them read',
                  tt='#P Easier#!, and [employer.GetTitledFirstName] is #P pleased#!, but it wins the family #N no renown#!',
                  res="I found in the heavens long life, victory and many sons, as the court had hoped, and kept the darker aspects to myself."),
             dict(a='warn', skill='learning', bonus=-10, name='Tell [employer.GetHerHim] what the stars truly say, however dark',
                  tt='#N Riskier#!; on success, #P prestige#! and a #P larger fee#!; on failure, [employer.GetTitledFirstName] is #N offended#!',
                  res="Mars stood ill in the house of enemies, and I said so plainly, with the years and the remedies."),
             dict(a='observatory', skill='learning', bonus=20, trigger='domicile ?= { has_domicile_building_or_higher = library_observatory_03 }', name="Take the planets' places from our own Observatory",
                  tt='An Observatory of our own does #P much better#!',
                  res="I had the planets' places taken that very night from the family's Observatory, rather than trusting old tables."),
         ],
         out=dict(critical=("[employer.GetTitledFirstName] keeps the horoscope by [employer.GetHerHis] bed, and the court astrologers have asked how it was done.", "Written in the stars"),
                  success=("[employer.GetTitledFirstName] has the horoscope [employer.GetSheHe] wanted, and has paid for it.", "The horoscope is cast"),
                  failure=("[employer.GetTitledFirstName] found the horoscope muddled and its predictions wrong, and has said so to the whole court.", "Clouded heavens"))),
]

OUTCOMES = ['critical', 'success', 'failure']
ANIM = {
    'critical': ('happiness', 'admiration'),
    'success': ('personality_content', 'acknowledging'),
    'failure': ('worry', 'disapproval'),
}
SCOPE = {'root': 'root', 'employer': 'scope:employer', 'target': 'scope:jip_contract_target'}
SKILL_ILLUSTRATION_BG = {'stewardship': 'study', 'diplomacy': 'council_chamber', 'learning': 'physicians_study', 'intrigue': 'corridor_night'}
# the mod's banner in the event window's top right, like a DLC's (gui/event_window_widgets/jip_event_source_badge.gui);
# the scheme outcome windows have no container for it
SOURCE_BADGE = ('\twidgets = {\n\t\twidget = {\n\t\t\tgui = "jip_event_source_badge"\n'
                '\t\t\tcontainer = "foreground_shader_vfx_container"\n\t\t}\n\t}\n')


def portrait(slot, who, anim, outcome_anims=False, other=False, outcomes=OUTCOMES):
    s = f'\t{slot} = {{\n\t\tcharacter = {SCOPE[who]}\n'
    if outcome_anims:
        i = 1 if other else 0
        for oc in ('critical', 'failure'):
            if oc in outcomes and len(outcomes) > 1:
                s += f'\t\ttriggered_animation = {{\n\t\t\ttrigger = {{ jip_contract_outcome_is_trigger = {{ OUTCOME = {oc} }} }}\n\t\t\tanimation = {ANIM[oc][i]}\n\t\t}}\n'
        s += f'\t\tanimation = {ANIM["failure" if outcomes == ["failure"] else "success"][i]}\n'
    else:
        s += f'\t\tanimation = {anim}\n'
    return s + '\t}\n'


def target_trigger(c):
    if c['right'] == 'target' or c['lower'] == 'target':
        return '\ttrigger = {\n\t\tjip_mishpacha_contract_event_trigger = yes\n\t\texists = scope:task_contract.var:jip_contract_target\n\t}\n'
    return '\ttrigger = { jip_mishpacha_contract_event_trigger = yes }\n'


def lower(c):
    return f'\tlower_right_portrait = {SCOPE[c["lower"]]}\n' if c['lower'] else ''


def scheme_type(c, skill):
    return f'jip_contract_{c["key"]}_{skill}_scheme'


def approach_modifiers(o):
    mods = []
    b = o['bonus']
    if b > 0:
        mods.append(f'jip_contract_scheme_bonus_{b}_modifier')
    elif b < 0:
        mods.append(f'jip_contract_scheme_malus_{-b}_modifier')
    if o.get('pace'):
        mods.append(f'jip_contract_scheme_pace_{o["pace"]}_modifier')
    return mods


def agent_slots(c, mix):
    s, sp = c['scheme']['success'], c['scheme']['speed']
    return {'success': [s[0], s[0], s[1], s[2], sp[0]],
            'balanced': [s[0], s[1], s[2], sp[0], sp[1]],
            'speed': [s[0], sp[0], sp[0], sp[1], sp[1]]}[mix]


def result_title(e1):
    s = '\ttitle = {\n\t\tfirst_valid = {\n'
    for oc in OUTCOMES[:2]:
        s += f'\t\t\ttriggered_desc = {{\n\t\t\t\ttrigger = {{ jip_contract_outcome_is_trigger = {{ OUTCOME = {oc} }} }}\n\t\t\t\tdesc = {e1}.t.{oc}\n\t\t\t}}\n'
    return s + f'\t\t\tdesc = {e1}.t.failure\n\t\t}}\n\t}}\n'


def result_desc(e1, rolled, outcomes):
    s = '\tdesc = {\n\t\tfirst_valid = {\n'
    # Every approach gets its trigger, or the engine flags the last one's flag as set but never used; it is also the fallback
    for o in rolled:
        s += f'\t\t\ttriggered_desc = {{\n\t\t\t\ttrigger = {{ jip_contract_approach_is_trigger = {{ APPROACH = {o["a"]} }} }}\n\t\t\t\tdesc = {e1}.{o["a"]}\n\t\t\t}}\n'
    s += f'\t\t\tdesc = {e1}.{rolled[-1]["a"]}\n\t\t}}\n'
    if len(outcomes) == 1:
        return s + f'\t\tdesc = {e1}.{outcomes[0]}\n\t}}\n'
    s += '\t\tfirst_valid = {\n'
    for oc in outcomes[:-1]:
        s += f'\t\t\ttriggered_desc = {{\n\t\t\t\ttrigger = {{ jip_contract_outcome_is_trigger = {{ OUTCOME = {oc} }} }}\n\t\t\t\tdesc = {e1}.{oc}\n\t\t\t}}\n'
    return s + f'\t\t\tdesc = {e1}.{outcomes[-1]}\n\t\t}}\n\t}}\n'


def result_options(c, e1, outcomes, end_scheme):
    s = ''
    for oc in outcomes:
        s += f'\n\toption = {{\n\t\tname = {e1}.{oc}.a\n'
        if len(outcomes) > 1:
            s += f'\t\ttrigger = {{ jip_contract_outcome_is_trigger = {{ OUTCOME = {oc} }} }}\n'
        s += f'\t\tjip_contract_finish_effect = {{ CONTRACT = {c["key"]} }}\n'
        if end_scheme:
            s += '\t\tscope:scheme ?= { end_scheme = yes }\n'
        s += '\t}\n'
    return s


ev = ['namespace = jip_mishpacha_contract', '',
      '# Generated by make_contract_events.py. Events for the Mishpacha contracts (common/task_contracts/jip_mishpacha_contracts.txt).',
      '# Event contracts (loan, tolls, physician, responsum):',
      '#   .00X0, a few months after the contract is taken: the family head picks an approach. The outcome is rolled then',
      '#   (jip_contract_choose_approach_effect) and shown as odds in the tooltip.',
      '#   .00X1, a few days later: what came of it, and the contract is completed (jip_contract_finish_effect).',
      '# Scheme contracts (caravan, envoy, ransom, translate, news), like vanilla contract schemes:',
      '#   .00X0, on acceptance: the approach picks the scheme type (its skill), its agents and its modifiers.',
      '#   Executing the scheme from vanilla\'s preparations window (scheme_critical_moments.0002) fires .00X2, which rolls',
      '#   the scheme\'s success chance and fires .00X3 (success window) or .00X4 (failure window), which complete it.',
      '# root = the family head',
      '# scope:task_contract = the contract',
      '# scope:employer = its employer',
      '# scope:jip_contract_target = the other character it is about, if any',
      '# scope:scheme = the contract scheme, for scheme contracts', '']
loc = [' # Events (generated by make_contract_events.py)',
       ' jip_contract_tests_stewardship_tt: "Tests your [stewardship|E]"',
       ' jip_contract_tests_diplomacy_tt: "Tests your [diplomacy|E]"',
       ' jip_contract_tests_learning_tt: "Tests your [learning|E]"',
       ' jip_contract_tests_intrigue_tt: "Tests your [intrigue|E]"',
       ' jip_contract_scheme_stewardship_tt: "Starts a [contract_scheme|E] that relies on your [stewardship|E]"',
       ' jip_contract_scheme_diplomacy_tt: "Starts a [contract_scheme|E] that relies on your [diplomacy|E]"',
       ' jip_contract_scheme_learning_tt: "Starts a [contract_scheme|E] that relies on your [learning|E]"',
       ' jip_contract_scheme_intrigue_tt: "Starts a [contract_scheme|E] that relies on your [intrigue|E]"',
       ' jip_contract_scheme_agents_success_tt: "Agents chosen for #P success#!"',
       ' jip_contract_scheme_agents_balanced_tt: "A #P balanced#! choice of agents"',
       ' jip_contract_scheme_agents_speed_tt: "Agents chosen for #P speed#!"',
       ' jip_contract_outcome_critical_tt: "$label_success_critical$"',
       ' jip_contract_outcome_success_tt: "$label_success_standard$"',
       ' jip_contract_outcome_failure_tt: "$label_failure_standard$"']
schemes = ['# Generated by make_contract_events.py. Contract schemes for the Mishpacha contracts that are long work: one type per',
           '# contract and skill, since the approach chosen when the contract is taken decides the skill. Modelled on vanilla\'s',
           '# laamp contract schemes, but executed into our own events (jip_contract_scheme_prep_effect).', '']
scheme_loc = [' # Contract schemes (generated by make_contract_events.py)',
              ' jip_contract_scheme_desc_success: "$laamp_contract_scheme_desc_success_boilerplate$"']
modifiers_used = set()

for c in C:
    n, key = c['n'], c['key']
    e0, e1, e2, e3, e4 = (f'jip_mishpacha_contract.{n + i:04d}' for i in range(5))
    sc = c.get('scheme')
    rolled = [o for o in c['opts'] if not o.get('special')]

    # Approach event
    what = 'take the contract on' if sc else 'choose an approach'
    s = f'# {c["t"]} ({key}): {what}\n{e0} = {{\n\ttype = character_event\n\ttitle = {e0}.t\n\tdesc = {e0}.desc\n\ttheme = {c["theme"]}\n'
    s += SOURCE_BADGE
    s += portrait('left_portrait', 'root', c['left'])
    s += portrait('right_portrait', c['right'], c['right_anim'])
    s += lower(c)
    s += '\n' + target_trigger(c) + '\n\timmediate = { jip_mishpacha_contract_event_scopes_effect = yes }\n'
    loc += ['', f' {e0}.t: "{c["t"]}"', f' {e0}.desc: "{c["desc"]}"']
    for i, o in enumerate(c['opts']):
        letter = 'abcd'[i]
        s += f'\n\toption = {{\n\t\tname = {e0}.{letter}\n'
        if o.get('cost'):
            cost = f'{{\n\t\t\t\tvalue = scope:task_contract.var:jip_contract_stake\n\t\t\t\tmultiply = {o["cost"]}\n\t\t\t}}'
            s += f'\t\ttrigger = {{\n\t\t\tgold >= {cost}\n\t\t}}\n'
            s += f'\t\tremove_short_term_gold = {cost}\n'
        elif o.get('trigger'):
            s += f'\t\ttrigger = {{ {o["trigger"]} }}\n'
        s += f'\t\tcustom_tooltip = {e0}.{letter}.tt\n'
        if o.get('special'):
            s += f'\t\tscope:task_contract = {{ complete_task_contract = {o["special"]} }}\n'
        elif sc:
            mods = approach_modifiers(o)
            modifiers_used.update(mods)
            s += f'\t\tcustom_tooltip = jip_contract_scheme_{o["skill"]}_tt\n'
            s += f'\t\tcustom_tooltip = jip_contract_scheme_agents_{o["mix"]}_tt\n'
            s += f'\t\tstart_scheme = {{\n\t\t\ttype = {scheme_type(c, o["skill"])}\n\t\t\tcontract = scope:task_contract\n\t\t\ttarget_character = {SCOPE[sc["target"]]}\n\t\t}}\n'
            s += '\t\thidden_effect = {\n\t\t\tscope:task_contract = {\n'
            s += f'\t\t\t\tset_variable = {{\n\t\t\t\t\tname = jip_contract_approach\n\t\t\t\t\tvalue = flag:{o["a"]}\n\t\t\t\t}}\n'
            s += '\t\t\t\tscheme ?= {\n'
            for a in agent_slots(c, o['mix']):
                s += f'\t\t\t\t\tadd_agent_slot = {a}\n'
            for m in mods:
                s += f'\t\t\t\t\tadd_scheme_modifier = {{ type = {m} }}\n'
            s += '\t\t\t\t}\n\t\t\t}\n\t\t}\n'
            s += '\t\topen_view = {\n\t\t\tview = intrigue_window\n\t\t\tplayer = root\n\t\t}\n'
        else:
            s += f'\t\tjip_contract_choose_approach_effect = {{ SKILL = {o["skill"]} BONUS = {o["bonus"]} APPROACH = {o["a"]} EVENT = {e1} }}\n'
        s += '\t}\n'
        loc += [f' {e0}.{letter}: "{o["name"]}"', f' {e0}.{letter}.tt: "{o["tt"]}"']
    s += '}\n'
    ev.append(s)

    if not sc:
        # Result event
        s = f'# {c["t"]} ({key}): the result\n{e1} = {{\n\ttype = character_event\n'
        s += result_title(e1) + result_desc(e1, rolled, OUTCOMES)
        s += f'\ttheme = {c["theme"]}\n'
        s += SOURCE_BADGE
        s += portrait('left_portrait', 'root', None, outcome_anims=True)
        s += portrait('right_portrait', c['right'], None, outcome_anims=True, other=True)
        s += lower(c)
        s += '\n' + target_trigger(c) + '\n\timmediate = { jip_mishpacha_contract_event_scopes_effect = yes }\n'
        s += result_options(c, e1, OUTCOMES, False) + '}\n'
        ev.append(s)
    else:
        # Execution: roll the scheme's success chance, as vanilla's roll_scheme_success_or_failure_effect does
        s = f'# {c["t"]} ({key}): the scheme is executed\n{e2} = {{\n\thidden = yes\n\n'
        s += '\ttrigger = {\n\t\tjip_mishpacha_contract_event_trigger = yes\n\t\texists = scope:scheme\n\t}\n\n'
        s += '\timmediate = {\n\t\tjip_mishpacha_contract_event_scopes_effect = yes\n'
        s += f'\t\tjip_contract_roll_scheme_effect = {{ SUCCESS_EVENT = {e3} FAILURE_EVENT = {e4} }}\n\t}}\n}}\n'
        ev.append(s)
        # Success and failure, in vanilla's scheme outcome windows
        for e, window, outcomes in ((e3, 'scheme_successful_event', ['critical', 'success']), (e4, 'scheme_failed_event', ['failure'])):
            s = f'# {c["t"]} ({key}): the scheme {"succeeds" if outcomes[0] != "failure" else "fails"}\n{e} = {{\n\ttype = character_event\n\twindow = {window}\n'
            if len(outcomes) > 1:
                s += '\ttitle = {\n\t\tfirst_valid = {\n'
                s += f'\t\t\ttriggered_desc = {{\n\t\t\t\ttrigger = {{ jip_contract_outcome_is_trigger = {{ OUTCOME = critical }} }}\n\t\t\t\tdesc = {e1}.t.critical\n\t\t\t}}\n'
                s += f'\t\t\tdesc = {e1}.t.success\n\t\t}}\n\t}}\n'
            else:
                s += f'\ttitle = {e1}.t.failure\n'
            s += result_desc(e1, rolled, outcomes)
            s += f'\ttheme = {c["theme"]}\n'
            s += portrait('center_portrait', 'root', None, outcome_anims=True, outcomes=outcomes)
            s += portrait('right_portrait', sc['target'], None, outcome_anims=True, other=True, outcomes=outcomes)
            s += '\n' + target_trigger(c) + '\n\timmediate = { jip_mishpacha_contract_event_scopes_effect = yes }\n'
            s += result_options(c, e1, outcomes, True) + '}\n'
            ev.append(s)

        # Scheme types
        skills = []
        for o in rolled:
            if o['skill'] not in skills:
                skills.append(o['skill'])
        scheme_loc += ['', f' jip_contract_{key}_scheme_desc_general: "{sc["blurb"]}$laamp_contract_scheme_desc_general_boilerplate$"']
        for sk in skills:
            st = scheme_type(c, sk)
            schemes.append(f'''# {c["t"]}, by {sk}
{st} = {{
	skill = {sk}
	desc = {st}_desc_general
	success_desc = jip_contract_scheme_desc_success
	icon = {sk}
	illustration = "gfx/interface/illustrations/event_scenes/{sc["illustration"]}.dds"
	target_type = character
	category = contract

	speed_per_skill_point = t2_spsp_owner_value
	base_progress_goal = t3_base_phase_length_value
	base_maximum_success = t3_base_max_success_value
	phases_per_agent_charge = 1
	success_chance_growth_per_skill_point = laamp_contract_scgpsp_value
	spymaster_speed_per_skill_point = 0
	uses_resistance = no

	valid = {{
		jip_contract_scheme_valid_trigger = yes
	}}

	agent_leave_threshold = -25
	agent_join_chance = {{
		base = 0
		ai_agent_join_chance_laamp_contract_modifier = yes
	}}
	valid_agent = {{ is_valid_agent_standard_trigger = yes }}
	agent_groups_owner_perspective = {{ courtiers }}

	base_success_chance = {{
		base = 0
		scheme_type_skill_success_chance_modifier = {{ SKILL = {sk.upper()} }}
		laamp_contract_scheme_basic_success_chance_modifier = yes
		jip_contract_scheme_{sk}_success_modifier = yes
	}}

	on_phase_completed = {{
		suppress_scheme_follow_up_event_till_input_given_effect = yes
		jip_contract_scheme_prep_effect = {{ EVENT = {e2} }}
		cap_schemes_and_fire_reminders_effect = yes
	}}
	on_hud_click = {{ jip_contract_scheme_prep_effect = {{ EVENT = {e2} }} }}
	on_invalidated = {{ jip_contract_scheme_invalidated_effect = yes }}
}}
''')
            scheme_loc += [f' {st}: "$jip_contract_{key}_contract$"', f' {st}_action: "{sc["action"]}"',
                           f' {st}_desc: "$jip_contract_{key}_scheme_desc_general$"',
                           # The engine looks for <scheme>_desc_general, like vanilla's laamp schemes
                           f' {st}_desc_general: "$jip_contract_{key}_scheme_desc_general$"']

    for o in rolled:
        loc.append(f' {e1}.{o["a"]}: "{o["res"]}\\n\\n"')
    for oc in OUTCOMES:
        text, title = c['out'][oc]
        loc += [f' {e1}.t.{oc}: "{title}"', f' {e1}.{oc}: "{text}"']
    loc += [f' {e1}.critical.a: "Better than I hoped"', f' {e1}.success.a: "It is done"', f' {e1}.failure.a: "We will do better next time"']

open('events/jip_mishpacha_contract_events.txt', 'wb').write(b'\xef\xbb\xbf' + '\n'.join(ev).replace('\n', '\r\n').encode('utf-8'))
open('common/schemes/scheme_types/jip_mishpacha_contract_schemes.txt', 'wb').write(b'\xef\xbb\xbf' + '\n'.join(schemes).replace('\n', '\r\n').encode('utf-8'))

# Approach modifiers on the schemes
MOD = ['# Generated by make_contract_events.py. Added to Mishpacha contract schemes by the approach chosen (events, .00X0).', '']
MOD_LOC = []
for m in sorted(modifiers_used):
    kind, amount = m.split('_')[3], m.split('_')[4]
    if kind == 'bonus':
        MOD.append(f'{m} = {{\n\ticon = intrigue_positive\n\tscheme_success_chance = {amount}\n\tscheme_success_chance_max = {amount}\n}}\n')
        MOD_LOC.append(f' {m}: "Favourable Approach"')
    elif kind == 'malus':
        MOD.append(f'{m} = {{\n\ticon = intrigue_negative\n\tscheme_success_chance = -{amount}\n}}\n')
        MOD_LOC.append(f' {m}: "Risky Approach"')
    elif amount == 'slow':
        MOD.append(f'{m} = {{\n\ticon = intrigue_negative\n\tscheme_phase_duration = 15\n}}\n')
        MOD_LOC.append(f' {m}: "Unhurried Approach"')
    else:
        MOD.append(f'{m} = {{\n\ticon = intrigue_positive\n\tscheme_phase_duration = -25\n}}\n')
        MOD_LOC.append(f' {m}: "Hasty Approach"')
open('common/modifiers/jip_contract_scheme_modifiers.txt', 'wb').write(b'\xef\xbb\xbf' + '\n'.join(MOD).replace('\n', '\r\n').encode('utf-8'))

p = 'localization/english/jip_mishpacha_contracts_l_english.yml'
t = open(p, encoding='utf-8-sig').read().replace('\r\n', '\n')
t = t[:t.index(' # Events')].rstrip('\n') + '\n\n' + '\n'.join(loc) + '\n\n' + '\n'.join(scheme_loc) + '\n\n # Scheme approach modifiers (generated)\n' + '\n'.join(MOD_LOC) + '\n'
open(p, 'wb').write(b'\xef\xbb\xbf' + t.replace('\n', '\r\n').encode('utf-8'))
print('events:', len(ev) - 1, 'schemes:', len(schemes) - 4, 'modifiers:', sorted(modifiers_used))
