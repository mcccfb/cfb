##
# February 22, 2022
#
#

import csv
from datetime import datetime
from datetime import date
import plotly.express as px
import pandas as pd

# read the csv into records

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
        
all_records = []
rownum=0
with open('1971_program_lifespans.csv', 'r') as file:
    reader = csv.reader(file)
    for cur_row in reader:
        rownum += 1
        if (rownum == 1):
            continue
        all_records.append(LifespanRecord(cur_row[0], cur_row[1]))

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


df = pd.DataFrame(gant_array)
fig = px.timeline(df, x_start = "Start", x_end = "Finish", y = "Program", color = "Program")
fig.show()
