import re
from pprint import pprint

from sqlalchemy import select
from sqlalchemy.orm import Session as Database, selectinload
from website.internal.database import get_session
from website.internal import models

import json
from lxml import html
from requests import Session
import requests


def admin_web_scrape_problems(
        db: Database
):
    base_url = 'http://www.usaco.org/index.php?page=viewproblem2&cpid='
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"

    first_index = 0
    last_index = 1300

    prevContestInfo = {}
    prevContestInfo['id'] = -1
    prevContestInfo['year'] = 0
    prevContestInfo['month'] = ""
    prevContestInfo['div'] = ""

    failed = []
    for i in range(first_index, last_index + 1):
        url = base_url + str(i)
        print('Requesting: ' + url)

        try:
            page = requests.get(url, headers=headers)
            data = html.fromstring(page.content)
            contestInfo = data.xpath('string(//div[@class="panel"]/h2[1])').split()
            nameInfo = data.xpath('string(//div[@class="panel"]/h2[2])').split('.')

            if not contestInfo:
                continue

            pid = i
            name = nameInfo[1].strip()
            for info in contestInfo:
                if re.match(r"20[0-9][0-9]", info):
                    year = int(info)
                elif info == "US":
                    month = "US Open"
                elif info == "November" or info == "December" or info == "January" or info == "February" or info == "March":
                    month = info
                elif info == "Bronze" or info == "Silver" or info == "Gold" or info == "Platinum":
                    div = info

            contest = db.execute(select(models.Contest).filter(models.Contest.year == year, models.Contest.month == month, models.Contest.division == div)).scalars().first()
            if not contest:
                contest = models.Contest(year=year, month=month, division=div)
                db.add(contest)
                db.commit()
                db.refresh(contest)
                print('NEW CONTEST: {} {} {} {}'.format(contest.id, year, month, div))

            prevContestInfo['id'] = contest.id
            prevContestInfo['year'] = year
            prevContestInfo['month'] = month
            prevContestInfo['div'] = div

            problem = db.execute(select(models.Problem).filter(models.Problem.id == pid)).scalars().first()
            if not problem:
                problem = models.Problem(id=pid, name=name, contest_id=contest.id)
                db.add(problem)
                db.commit()
                db.refresh(problem)

            print(problem.id, div, name)

        except Exception as e:
            print(
                'Failed to retrieve data for {} {} {} {} {}. ({})'.format(i, year, month, div, name, str(e)))
            failed.append(name)

    print('Error retrieving the following problems:')
    pprint(failed)


def web_scrape_problem_cases(
        db: Database,
        s: Session,
        user_id: int,
):
    status_url = 'http://www.usaco.org/current/tpcm/status-update.php'

    for problem in db.execute(select(models.Problem)).scalars().all():
        # print('Fetching problem#{}'.format(problem.id))

        try:
            problem_url = 'http://www.usaco.org/index.php?page=viewproblem2&cpid=' + str(problem.id)
            r = s.get(problem_url)
            problem_page = html.fromstring(r.text)
            sid = problem_page.xpath('string(//*[@id="last-status"]/@data-sid)')
            if sid == "-1":
                # user has not attempted problem
                continue

            payload = {'sid': sid}
            r = s.post(status_url, data=payload)

            div_text = json.loads(r.text)["jd"]
            if div_text == "":
                # user failed sample case
                continue

            trial_info = html.fromstring(div_text[:len(div_text) - 1])
            cases = trial_info.findall('a')

            entry = db.execute(select(models.ChecklistEntry).filter(models.ChecklistEntry.user_id == user_id, models.ChecklistEntry.problem_id == problem.id)).scalars().first()
            if not entry:
                entry = models.ChecklistEntry(status=0, problem_id=problem.id, user_id=user_id)
                db.add(entry)
                db.commit()
                db.refresh(entry)

            all_correct = True
            for case in cases:
                symbol = case.find('div[1]/div[1]').text
                number = case.find('div[1]/div[2]').text
                memory = ""
                time = ""
                is_correct = False
                case_classes = case.find('div[1]').classes
                for cssclass in case_classes:
                    if cssclass == "trial-status-yes":
                        is_correct = True
                        memory = case.find('div[1]/div[3]/span[1]').text
                        time = case.find('div[1]/div[3]/span[2]').text

                entry_case = db.execute(select(models.ChecklistEntryCase).filter(models.ChecklistEntryCase.entry_id == entry.id, models.ChecklistEntryCase.case_number == number)).scalars().first()
                if not entry_case:
                    new_entry_case = models.ChecklistEntryCase(case_number=number, is_correct=is_correct, symbol=symbol, memory_used=memory, time_taken=time, entry_id=entry.id)
                    db.add(new_entry_case)
                    db.commit()
                    db.refresh(new_entry_case)
                else:
                    entry_case.case_number = number
                    entry_case.is_correct = is_correct
                    entry_case.symbol = symbol
                    entry_case.memory_used = memory
                    entry_case.time_taken = time
                    db.commit()
                    db.refresh(entry_case)

                if not is_correct:
                    all_correct = False

            if all_correct:
                entry.status = 3
            else:
                entry.status = 1
            db.commit()
            db.refresh(entry)
        except:
            pass
