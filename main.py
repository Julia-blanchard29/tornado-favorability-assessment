from drafter import *
from dataclasses import dataclass
import matplotlib.pyplot as plt
import math

set_website_title("Tornado Favorability Assessment")
set_site_information(
    author="Julia Blanchard",
    description="Input weather conditions to calculate storm relative helicity, dew point,\n"
    "and assess the location to determine the likelihood of a tornado forming.",
    sources="Drafter Documentation",
    planning=["https://1drv.ms/w/c/0707199A98986B26/IQDRTgUGvu_UTLXSCFX0u7JrAUMH-pLdAvsAAVjloYeR2oE?e=dW2VpW", "https://1drv.ms/w/c/0707199A98986B26/IQDElTUM4zxLQYlHP_I70URgAUPJ1VpOaLxVkr9603mzZNU?e=hI5CqT", "https://1drv.ms/w/c/0707199A98986B26/IQD0N8mCG4XeRIxyKxqVAcmSAZwoB3jv0qgrOLzfCnUa3dM?e=Fk7HYC"],
    links=[]
)

hide_debug_information()
set_website_framed(False)

@dataclass
class SRH:
    uv_upper: list[float] #(the first value in the list is west/east and the second is north/south
    uv_lower: list[float]
    upper_alt: int
    lower_alt: int
    storm_u: float
    storm_v: float
    
@dataclass
class outside_conditions:
    humidity: float
    location: str
    temperature: float

@dataclass
class State:
    srh_conditions: list[SRH]
    weather: outside_conditions
    likelihood_scale: str
    tornado_risk: str

@route
def index(state: State) -> Page:
    return Page(state, [
        "What conditions create favorability for a tornado?" + "\n" + "Click Thunderstorm or Supercell to find out:" + "\n",
        Button("Thunderstorm", "initial_storm"),
        Button("Supercell", "initial_supercell"),
    ])
        
@route
def initial_storm(state: State) -> Page:
    return Page(state, [
        "Tornados form out of intensified thunderstorms, supercells, that experience rotation." + "\n",
        "Go Back and click Supercell to learn more!\n",
        Button("Go Back", "index"),
    ])
@route
def initial_supercell(state: State) -> Page:
    return Page(state, [
        "There are many factors that play into the conditions of a supercell!\n",
        "You will be prompted through a set of input conditions to determine the\n",
        "storm relative helicity.\n",
        "The lower and upper altitude values should be number in kilometers, EX: 3 kilometers = 10,000 ft.\n",
        "Enter the lower altitude:\n",
        "Hint: the lower altitude is typically 0.\n",
        TextBox("lower_altitude", 0),
        Button("Enter Lower", "enter_lower"),
        Button("Go Back", "index"),
    ])

@route
def enter_lower(state: State, lower_altitude: int) -> Page:
    state.srh_conditions[0].lower_alt = lower_altitude
    return Page(state, [
        "Enter the upper altitude:\n",
        TextBox("upper_altitude", 0),
        Button("Enter", "enter_upper"),
    ])

@route
def enter_upper(state: State, upper_altitude: int) -> Page:
    state.srh_conditions[0].upper_alt = upper_altitude
    return Page(state, [
        "Great! Now we need to know the wind velocity conditions.\n",
        "What is the upper wind velocity west/east? The input should be a decimal.\n",
        "(Can be negative or positive)\n",
        TextBox("upper_west_east_velocity", 0.0),
        Button("Enter", "enter_upper_WEV"),
    ])

@route
def enter_upper_WEV(state: State, upper_west_east_velocity: float) -> Page:
    state.srh_conditions[0].uv_upper[0] = upper_west_east_velocity
    return Page(state, [
        "What is the upper wind velocity north/south?\n",
        TextBox("upper_north_south_velocity", 0.0),
        Button("Enter", "enter_upper_NSV"),
    ])

@route
def enter_upper_NSV(state: State, upper_north_south_velocity: float) -> Page:
    state.srh_conditions[0].uv_upper[1] = upper_north_south_velocity
    return Page(state, [
        "What is the lower west/east velocity\n",
        TextBox("lower_west_east_velocity", 0.0),
        Button("Enter", "enter_lower_WEV"),
    ])

@route
def enter_lower_WEV(state: State, lower_west_east_velocity: float) -> Page:
    state.srh_conditions[0].uv_lower[0] = lower_west_east_velocity
    return Page(state, [
        "What is the lower north/south velocity?\n",
        TextBox("lower_north_south_velocity", 0.0),
        Button("Enter", "enter_lower_NSV"),
    ])

@route
def enter_lower_NSV(state: State, lower_north_south_velocity: float) -> Page:
    state.srh_conditions[0].uv_lower[1] = lower_north_south_velocity
    return Page(state, [
        "Great! Now we need to collect the storm motion for west/east and north/south.",
        "What's the motion of the storm horizontally (west/east)? Enter a negative or positive decimal.",
        TextBox("west_east_motion", 0.0),
        Button("Enter", "enter_west_east_motion"),
    ])

@route
def enter_west_east_motion(state: State, west_east_motion: float ) -> Page:
    state.srh_conditions[0].storm_u = west_east_motion
    return Page(state, [
        "What is the storm motion vertically (north/south)?\n",
        TextBox("north_south_motion", 0.0),
        Button("Enter", "enter_north_south_motion"),
    ])

@route
def enter_north_south_motion(state: State, north_south_motion: float) -> Page:
    state.srh_conditions[0].storm_v = north_south_motion
    return Page(state, [
        "Now we have satisfied all the variables needed to calculate the storm relative helicity!\n",
        "Click Calculate to reveal your storm's helicity!\n",
        Button("Calculate", "calculate_SRH"),
    ])

def calculate_srh(conditions: SRH) -> float:
    u_average = (conditions.uv_upper[0] + conditions.uv_lower[0]) / 2
    v_average = (conditions.uv_upper[1] + conditions.uv_lower[1]) / 2

    change_u = conditions.uv_upper[0] - conditions.uv_lower[0]
    change_v = conditions.uv_upper[1] - conditions.uv_lower[1]

    storm_relative_helicity = ((u_average - conditions.storm_u) * change_v
                               - (v_average - conditions.storm_v) * change_u)
    return storm_relative_helicity

def compare_srh_risk(srh_value: float) -> str:
    if srh_value <= 50.0:
        return "low risk"
    if 50 < srh_value <= 70:
        return "moderate risk"
    if 70 < srh_value < 100:
        return "intermediate risk"
    if srh_value >= 100:
        return "high risk"

@route
def calculate_SRH(state: State) -> Page:
    result = calculate_srh(state.srh_conditions[0])
    risk = compare_srh_risk(result)
    
    state.likelihood_scale = risk
    
    return Page(state, [
        "The storm relative helicity is: \n",
        str(round(result, 2)) + "m²/s²\n",
        "Your SRH value indicates " + risk + " for the formation of a tornado.\n",
        "Compare your data with real SRH values from past tornadoes: \n",
        Button("Compare Data", "compare_plot_data"),
    ])
    
def add_plot_data(srh_value: float) -> list[float]:
    #Past tornado SRH values:
    #tornado_locations = [[Butler County, Missouri], [Moore, Oklahoma], [Bridge Creek–Moore, Oklahoma]]
    srh_values = [272.0, 156.0, 338.0]
    srh_values.append(srh_value)
    return srh_values

@route
def compare_plot_data(state: State) -> Page:
    result = calculate_srh(state.srh_conditions[0])
    values = add_plot_data(result)

    locations = ["Butler County", "Moore", "Bridge Creek-Moore", "User data"]
    
    plt.bar(locations, values)
    plt.xlabel("Storm")
    plt.ylabel("SRH (m²/s²)")
    plt.title("Comparing Storm Relative Helicity")
    plt.xticks(rotation=15)
    
    return Page(state, [
        "On the graph below, your SRH value is compared with SRH values of real tornadoes\n",
        "that occurred in Butler County, Missouri, Moore, Oklahoma, and Bridge Creek–Moore, Oklahoma.\n",
        "Its important to note that just because an SRH value is large, does not mean the tornado will\n",
        "also be large. It is just a measurement on the possibility of one forming. We will need to add\n",
        "some more conditions.\n",
        MatPlotLibPlot(),
        Button("Add More Conditions", "get_dew_point_measurements"),
    ])

@route
def get_dew_point_measurements(state: State) -> Page:
    return Page(state, [
        "Let's find three more conditions to narrow down the likelihood of a tornado forming!\n",
        "We will calculate the dew point by taking the temperature and the humidity of the\n",
        "outside conditions. In addition, we will take a general geographic location.\n",
        "Inputs will be calculated in Celsius.\n",
        "\n",
        "What is the temperature: ",
        TextBox("temperature", 0.0),
        "What is the humidity: ",
        TextBox("humidity", 0.0),
        Button("Calculate Dew Point", "use_dew_point"),
    ])

def calculate_dew_point(temperature: float, humidity: float) -> float:
    a = 17.625
    b = 243.04
    alpha = math.log(humidity / 100) + (a * temperature) / (b + temperature)
    dew_point = (b * alpha) / (a - alpha)
    return dew_point

def compare_dew_point(dew_point: float) -> str:
    if dew_point <= 13:
        return "unfavorable and not likely"
    if 13 < dew_point < 16:
        return "generally favorable and possibly likely"
    if dew_point >= 17:
        return "favorable and likely"
    else:
        return "unfavorable"

@route
def use_dew_point(state: State, temperature: float, humidity: float) -> Page:
    state.weather.temperature = temperature
    state.weather.humidity = humidity
    
    result = calculate_dew_point(temperature, humidity)
    risk = compare_dew_point(result)

    state.tornado_risk = risk
    
    return Page(state, [
        "The calculated dew point is: ",
        str(round(result, 2)) + "°C\n",
        "The dew point is ",
        compare_dew_point(result),
        "for the formation of a tornado.\n",
        Button("Add Location", "enter_location"),
    ])

@route
def enter_location(state: State) -> Page:
        return Page(state, [
        "Finally, enter one of these general geographical locations: \n",
        "North, East, South, West \n",
        TextBox("location", ""),
        Button("Enter", "get_location"),
    ])
    
def compare_locations(location: str) -> str:
    if location == "North":
        return "unfavorable"
    if location == "East":
        return "potentially favorable if closer to the south"
    if location == "West":
        return "potentially favorable if not far west"
    if location == "South":
        return "favorable"
    else:
        return "unfavorable"

@route
def get_location(state: State, location: str) -> Page:
    state.weather.location = location
    result = compare_locations(location)
    
    return Page(state, [
        "Your storm's location is ",
        result,
        "for the formation of a tornado.\n",
        "Look at the overall results!\n",
        Button("Overall Results", "retrieve_overall"),
    ])

@route
def retrieve_overall(state: State) -> Page:
    # Calculate SRH
    srh_result = calculate_srh(state.srh_conditions[0])
    srh_assessment = compare_srh_risk(srh_result)

    # Calculate dew point
    dew_point = calculate_dew_point(
        state.weather.temperature,
        state.weather.humidity
    )
    dew_point_assessment = compare_dew_point(dew_point)

    # Calculate location
    location_assessment = compare_locations(state.weather.location)

    return Page(state, [
        "OVERALL RESULTS\n",
        "--------------------------\n",

        "Storm Relative Helicity:\n",
        str(round(srh_result, 2)) + " m²/s²\n",
        "SRH Assessment: ",
        srh_assessment,
        "\n\n",

        "Dew Point:\n",
        str(round(dew_point, 2)) + "°C\n",
        "Dew Point Assessment: ",
        dew_point_assessment,
        "\n\n",

        "Location:\n",
        state.weather.location,
        "\n",
        "Location Assessment: ",
        location_assessment,
        "\n\n",

        "These are environmental indicators, not a prediction "
        "that a tornado will form."
    ])
        

start_server(State(
    [SRH([0.0, 0.0], [0.0, 0.0], 0, 0, 0.0, 0.0)],
    outside_conditions(0.0, "", 0.0),
    "",
    ""
))
