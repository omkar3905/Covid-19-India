# Note: This script is subject to change, as it relies on the government website https://www.mohfw.gov.in/ for information which in itself is always subject to change

# Importing libraries
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Options_Chrome
from time import sleep
import mysql.connector
import datetime


class Data:
    # Initializing global variables
    def __init__(self):
        self.URL_government = "https://www.mohfw.gov.in/"
        self.URL_org = 'https://www.covid19india.org/'

        # freemysqlhosting.net --> info 

    def parse(self):
        options = Options_Chrome()
        options.headless = True
        requests = webdriver.Chrome(options=options)
        requests.get(self.URL_government)
        sleep(3)
        response = requests.page_source
        requests.quit()
        soup = BeautifulSoup(response, 'html.parser')
        statistics_holder = soup.find('div', {'class':'site-stats-count'})
        statistics_div = statistics_holder.find('ul')
        statistics = statistics_div.find_all('li')

        # India wide stats
        total_airport_checks = 1524267
        total_active_cases = int((statistics[0].find('strong')).text.replace("#", ""))
        total_deaths = int((statistics[2].find('strong')).text.replace("#", ""))
        total_recovered = int((statistics[1].find('strong')).text.replace("#", ""))
        toal_migrated = int((statistics[3].find('strong')).text.replace("#", ""))
        total_hospitalized = "Unavailable"
        total_intensive_care = "Unavailable"

        total_cases = total_active_cases + total_recovered + total_deaths

        # Framing details for each state
        state_names = []
        state_cases = []
        state_deaths = []
        state_recovered = []
        state_upload = []

        # Presenting information
        print("__________As of {}________\n".format(datetime.datetime.now().replace(microsecond=0)))
        
        print("-------Coronavirus in India by state-------")

        try:
            print("\n    Attempting Government state data!")
            # Government state stats
            table_div = soup.find('div', {'class':'table-responsive'})
            table = table_div.find('table')
            rows = table.find_all('tr')[1:-1]
            total_row_holder = table.find_all('tr')[-1]
            total_row_verify = total_row_holder.find_all('td')
            if len(total_row_verify) < 4:
                total_row_holder = table.find_all('tr')[-2]
                rows = table.find_all('tr')[1:-2]
            else:
                rows = table.find_all('tr')[1:-1]
                pass

            for row in rows:
                all_data = row.find_all('td')
                raw_state_name = str(all_data[1].text.replace("#", ""))
                if raw_state_name == "Odisha":
                    state_name = "Orissa"
                elif raw_state_name == "Uttarakhand":
                    state_name = "IN-UT"
                else:
                    state_name = raw_state_name                

                state_case = int(all_data[2].text.replace("#", ""))
                state_death = int(all_data[4].text.replace("#", ""))
                state_recover = int(all_data[3].text.replace("#", ""))

                print("{}: ".format(state_name))
                print("    Cases: {}".format(state_case))
                print("    Deaths: {}".format(state_death))
                print("    Recovered: {}".format(state_recover))

                # Updating details for each state
                state_names.append(state_name)
                state_cases.append(state_case)
                state_deaths.append(state_death)
                state_recovered.append(state_recover)

            for i in range(len(state_names)):
                state_upload.append((state_names[i], state_cases[i], state_deaths[i], state_recovered[i]))

            result_info = 'gov'

            print("\n    Used government state data!")

        except:
            # Clearing lists if government does not work
            state_upload.clear()
            state_names.clear()
            state_cases.clear()
            state_deaths.clear()
            state_recovered.clear()
            state_upload.clear()

            print("\n    Government state data unavailable, attempting covid19india.org instead!")
            # https://www.covid19india.org/ state stats
            options = Options_Chrome()
            options.headless = True
            requests = webdriver.Chrome(options=options)
            requests.get(self.URL_org)
            sleep(4)
            html = requests.page_source
            requests.quit()

            soup = BeautifulSoup(html, 'html.parser')

            table_div = soup.find('table', {'class':'table'})
            row_holders = soup.find_all('tr', {'class':'state'})[:-1]
            #print(row_holders)

            rows = []
            for tbody in row_holders:
                actual_row = tbody
                rows.append(actual_row)
            
            for row in rows:
                all_data = row.find_all('td')
                state_name = str(all_data[0].text.replace("-", "0"))

                # Deducting the daily increase value, and getting totals only
                if len(all_data[1]) > 1:
                    all_data[1].find('span').decompose()
                    state_case = int(all_data[1].text.replace("-", "0"))
                else:
                    state_case = int(all_data[1].text.replace("-", "0"))

                if len(all_data[4]) > 1:
                    all_data[4].find('span').decompose()
                    state_death = int(all_data[4].text.replace("-", "0"))
                else:
                    state_death = int(all_data[4].text.replace("-", "0"))

                if len(all_data[3]) > 1:
                    all_data[3].find('span').decompose()
                    state_recover = int(all_data[3].text.replace("-", "0"))
                else:
                    state_recover = int(all_data[3].text.replace("-", "0"))

                print("{}: ".format(state_name))
                print("    Cases: {}".format(state_case))
                print("    Deaths: {}".format(state_death))
                print("    Recovered: {}".format(state_recover))

                # Updating details for each state
                state_names.append(state_name)
                state_cases.append(state_case)
                state_deaths.append(state_death)
                state_recovered.append(state_recover)

            for i in range(len(state_names)):
                state_upload.append((state_names[i], state_cases[i], state_deaths[i], state_recovered[i]))
            
            print("\n    Used state data from covid19india.org!")


        print("------------India wide statistics----------")
        print("Total cases: {}".format(total_cases))
        print("Total deaths: {}".format(str(total_deaths)))
        print("Total hospitalized cases: {}".format(total_hospitalized))
        print("Total individuals screened at airport: {}".format(total_airport_checks))
        print("Total in intensive care: {}".format(total_intensive_care))
        print("Total recovered: {}".format(total_recovered))

        result_info = 'org'

        # Returning results
        return total_cases, total_deaths, total_airport_checks, None, total_recovered, state_upload, result_info

    def upload_data(self):
        mydb = mysql.connector.connect(host=self.host, user=self.user, passwd=self.passwd, database=self.database_name)
        print(mydb)
        cursor = mydb.cursor()

        # Emptying table before upload
        #cursor.execute("TRUNCATE TABLE india_wide")        
        
        parse_data = self.parse()
        current_time = str(datetime.datetime.now().replace(microsecond=0))  
        
        # Uploading the India wide stats
        formula_india_world = "INSERT INTO india_wide (Date, Cases, Deaths, Screened, Recovered) VALUES (%s, %s, %s, %s, %s)"
        upload_india = (current_time, parse_data[0], parse_data[1], parse_data[2], parse_data[4])
            
        cursor.execute(formula_india_world, upload_india)
        
        # Uploading data for line graph
        formula_trend = "INSERT INTO trend (Date, Cases, Deaths, Recovered) VALUES (%s, %s, %s, %s)"
        current_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        upload_trend = (current_date, parse_data[0], parse_data[1], parse_data[4])

        # Updating duplicates if existing
        try:
            cursor.execute("DELETE FROM trend WHERE (Date = '{}')".format(current_date))
        except:
            pass
        cursor.execute(formula_trend, upload_trend)
        
        # Uploading state wise stats
        for data in parse_data[-2]:
            try:
                cursor.execute("DELETE FROM state_wise WHERE (State = '{}')".format(str(data[0])))
            except:
                pass

        formula_states = "INSERT INTO state_wise (State, Cases, Deaths, Recovered) VALUES (%s, %s, %s, %s)"
        cursor.executemany(formula_states, parse_data[-2])
    
        mydb.commit()
        mydb.disconnect()

    def run(self):
        while True:
            #"""
            try:
                self.upload_data()
                print("{} --> All sets of of covid19 data succesfully uploaded!".format(datetime.datetime.now().replace(microsecond=0)))
            except:
                print("{} --> Problem occured while uploading data!".format(datetime.datetime.now().replace(microsecond=0)))
            #"""
            #self.upload_data()
            sleep(3600)

Data().run()
