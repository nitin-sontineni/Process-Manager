import threading
import time
import random
import os
import psutil
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import timeunit
import glob

class PreemptiveScheduler:
    def __init__(self, time_slice=0.5):
        self.threads = []
        self.time_slice = time_slice
        self.current = 0
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.active = True
        self.start_time = None
        self.process = psutil.Process(os.getpid())
        self.completion_times = {}  # Store completion times of threads

    def add_thread(self, target, args):
        thread = threading.Thread(target=self.run_thread, args=(target, args))
        self.threads.append(thread)

    def run_thread(self, target, args):
        thread_index = self.threads.index(threading.current_thread())
        start_time = time.time()  # Record start time
        while self.active:
            with self.condition:
                while self.current != thread_index and self.active:
                    self.condition.wait()
                if not self.active:
                    break

                #print(f"Thread {thread_index} starts running at {time.ctime()}.")
                task_start_time = time.time()

                # Allow thread to run for its time slice or until stopped
                target(*args)

                task_duration = time.time() - task_start_time
                #print(f"Thread {thread_index} stops running at {time.ctime()}. Task Duration: {task_duration:.4f} seconds.")

                self.current = (self.current + 1) % len(self.threads)
                self.condition.notify_all()

        completion_time = time.time() - start_time  # Calculate completion time
        self.completion_times[thread_index] = completion_time

    def start(self):
        self.start_time = time.time()
        for thread in self.threads:
            thread.start()

    def join(self):
        for thread in self.threads:
            thread.join()
        total_duration = time.time() - self.start_time
        print(f"Total execution time: {total_duration:.4f} seconds")
        print(f"CPU Usage during execution: {self.process.cpu_percent()}%")

        # Calculate and print turnaround time for each thread
        for i, completion_time in self.completion_times.items():
            turnaround_time = completion_time
            print(f"Turnaround time for Thread {i}: {turnaround_time:.4f} seconds")

        # Calculate throughput
        throughput = len(self.threads) / total_duration
        print(f"Throughput: {throughput:.4f} threads/second")

        # Calculate CPU utilization
        cpu_utilization = (self.process.cpu_percent() / psutil.cpu_count())
        print(f"CPU Utilization: {cpu_utilization:.2f}%")

        # Calculate waiting time (assuming all threads start simultaneously)
        waiting_time = total_duration - sum(self.completion_times.values())
        print(f"Waiting time: {waiting_time:.4f} seconds")

    def stop(self):
        with self.lock:
            self.active = False
            self.condition.notify_all()
            


def computation_task():
    result = 0
    for _ in range(1000000):  # Increase iterations
        result += random.randint(1, 1000)  # Increase range
    print("Computation task completed.")

def io_task(filename):
    with open(filename, "a") as file:
        file.write(f"Log entry at {time.ctime()}\n")
    #print("I/O task completed.")

def data_processing_task(data):
    print("in data")
    data.sort()

def network_task():
    response = requests.get("https://www.usenix.org/system/files/conference/atc18/atc18-bouron.pdf")
    print("Network task completed.")
    #print(response)

def image_processing_task(image_path):
    image = Image.open(image_path)
    # Perform image processing operations here
    # For demonstration, let's rotate the image
    rotated_image = image.rotate(90)
    rotated_image.save("rotated_image.jpg")
    print("Image processing task completed.")

def embarrassingly_parallel_task(scheduler, num_threads):
    def parallel_computation():
        count = 0
        for _ in range(1000000 // num_threads):  # Divide workload among threads
            x = random.random()
            y = random.random()
            if x * y <= 0.5:  # Example condition
                count += 1
        print(f"Embarrassingly parallel task completed by Thread {threading.current_thread().name}.")

    for i in range(num_threads):
        scheduler.add_thread(target=parallel_computation, args=())
        
        
def scrape(airline_codes, airportCodes):

    current_thread = threading.current_thread()
    print(f"Thread Name: {current_thread.name}")
    print(f"Thread ID: {current_thread.ident}")
    print(f"Is Daemon: {current_thread.daemon}")
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1366,768")
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("enable-automation")
    chrome_options.add_argument("--disable-browser-side-navigation")
    #chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.transtats.bts.gov/ONTIME/Departures.aspx")


    # Create a Select object from the dropdown element


    # Get the list of options in the dropdown
 

    fileNames = []

    for airlineCode in airline_codes:
        for airportCode in airportCodes:
            try:
                dropdown = driver.find_element(By.CSS_SELECTOR, "#cboAirline")
                select = Select(dropdown)
                options = select.options
                dropdownA = driver.find_element(By.CSS_SELECTOR, "#cboAirport")
                selectA = Select(dropdownA)
                optionsA = selectA.options
                # Select the option in the dropdown
                checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'][id='chkAllMonths']")
                if not checkbox.is_selected():
                        checkbox.click()

                checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'][id='chkAllStatistics']")
                if not checkbox.is_selected():
                        checkbox.click()

                checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'][id='chkAllDays']")
                if not checkbox.is_selected():
                        checkbox.click()

                checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'][id='chkAllYears']")
                if not checkbox.is_selected():
                        checkbox.click()

                select.select_by_visible_text(airlineCode)
                selectA.select_by_visible_text(airportCode)
                button = driver.find_element(By.NAME, "btnSubmit")
                button.click()

                wait = WebDriverWait(driver, 1.2)
            except:
                continue

            # Try to find the element on the page
            try:
                print(airlineCode, airportCode)
                element = wait.until(lambda driver: driver.find_element(By.ID, "DL_CSV"))
                print("Download link found")
                file_name = airlineCode + airportCode[:39] + ".csv"
                file_name = file_name.replace(":","")
                file_name = file_name.replace("/","")
                fileNames.append(file_name)
                element.click()
                # Wait for the file to download


            except:
                continue

        files = glob.glob("/home/nitin/Downloads" + '/*')
        files.sort(key=os.path.getmtime)
        files = files[len(files)-len(fileNames):]
        print(fileNames)
        #fileNames = fileNames[::-1]
        #files = files[:len(fileNames)]
        i = 0
        while i < len(fileNames):
                most_recent_file = files[0]
                os.rename(most_recent_file, "/home/nitin/Downloads" + fileNames[i])
                del files[0]
                i += 1
                print(fileNames[i-1] + " renamed")
        fileNames = []
        
        

def main():

	airline_codes = [
		'ExpressJet Airlines Inc. (XE)',
		'ExpressJet Airlines LLC (EV)',
		'Frontier Airlines Inc. (F9)',
		'Hawaiian Airlines Inc. (HA)',
		'Horizon Air (QX)',
		'Independence Air (DH)',
		'JetBlue Airways (B6)']

	airportCodes = [
	"Aberdeen, SD: Aberdeen Regional (ABR)",
	"Abilene, TX: Abilene Regional (ABI)",
	"Adak Island, AK: Adak (ADK)",
	"Aguadilla, PR: Rafael Hernandez (BQN)",
	"Akron, OH: Akron-Canton Regional (CAK)",
	"Alamosa, CO: San Luis Valley Regional/Bergman Field (ALS)",
	"Albany, GA: Southwest Georgia Regional (ABY)",
	"Albany, NY: Albany International (ALB)",
	"Albuquerque, NM: Albuquerque International Sunport (ABQ)",
	"Alexandria, LA: Alexandria International (AEX)",
	"Allentown/Bethlehem/Easton, PA: Lehigh Valley International (ABE)",
	"Alpena, MI: Alpena County Regional (APN)",
	"Amarillo, TX: Rick Husband Amarillo International (AMA)",
	"Anchorage, AK: Ted Stevens Anchorage International (ANC)",
	"Aniak, AK: Aniak Airport (ANI)",
	"Appleton, WI: Appleton International (ATW)",
	"Arcata/Eureka, CA: California Redwood Coast Humboldt County (ACV)",
	"Asheville, NC: Asheville Regional (AVL)",
	"Ashland, WV: Tri-State/Milton J. Ferguson Field (HTS)",
	"Aspen, CO: Aspen Pitkin County Sardy Field (ASE)",
	"Atlanta, GA: Hartsfield-Jackson Atlanta International (ATL)",
	"Atlantic City, NJ: Atlantic City International (ACY)",
	"Augusta, GA: Augusta Regional at Bush Field (AGS)",
	"Austin, TX: Austin - Bergstrom International (AUS)",
	"Austin, TX: Robert Mueller Municipal (AUS)",
	"Bakersfield, CA: Meadows Field (BFL)",
	"Baltimore, MD: Baltimore/Washington International Thurgood Marshall (BWI)",
	"Bangor, ME: Bangor International (BGR)",
	"Barrow, AK: Wiley Post/Will Rogers Memorial (BRW)",
	"Baton Rouge, LA: Baton Rouge Metropolitan/Ryan Field (BTR)",
	"Beaumont/Port Arthur, TX: Jack Brooks Regional (BPT)",
	"Belleville, IL: Scott AFB MidAmerica St Louis (BLV)",
	"Belleville, IL: Scott AFB/MidAmerica (BLV)",
	"Bellingham, WA: Bellingham International (BLI)",
	"Bemidji, MN: Bemidji Regional (BJI)",
	"Bend/Redmond, OR: Roberts Field (RDM)",
	"Bethel, AK: Bethel Airport (BET)",
	"Billings, MT: Billings Logan International (BIL)",
	"Binghamton, NY: Greater Binghamton/Edwin A. Link Field (BGM)",
	"Birmingham, AL: Birmingham-Shuttlesworth International (BHM)",
	"Bishop, CA: Bishop Airport (BIH)",
	"Bismarck/Mandan, ND: Bismarck Municipal (BIS)",
	"Bloomington/Normal, IL: Central Il Regional Airport at Bloomington (BMI)",
	"Boise, ID: Boise Air Terminal (BOI)",
	"Boston, MA: Logan International (BOS)",
	"Bozeman, MT: Bozeman Yellowstone International (BZN)",
	"Brainerd, MN: Brainerd Lakes Regional (BRD)",
	"Branson, MO: Branson Airport (BKG)",
	"Bristol/Johnson City/Kingsport, TN: Tri Cities (TRI)",
	"Brownsville, TX: Brownsville South Padre Island International (BRO)",
	"Brunswick, GA: Brunswick Golden Isles (BQK)",
	"Buffalo, NY: Buffalo Niagara International (BUF)",
	"Bullhead City, AZ: Laughlin/Bullhead International (IFP)",
	"Burbank, CA: Bob Hope (BUR)",
	"Burlington, VT: Burlington International (BTV)",
	"Butte, MT: Bert Mooney (BTM)",
	"Cape Girardeau, MO: Cape Girardeau Regional (CGI)",
	"Carlsbad, CA: McClellan-Palomar (CLD)",
	"Casper, WY: Casper/Natrona County International (CPR)",
	"Cedar City, UT: Cedar City Regional (CDC)",
	"Cedar Rapids/Iowa City, IA: The Eastern Iowa (CID)",
	"Champaign/Urbana, IL: University of Illinois/Willard (CMI)",
	"Charleston, SC: Charleston AFB/International (CHS)",
	"Charleston/Dunbar, WV: West Virginia International Yeager (CRW)",
	"Charleston/Dunbar, WV: Yeager (CRW)",
	"Charlotte Amalie, VI: Cyril E King (STT)",
	"Charlotte, NC: Charlotte Douglas International (CLT)",
	"Charlottesville, VA: Charlottesville Albemarle (CHO)",
	"Chattanooga, TN: Lovell Field (CHA)",
	"Cheyenne, WY: Cheyenne Regional/Jerry Olson Field (CYS)",
	"Chicago, IL: Chicago Midway International (MDW)",
	"Chicago, IL: Chicago O'Hare International (ORD)",
	"Chico, CA: Chico Municipal (CIC)",
	"Christiansted, VI: Henry E. Rohlsen (STX)",
	"Cincinnati, OH: Cincinnati/Northern Kentucky International (CVG)",
	"Clarksburg/Fairmont, WV: North Central West Virginia (CKB)",
	"Cleveland, OH: Cleveland-Hopkins International (CLE)",
	"Cody, WY: Yellowstone Regional (COD)",
	"Cold Bay, AK: Cold Bay Airport (CDB)",
	"College Station/Bryan, TX: Easterwood Field (CLL)",
	"Colorado Springs, CO: City of Colorado Springs Municipal (COS)",
	"Columbia, MO: Columbia Regional (COU)",
	"Columbia, SC: Columbia Metropolitan (CAE)",
	"Columbus, GA: Columbus Airport (CSG)",
	"Columbus, MS: Columbus AFB (CBM)",
	"Columbus, MS: Golden Triangle Regional (GTR)",
	"Columbus, OH: John Glenn Columbus International (CMH)",
	"Columbus, OH: Rickenbacker International (LCK)",
	"Concord, CA: Buchanan Field (CCR)",
	"Concord, NC: Concord Padgett Regional (USA)",
	"Cordova, AK: Merle K Mudhole Smith (CDV)",
	"Corpus Christi, TX: Corpus Christi International (CRP)",
	"Crescent City, CA: Jack McNamara Field (CEC)",
	"Dallas, TX: Dallas Love Field (DAL)",
	"Dallas/Fort Worth, TX: Dallas/Fort Worth International (DFW)",
	"Dayton, OH: James M Cox/Dayton International (DAY)",
	"Daytona Beach, FL: Daytona Beach International (DAB)",
	"Deadhorse, AK: Deadhorse Airport (SCC)",
	"Decatur, IL: Decatur Airport (DEC)",
	"Del Rio, TX: Del Rio International (DRT)",
	"Denver, CO: Denver International (DEN)",
	"Des Moines, IA: Des Moines International (DSM)",
	"Detroit, MI: Coleman A. Young Municipal (DET)",
	"Detroit, MI: Detroit Metro Wayne County (DTW)",
	"Devils Lake, ND: Devils Lake Regional (DVL)",
	"Dickinson, ND: Dickinson - Theodore Roosevelt Regional (DIK)",
	"Dillingham, AK: Dillingham Airport (DLG)",
	"Dodge City, KS: Dodge City Regional (DDC)",
	"Dothan, AL: Dothan Regional (DHN)",
	"Dubuque, IA: Dubuque Regional (DBQ)",
	"Duluth, MN: Duluth International (DLH)",
	"Durango, CO: Durango La Plata County (DRO)",
	"Eagle, CO: Eagle County Regional (EGE)",
	"Eau Claire, WI: Chippewa Valley Regional (EAU)",
	"El Centro, CA: Imperial County (IPL)",
	"El Paso, TX: El Paso International (ELP)",
	"Elko, NV: Elko Regional (EKO)",
	"Elmira/Corning, NY: Elmira/Corning Regional (ELM)",
	"Erie, PA: Erie International/Tom Ridge Field (ERI)",
	"Escanaba, MI: Delta County (ESC)",
	"Eugene, OR: Mahlon Sweet Field (EUG)",
	"Evansville, IN: Evansville Regional (EVV)",
	"Everett, WA: Snohomish County (PAE)",
	"Fairbanks, AK: Fairbanks International (FAI)",
	"Fargo, ND: Hector International (FAR)",
	"Farmington, NM: Four Corners Regional (FMN)",
	"Fayetteville, AR: Northwest Arkansas National (XNA)",
	"Fayetteville, AR: Northwest Arkansas Regional (XNA)",
	"Fayetteville, NC: Fayetteville Regional/Grannis Field (FAY)",
	"Flagstaff, AZ: Flagstaff Pulliam (FLG)",
	"Flint, MI: Bishop International (FNT)",
	"Florence, SC: Florence Regional (FLO)",
	"Fort Collins/Loveland, CO: Northern Colorado Regional (FNL)",
	"Fort Dodge, IA: Fort Dodge Regional (FOD)",
	"Fort Lauderdale, FL: Fort Lauderdale-Hollywood International (FLL)",
	"Fort Leonard Wood, MO: Waynesville-St. Robert Regional Forney Field (TBN)",
	"Fort Myers, FL: Southwest Florida International (RSW)",
	"Fort Smith, AR: Fort Smith Regional (FSM)",
	"Fort Wayne, IN: Fort Wayne International (FWA)",
	"Fresno, CA: Fresno Yosemite International (FAT)",
	"Gainesville, FL: Gainesville Regional (GNV)",
	"Garden City, KS: Garden City Regional (GCK)",
	"Gillette, WY: Gillette Campbell County (GCC)",
	"Gillette, WY: Northeast Wyoming Regional (GCC)",
	"Grand Canyon, AZ: Grand Canyon National Park (GCN)",
	"Grand Forks, ND: Grand Forks International (GFK)",
	"Grand Island, NE: Central Nebraska Regional (GRI)",
	"Grand Junction, CO: Grand Junction Regional (GJT)",
	"Grand Rapids, MI: Gerald R. Ford International (GRR)",
	"Great Falls, MT: Great Falls International (GTF)",
	"Green Bay, WI: Green Bay Austin Straubel International (GRB)",
	"Greensboro/High Point, NC: Piedmont Triad International (GSO)",
	"Greenville, MS: Greenville Mid Delta (GLH)",
	"Greenville, NC: Pitt Greenville (PGV)",
	"Greer, SC: Greenville-Spartanburg International (GSP)",
	"Guam, TT: Guam International (GUM)",
        "Gulfport/Biloxi, MS: Gulfport-Biloxi International (GPT)",
        "Gunnison, CO: Gunnison-Crested Butte Regional (GUC)",
        "Gustavus, AK: Gustavus Airport (GST)",
        "Hagerstown, MD: Hagerstown Regional-Richard A. Henson Field (HGR)",
        "Hancock/Houghton, MI: Houghton County Memorial (CMX)",
        "Harlingen/San Benito, TX: Valley International (HRL)",
        "Harrisburg, PA: Harrisburg International (MDT)",
        "Hartford, CT: Bradley International (BDL)",
        "Hattiesburg/Laurel, MS: Hattiesburg-Laurel Regional (PIB)",
        "Hayden, CO: Yampa Valley (HDN)",
        "Hays, KS: Hays Regional (HYS)",
        "Helena, MT: Helena Regional (HLN)",
        "Hibbing, MN: Range Regional (HIB)",
        "Hickory, NC: Hickory Regional (HKY)",
        "Hilo, HI: Hilo International (ITO)",
        "Hilton Head, SC: Hilton Head Airport (HHH)",
        "Hobbs, NM: Lea County Regional (HOB)",
        "Honolulu, HI: Daniel K Inouye International (HNL)",
        "Hoolehua, HI: Molokai (MKK)",
        "Houston, TX: Ellington (EFD)",
        "Houston, TX: George Bush Intercontinental/Houston (IAH)",
        "Houston, TX: William P Hobby (HOU)",
        "Huntsville, AL: Huntsville International-Carl T Jones Field (HSV)",
        "Hyannis, MA: Barnstable Municipal-Boardman/Polando Field (HYA)",
        "Hyannis, MA: Cape Cod Gateway (HYA)",
        "Idaho Falls, ID: Idaho Falls Regional (IDA)",
        "Indianapolis, IN: Indianapolis International (IND)",
        "International Falls, MN: Falls International Einarson Field (INL)",
        "Inyokern, CA: Inyokern Airport (IYK)",
        "Iron Mountain/Kingsfd, MI: Ford (IMT)",
        "Islip, NY: Long Island MacArthur (ISP)",
        "Ithaca/Cortland, NY: Ithaca Tompkins International (ITH)",
        "Ithaca/Cortland, NY: Ithaca Tompkins Regional (ITH)",
        "Jackson, WY: Jackson Hole (JAC)",
        "Jackson/Vicksburg, MS: Jackson Medgar Wiley Evers International (JAN)",
        "Jacksonville, FL: Jacksonville International (JAX)",
        "Jacksonville/Camp Lejeune, NC: Albert J Ellis (OAJ)",
        "Jamestown, ND: Jamestown Regional (JMS)",
        "Johnstown, PA: John Murtha Johnstown-Cambria County (JST)",
        "Joplin, MO: Joplin Regional (JLN)",
        "Juneau, AK: Juneau International (JNU)",
        "Kahului, HI: Kahului Airport (OGG)",
        "Kalamazoo, MI: Kalamazoo/Battle Creek International (AZO)",
        "Kalispell, MT: Glacier Park International (FCA)",
        "Kansas City, MO: Charles B. Wheeler Downtown (MKC)",
        "Kansas City, MO: Kansas City International (MCI)",
        "Kearney, NE: Kearney Regional (EAR)",
        "Ketchikan, AK: Ketchikan International (KTN)",
        "Key West, FL: Key West International (EYW)",
        "Killeen, TX: Robert Gray AAF (GRK)",
        "Killeen, TX: Skylark Field (ILE)",
        "King Salmon, AK: King Salmon Airport (AKN)",
        "Kinston, NC: Kinston Regional Jetport at Stallings Field (ISO)",
        "Klamath Falls, OR: Crater Lake Klamath Regional (LMT)",
        "Knoxville, TN: McGhee Tyson (TYS)",
        "Kodiak, AK: Kodiak Airport (ADQ)",
        "Kona, HI: Ellison Onizuka Kona International at Keahole (KOA)",
        "Koror, Palau: Babelthuap (ROR)",
        "Kotzebue, AK: Ralph Wien Memorial (OTZ)",
        "La Crosse, WI: La Crosse Regional (LSE)",
        "Lafayette, LA: Lafayette Regional Paul Fournet Field (LFT)",
        "Lake Charles, LA: Lake Charles Regional (LCH)",
        "Lake Tahoe, CA: Lake Tahoe Airport (TVL)",
        "Lanai, HI: Lanai Airport (LNY)",
        "Lansing, MI: Capital Region International (LAN)",
        "Laramie, WY: Laramie Regional (LAR)",
        "Laredo, TX: Laredo International (LRD)",
        "Las Vegas, NV: Harry Reid International (LAS)",
        "Las Vegas, NV: McCarran International (LAS)",
        "Latrobe, PA: Arnold Palmer Regional (LBE)",
        "Lawton/Fort Sill, OK: Lawton-Fort Sill Regional (LAW)",
        "Lewisburg, WV: Greenbrier Valley (LWB)",
        "Lewiston, ID: Lewiston Nez Perce County (LWS)",
        "Lexington, KY: Blue Grass (LEX)",
        "Liberal, KS: Liberal Mid-America Regional (LBL)",
        "Lihue, HI: Lihue Airport (LIH)",
        "Lincoln, NE: Lincoln Airport (LNK)",
        "Little Rock, AR: Bill and Hillary Clinton Nat Adams Field (LIT)",
        "Long Beach, CA: Long Beach Airport (LGB)",
        "Longview, TX: East Texas Regional (GGG)",
        "Los Angeles, CA: Los Angeles International (LAX)",
        "Louisville, KY: Louisville Muhammad Ali International (SDF)",
        "Lubbock, TX: Lubbock Preston Smith International (LBB)",
        "Lynchburg, VA: Lynchburg Regional/Preston Glenn Field (LYH)",
        "Macon, GA: Middle Georgia Regional (MCN)",
        "Madison, WI: Dane County Regional-Truax Field (MSN)",
        "Mammoth Lakes, CA: Mammoth Lakes Airport (MMH)",
        "Manchester, NH: Manchester Boston Regional (MHT)",
        "Manchester, NH: Manchester-Boston Regional (MHT)",
        "Manhattan/Ft. Riley, KS: Manhattan Regional (MHK)",
        "Marathon, FL: The Florida Keys Marathon International (MTH)",
        "Marquette, MI: Marquette Sawyer Regional (MQT)",
        "Marquette, MI: Sawyer International (MQT)",
        "Martha's Vineyard, MA: Martha's Vineyard Airport (MVY)",
        "Mason City, IA: Mason City Municipal (MCW)",
        "Mayaguez, PR: Eugenio Maria de Hostos (MAZ)",
        "Medford, OR: Rogue Valley International - Medford (MFR)",
        "Melbourne, FL: Melbourne International (MLB)",
        "Melbourne, FL: Melbourne Orlando International (MLB)",
        "Memphis, TN: Memphis International (MEM)",
        "Meridian, MS: Key Field (MEI)",
        "Miami, FL: Miami International (MIA)",
        "Midland/Odessa, TX: Midland International Air and Space Port (MAF)",
        "Milwaukee, WI: General Mitchell International (MKE)",
        "Minneapolis, MN: Minneapolis-St Paul International (MSP)",
        "Minot, ND: Minot AFB (MIB)",
        "Minot, ND: Minot International (MOT)",
        "Mission/McAllen/Edinburg, TX: McAllen International (MFE)",
        "Missoula, MT: Missoula International (MSO)",
        "Missoula, MT: Missoula Montana (MSO)",
        "Moab, UT: Canyonlands Field (CNY)",
        "Moab, UT: Canyonlands Regional (CNY)",
        "Mobile, AL: Mobile Downtown (BFM)",
        "Mobile, AL: Mobile International (BFM)",
        "Mobile, AL: Mobile Regional (MOB)",
        "Modesto, CA: Modesto City-County-Harry Sham Field (MOD)",
        "Moline, IL: Quad Cities International (MLI)",
        "Moline, IL: Quad City International (MLI)",
        "Monroe, LA: Monroe Regional (MLU)",
        "Monterey, CA: Monterey Regional (MRY)",
        "Montgomery, AL: Montgomery Regional (MGM)",
        "Montrose/Delta, CO: Montrose Regional (MTJ)",
        "Moses Lake, WA: Grant County International (MWH)",
        "Mosinee, WI: Central Wisconsin (CWA)",
        "Muskegon, MI: Muskegon County (MKG)",
        "Myrtle Beach, SC: Myrtle Beach International (MYR)",
        "Nantucket, MA: Nantucket Memorial (ACK)",
        "Naples, FL: Naples Municipal (APF)",
        "Nashville, TN: Nashville International (BNA)",
        "New Bern/Morehead/Beaufort, NC: Coastal Carolina Regional (EWN)",
        "New Haven, CT: Tweed New Haven (HVN)",
        "New Orleans, LA: Louis Armstrong New Orleans International (MSY)",
        "New York, NY: John F. Kennedy International (JFK)",
        "New York, NY: LaGuardia (LGA)",
        "Newark, NJ: Newark Liberty International (EWR)",
        "Newburgh/Poughkeepsie, NY: New York Stewart International (SWF)",
        "Newport News/Williamsburg, VA: Newport News/Williamsburg International (PHF)",
        "Niagara Falls, NY: Niagara Falls International (IAG)",
        "Nome, AK: Nome Airport (OME)",
        "Norfolk, VA: Norfolk International (ORF)",
        "North Bend/Coos Bay, OR: Southwest Oregon Regional (OTH)",
        "North Platte, NE: North Platte Regional Airport Lee Bird Field (LBF)",
        "Oakland, CA: Metropolitan Oakland International (OAK)",
        "Ogden, UT: Ogden-Hinckley (OGD)",
        "Ogdensburg, NY: Ogdensburg International (OGS)",
        "Oklahoma City, OK: Will Rogers World (OKC)",
        "Omaha, NE: Eppley Airfield (OMA)",
        "Ontario, CA: Ontario International (ONT)",
        "Orlando, FL: Orlando International (MCO)",
        "Owensboro, KY: Owensboro Daviess County Regional (OWB)",
        "Oxnard/Ventura, CA: Oxnard (OXR)",
        "Paducah, KY: Barkley Regional (PAH)",
        "Pago Pago, TT: Pago Pago International (PPG)",
        "Palm Springs, CA: Palm Springs International (PSP)",
        "Palmdale, CA: Palmdale USAF Plant 42 (PMD)",
        "Panama City, FL: Bay County (PFN)",
        "Panama City, FL: Northwest Florida Beaches International (ECP)",
        "Pasco/Kennewick/Richland, WA: Tri Cities (PSC)",
        "Pellston, MI: Pellston Regional Airport of Emmet County (PLN)",
        "Pensacola, FL: Pensacola International (PNS)",
        "Peoria, IL: General Downing - Peoria International (PIA)",
        "Petersburg, AK: Petersburg James A Johnson (PSG)",
        "Philadelphia, PA: Philadelphia International (PHL)",
        "Phoenix, AZ: Phoenix - Mesa Gateway (AZA)",
        "Phoenix, AZ: Phoenix Sky Harbor International (PHX)",
        "Pierre, SD: Pierre Regional (PIR)",
        "Pinehurst/Southern Pines, NC: Moore County (SOP)",
        "Pittsburgh, PA: Pittsburgh International (PIT)",
        "Plattsburgh, NY: Plattsburgh International (PBG)",
        "Pocatello, ID: Pocatello Regional (PIH)",
        "Ponce, PR: Mercedita (PSE)",
        "Portland, ME: Portland International Jetport (PWM)",
        "Portland, OR: Portland International (PDX)",
        "Portsmouth, NH: Portsmouth International at Pease (PSM)",
        "Prescott, AZ: Prescott Regional Ernest A Love Field (PRC)",
        "Providence, RI: Rhode Island Tf Green International (PVD)",
        "Providence, RI: Theodore Francis Green State (PVD)",
        "Provo, UT: Provo Municipal (PVU)",
        "Pueblo, CO: Pueblo Memorial (PUB)",
        "Pullman, WA: Pullman Moscow Regional (PUW)",
        "Punta Gorda, FL: Punta Gorda Airport (PGD)",
        "Quincy, IL: Quincy Regional-Baldwin Field (UIN)",
        "Raleigh/Durham, NC: Raleigh-Durham International (RDU)",
        "Rapid City, SD: Ellsworth AFB (RCA)",
        "Rapid City, SD: Rapid City Regional (RAP)",
        "Red River, ND: Grand Forks AFB (RDR)",
        "Redding, CA: Redding Municipal (RDD)",
        "Redding, CA: Redding Regional (RDD)",
        "Reno, NV: Reno/Tahoe International (RNO)",
        "Rhinelander, WI: Rhinelander/Oneida County (RHI)",
        "Richmond, VA: Richmond International (RIC)",
        "Riverton/Lander, WY: Central Wyoming Regional (RIW)",
        "Riverton/Lander, WY: Riverton Regional (RIW)",
        "Roanoke, VA: Roanoke Blacksburg Regional (ROA)",
        "Rochester, MN: Rochester International (RST)",
        "Rochester, NY: Frederick Douglass Grtr Rochester International (ROC)",
        "Rochester, NY: Greater Rochester International (ROC)",
        "Rock Springs, WY: Southwest Wyoming Regional (RKS)",
        "Rockford, IL: Chicago/Rockford International (RFD)",
        "Roswell, NM: Roswell Air Center (ROW)",
        "Roswell, NM: Roswell International Air Center (ROW)",
        "Rota, TT: Benjamin Taisacan Manglona International (ROP)",
        "Sacramento, CA: Sacramento International (SMF)",
        "Saginaw/Bay City/Midland, MI: MBS International (MBS)",
        "Saipan, TT: Francisco C. Ada Saipan International (SPN)",
        "Salem, OR: McNary Field (SLE)",
        "Salina, KS: Salina Regional (SLN)",
        "Salt Lake City, UT: Salt Lake City International (SLC)",
        "San Angelo, TX: San Angelo Regional/Mathis Field (SJT)",
        "San Antonio, TX: San Antonio International (SAT)",
        "San Diego, CA: San Diego International (SAN)",
        "San Francisco, CA: San Francisco International (SFO)",
        "San Jose, CA: Norman Y. Mineta San Jose International (SJC)",
        "San Juan, PR: Luis Munoz Marin International (SJU)",
        "San Luis Obispo, CA: San Luis County Regional (SBP)",
        "Sanford, FL: Orlando Sanford International (SFB)",
        "Santa Ana, CA: John Wayne Airport-Orange County (SNA)",
        "Santa Barbara, CA: Santa Barbara Municipal (SBA)",
        "Santa Fe, NM: Santa Fe Municipal (SAF)",
        "Santa Maria, CA: Santa Maria Public/Capt. G. Allan Hancock Field (SMX)",
        "Santa Rosa, CA: Charles M. Schulz - Sonoma County (STS)",
        "Sarasota/Bradenton, FL: Sarasota/Bradenton International (SRQ)",
        "Sault Ste. Marie, MI: Chippewa County International (CIU)",
        "Savannah, GA: Savannah/Hilton Head International (SAV)",
        "Scottsbluff, NE: Western Neb. Regional/William B. Heilig Field (BFF)",
        "Scranton/Wilkes-Barre, PA: Wilkes Barre Scranton International (AVP)",
        "Seattle, WA: Boeing Field/King County International (BFI)",
        "Seattle, WA: Seattle/Tacoma International (SEA)",
        "Sheridan, WY: Sheridan County (SHR)",
        "Shreveport, LA: Shreveport Regional (SHV)",
        "Sioux City, IA: Sioux Gateway Brig Gen Bud Day Field (SUX)",
        "Sioux Falls, SD: Joe Foss Field (FSD)",
        "Sitka, AK: Sitka Rocky Gutierrez (SIT)",
        "South Bend, IN: South Bend International (SBN)",
        "Spokane, WA: Fairchild AFB (SKA)",
        "Spokane, WA: Spokane International (GEG)",
        "Springfield, IL: Abraham Lincoln Capital (SPI)",
        "Springfield, MO: Springfield-Branson National (SGF)",
        "St. Augustine, FL: Northeast Florida Regional (UST)",
        "St. Cloud, MN: St. Cloud Regional (STC)",
        "St. George, UT: St George Regional (SGU)",
        "St. Louis, MO: St Louis Lambert International (STL)",
        "St. Mary's, AK: St. Mary's Airport (KSM)",
        "St. Petersburg, FL: St Pete Clearwater International (PIE)",
        "State College, PA: University Park (SCE)",
        "Staunton, VA: Shenandoah Valley Regional (SHD)",
        "Stillwater, OK: Stillwater Regional (SWO)",
        "Stockton, CA: Stockton Metropolitan (SCK)",
        "Sun Valley/Hailey/Ketchum, ID: Friedman Memorial (SUN)",
        "Syracuse, NY: Syracuse Hancock International (SYR)",
        "Tallahassee, FL: Tallahassee International (TLH)",
        "Tampa, FL: Tampa International (TPA)",
        "Telluride, CO: Telluride Regional (TEX)",
        "Texarkana, AR: Texarkana Regional-Webb Field (TXK)",
        "Tokeen, AK: Tokeen Airport (TKI)",
        "Toledo, OH: Eugene F Kranz Toledo Express (TOL)",
        "Toledo, OH: Toledo Express (TOL)",
        "Topeka, KS: Topeka Regional (FOE)",
        "Traverse City, MI: Cherry Capital (TVC)",
        "Trenton, NJ: Trenton Mercer (TTN)",
        "Tucson, AZ: Tucson International (TUS)",
        "Tulsa, OK: Tulsa International (TUL)",
        "Tunica, MS: Tunica Municipal (UTM)",
        "Tupelo, MS: Tupelo Regional (TUP)",
        "Twin Falls, ID: Joslin Field - Magic Valley Regional (TWF)",
        "Tyler, TX: Tyler Pounds Regional (TYR)",
        "Unalaska, AK: Unalaska Airport (DUT)",
        "Utica/Rome, NY: Oneida County (UCA)",
        "Valdosta, GA: Valdosta Regional (VLD)",
        "Valparaiso, FL: Eglin AFB Destin Fort Walton Beach (VPS)",
        "Vernal, UT: Vernal Regional (VEL)",
        "Victoria, TX: Victoria Regional (VCT)",
        "Visalia, CA: Visalia Municipal (VIS)",
        "Waco, TX: Waco Regional (ACT)",
        "Walla Walla, WA: Walla Walla Regional (ALW)",
        "Washington, DC: Ronald Reagan Washington National (DCA)",
        "Washington, DC: Washington Dulles International (IAD)",
        "Waterloo, IA: Waterloo Regional (ALO)",
        "Watertown, NY: Watertown International (ART)",
        "Watertown, SD: Watertown Regional (ATY)",
        "Wenatchee, WA: Pangborn Memorial (EAT)",
        "Wendover, UT: Wendover Airport (ENV)",
        "West Palm Beach/Palm Beach, FL: Palm Beach International (PBI)",
        "West Yellowstone, MT: Yellowstone (WYS)",
        "White Plains, NY: Westchester County (HPN)",
        "Wichita Falls, TX: Sheppard AFB/Wichita Falls Municipal (SPS)",
        "Wichita, KS: Wichita Dwight D Eisenhower National (ICT)",
        "Williamsport, PA: Williamsport Regional (IPT)",
        "Williston, ND: Sloulin Field International (ISN)",
        "Williston, ND: Williston Basin International (XWA)",
        "Wilmington, DE: New Castle (ILG)",
        "Wilmington, NC: Wilmington International (ILM)",
        "Worcester, MA: Worcester Regional (ORH)",
        "Wrangell, AK: Wrangell Airport (WRG)",
        "Yakima, WA: Yakima Air Terminal/McAllister Field (YKM)",
        "Yakutat, AK: Yakutat Airport (YAK)",
        "Yap, Federated States of Micronesia: Yap International (YAP)",
        "Youngstown/Warren, OH: Youngstown-Warren Regional (YNG)",
        "Yuma, AZ: Yuma MCAS/Yuma International (YUM)"]
	
	scheduler = PreemptiveScheduler(time_slice=0.5)
	
	scheduler.add_thread(target=scrape, args=(airline_codes, airportCodes[:5]))
	scheduler.add_thread(target=scrape, args=(airline_codes, airportCodes[5:10]))
	scheduler.add_thread(target=scrape, args=(airline_codes, airportCodes[10:15]))
	scheduler.add_thread(target=scrape, args=(airline_codes, airportCodes[15:20]))
	scheduler.add_thread(target=scrape, args=(airline_codes, airportCodes[20:25]))
	
	scheduler.add_thread(target=computation_task, args=())
	scheduler.add_thread(target=io_task, args=("log1.txt",))
	scheduler.add_thread(target=network_task, args=())
	scheduler.add_thread(target=data_processing_task, args=([random.randint(1, 1000) for _ in range(100)],))
	scheduler.add_thread(target=image_processing_task, args=("image.jpeg",))
	embarrassingly_parallel_task(scheduler, 4)  # Add EP task with 4 threads

	scheduler.start()
	time.sleep(10)  # Let the threads run for 10 seconds
	scheduler.stop()
	scheduler.join()

if __name__ == "__main__":
    main()
