from numpy import double
from vehicle.models import Vehicles
from calculator.models import Commute

# These constants are officially provided by fortis bc and bc hydro and are only specific to these companies
EMISSION_FACTOR_FORTIS = 0.719
EMISSION_FACTOR = 0.010670
MILE_TO_KM_RATIO = 1.609
GALLON_TO_LITRES_RATIO = 3.785
PER_100MILES_TO_KM_RATIO = 160.934
EMISSION_FACTOR_FUEL_PRODUCTION = 0.43
METRIC_TONNE_TO_KG_RATIO = 1000


def hydro_calculations(bill_entries):
    """
    Calculate the total_footprint generated from the hydro bill
    :param bill_entries: These are the values from the hydro bill
    :return carbon_footprint: This is the total footprint from the hydro bill
    """
    total_kwh = sum(bill_entries)
    carbon_footprint = (total_kwh * EMISSION_FACTOR) / METRIC_TONNE_TO_KG_RATIO  # in metric tonnes
    return carbon_footprint


def fortis_calculations(bill_entries):
    """
    Calculate the total_footprint generated from the fortis bill
    :param bill_entries: This is a list of kj values from the fortis bill
    :return carbon_footprint: This is the total footprint from the fortis bill
    """
    total_kj = sum(bill_entries)
    carbon_footprint = total_kj * EMISSION_FACTOR_FORTIS
    return carbon_footprint


class CommuteCalculations:
    def __init__(self, commute: Commute):
        """
        Initializer for the class , method _get_emission_efficiency checks if the
        vehicle is electric or not
        :param commute: commute object stores attributes for each commute.
        """
        self.commute = commute
        self.common_emissions = None
        self.city_fuel_eff = None
        self.highway_fuel_eff = None
        self.is_electric = None
        self._get_emission_efficiency()

    def calculate_footprint(self):
        """
        Checks if the vehicle is electric or not and calls the corresponding methods to
        calculate carbon footprint
        """

        distance = self.commute.distance
        highway_percentage = self.commute.highway_perc
        if self.is_electric:
            return self._electric_vehicles_footprint(distance, highway_percentage)
        else:
            return self._calculate_footprint_gasoline(distance, highway_percentage)

    def _get_emission_efficiency(self):
        required_rows = list(Vehicles.objects.all().filter(name=self.commute.vehicle, year=self.commute.vehicle_year,
                                                           trany=self.commute.transmission).values())
        if required_rows[0].cityE != 0:
            self.is_electric = True
            self._get_electric_vehicle_kwh(required_rows)
        else:
            self._get_emission_efficiency_gasoline(required_rows)

    def _get_emission_efficiency_gasoline(self, required_rows):
        """
        This method is called for the non electric vehicles and reads the database for the co2TailpipeGpm ,
        city08 and highway08
        co2TailpipeGpm: This is the emissions of co2 from each vehicle
        city08: Fuel efficiency of the vehicle in the city
        highway08: Fuel efficiency of the vehicle on the highway
        :param required_rows: It is a list of dictionary which stores all the required data of a vehicle
        """
        self.common_emissions = self._mean(required_rows, 'co2TailpipeGpm')
        self.city_fuel_eff = self._mean(required_rows, 'city08')
        self.highway_fuel_eff = self._mean(required_rows, 'highway08')

    def _get_electric_vehicle_kwh(self, required_rows):
        """
        This method is called for the  electric vehicles and reads the database for the cityE ,
        highwayE for a vehicle
        cityE: kwh of the vehicle in the city
        highwayE: kwh of the vehicle on the highway
        """
        self.city_fuel_eff = self._mean(required_rows, 'cityE')
        self.highway_fuel_eff = self._mean(required_rows, 'highwayE')

    @classmethod
    def _mean(cls, lst, key):
        """
        Find the mean of a particular property in a list of dicts
        :param lst: the list of dicts
        :param key: the property whose mean is needed
        """
        return float(sum(d[key] for d in lst)) / len(lst)

    def _calculate_footprint_gasoline(self, distance, highway_percentage) -> double:
        # converting city  fuel efficiency to km per litres
        converted_city_fuel_eff = (self.city_fuel_eff * MILE_TO_KM_RATIO) / GALLON_TO_LITRES_RATIO

        # calculating highway distance
        highway_distance = (highway_percentage / 100) * distance
        # calculating highway fuel
        highway_fuel = highway_distance / ((self.highway_fuel_eff * MILE_TO_KM_RATIO) / GALLON_TO_LITRES_RATIO)
        # calculating city distance
        city_distance = distance - highway_distance
        # calculating city fuel
        city_fuel = city_distance / converted_city_fuel_eff
        # converting emissions to KGco2 per km
        common_emm = self.common_emissions / (MILE_TO_KM_RATIO * METRIC_TONNE_TO_KG_RATIO)
        # calculating footprint for  decomposition city
        fuel_decomposition_city = common_emm * city_distance
        # calculating footprint for  decomposition highway
        fuel_decomposition_highway = highway_distance * common_emm
        # calculating footprint for  fuel production city
        fuel_production_city = city_fuel * EMISSION_FACTOR_FUEL_PRODUCTION
        # calculating footprint for  fuel production city
        fuel_production_highway = highway_fuel * EMISSION_FACTOR_FUEL_PRODUCTION
        # calculating total footprint for the commute
        total_footprint = (fuel_decomposition_city + fuel_production_city + fuel_decomposition_highway
                           + fuel_production_highway) / METRIC_TONNE_TO_KG_RATIO  # in metric tonnes
        print(total_footprint)
        return total_footprint

    def _electric_vehicles_footprint(self, distance, highway_percentage):
        # converting the city and highway data into proper units
        converted_city_kwh = self.city_fuel_eff / PER_100MILES_TO_KM_RATIO
        converted_highway_kwh = self.highway_fuel_eff / PER_100MILES_TO_KM_RATIO

        # calculating highway distance
        highway_distance = (highway_percentage / 100) * distance
        # calculating city distance
        city_distance = distance - highway_distance
        # calculating city kwh
        total_city_kwh = converted_city_kwh * city_distance
        # calculating highway kwh
        total_highway_kwh = converted_highway_kwh * highway_distance
        total_kwh = total_city_kwh + total_highway_kwh
        total_footprint = (total_kwh * EMISSION_FACTOR) / METRIC_TONNE_TO_KG_RATIO  # metric tonnes
        return total_footprint
