##
# February 22, 2022
#
#

import csv
from datetime import datetime
from datetime import date
import plotly.express as px
import pandas as pd
import statistics

class Span:
    def __init__(self, start, end, to_present):
        self.start = start
        self.end = end
        self.to_present = to_present

class LifespanRecord:
    def __init__(self, program_name, raw_spans):
        self.program_name = program_name
        self.raw_spans = raw_spans
        self.spans = []
        self.valid = self.parse_spans()

    def __str__(self):
        kicker = ''
        if (self.valid) :
            kicker = str(len(self.spans)) + " spans"
        else:
            kicker = "INVALID: " + self.raw_spans
        return self.program_name + " " + kicker

    def parse_spans(self):
        txt_spans = self.raw_spans.split("; ")
        for t in txt_spans:
            start_end = t.split("-")
            if (len(start_end) == 1):
                start = start_end[0]
                end = start_end[0]
            elif (len(start_end) == 2):
                start = start_end[0]
                end = start_end[1]
            else:
                return False
            if (not start.isnumeric()):
                return false
            if (not end.isnumeric()):
                if (end != 'present'):
                    return False
                else:
                    self.spans.append(Span(int(start), 0, True))
            else:
                self.spans.append(Span(int(start), int(end), False))
        return True


def total_years(lsrec):
    this_year = date.today().year
    total_years = 0
    for span in lsrec.spans:
        if (span.to_present):
            total_years += (this_year - span.start) + 1
        else:
            total_years += (span.end - span.start) + 1
    return total_years


all_records = []
rownum=0
with open('1971_program_lifespans.csv', 'r') as file:
    reader = csv.reader(file)
    for cur_row in reader:
        rownum += 1
        if (rownum == 1):
            continue
        all_records.append(LifespanRecord(cur_row[0], cur_row[1]))

all_records.sort(key = total_years)

gant_array = []
present_day = datetime.strftime(date.today(), "%Y-%m-%d")
#print(present_day)

for record in all_records:
    if (not record.valid):
        print("Skipping invalid record " + record.program_name)
        continue
    task_count = 0
    for span in record.spans:
        start_str = str(span.start) + "-01-01"
        if (span.to_present):
            end_str = present_day
        else:
            end_str = str(span.end + 1) + "-01-01"
        task_count += 1
        task_name = record.program_name + " " + str(task_count)
        gant_array.append(dict(Task = task_name,
                               Start = start_str,
                               Finish = end_str,
                               Program = record.program_name))


#df = pd.DataFrame(gant_array)
#fig = px.timeline(df, x_start = "Start", x_end = "Finish", y = "Program", color = "Program")
#fig.show()

pre_1971_years = {}
post_1971_years = {}
dead = []
alive = []
this_year = date.today().year
for record in all_records:
    if (not record.valid):
        print("Skipping invalid record " + record.program_name)
        continue
    pre_71 = 0
    post_71 = 0
    currently_alive = False
    for span in record.spans:
        # total up pre-1971 years
        if (span.start < 1971):
            if (span.to_present):
                pre_71 += (1971 - span.start)
                post_71 += (this_year - 1971)
                currently_alive = True
            elif (span.end > 1971):
                pre_71 += (1971 - span.start)
                post_71 += (span.end - 1971) + 1
            else:
                pre_71 += span.end - span.start + 1
        else:
            if (span.to_present):
                post_71 += this_year - 1971 + 1
                currently_alive = True
            else:
                post_71 += span.end - 1971 + 1
    pre_1971_years[record.program_name] = pre_71
    post_1971_years[record.program_name] = post_71
    if (currently_alive):
        alive.append(record.program_name)
    else:
        dead.append(record.program_name)

print(pre_1971_years)
print(alive)
print(dead)

working = []
for team in alive:
    working.append(pre_1971_years[team])
print("mean of live = " + str(statistics.mean(working)))
print("median of live = " + str(statistics.median(working)))

working = []
for team in dead:
    working.append(pre_1971_years[team])
print("mean of dead = " + str(statistics.mean(working)))
print("median of dead = " + str(statistics.median(working)))

scatter_array = []
for team in alive:
    scatter_array.append(dict(Program = team,
                              pre_71 = pre_1971_years[team],
                              post_71 = post_1971_years[team],
                              text = team,
                              Size = 1,
                              alive = True))
for team in dead:
    scatter_array.append(dict(Program = team,
                              pre_71 = pre_1971_years[team],
                              post_71 = post_1971_years[team],
                              text = team,
                              Size = 1,
                              alive = False))

df = pd.DataFrame(scatter_array)
fig = px.scatter(df, y = "pre_71", x = "post_71", color = "alive", \
                 trendline="ols", \
                 size = "Size", \
                 text = "text", \
                 hover_data = {'Program' : False , 'Size' : False, 'alive' : False})
fig.show()

all_predictions = []

# monkey test dyads
total_recs = len(all_records)
count_dyads = 0
count_ties = 0
count_correct = 0
for i in range(0, total_recs):
    for j in range((i + 1), total_recs):
        dyad = [all_records[i].program_name, all_records[j].program_name]
        result = "";
        prediction = ""
        if (pre_1971_years[dyad[0]] > pre_1971_years[dyad[1]]):
            prediction = "A"
        elif (pre_1971_years[dyad[1]] > pre_1971_years[dyad[0]]):
            prediction = "B"
        else:
             prediction = "T" 
                                
        if (post_1971_years[dyad[0]] > post_1971_years[dyad[1]]):
            result = "A"
        elif (post_1971_years[dyad[1]] > post_1971_years[dyad[0]]):
            result = "B"
        else:
            result = "T"
            count_ties += 1
        print("dyad : " + dyad[0] + " vs " + dyad[1] + " prediction: " + prediction + " result: " + result)
        count_dyads += 1
        if (prediction == result):
            count_correct += 1


print("total dyads " + str(count_dyads))
print("total ties " + str(count_ties))
print("total correct predictions " + str(count_correct))

