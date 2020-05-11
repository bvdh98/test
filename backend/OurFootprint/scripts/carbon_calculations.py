from numpy import double
from vehicle.models import Vehicles

# These constants are officially provided by fortis bc and bc hydro and are only specific to these companies
EMISSION_FACTOR_FORTIS = 0.719
EMISSION_FACTOR_HYDRO = 0.010670


def hydro_calculations(bill_entries):
    """
    Calculate the total_footprint generated from the hydro bill
    :param bill_entries: These are the values from the hydro bill
    :return carbon_footprint: This is the total footprint from the hydro bill
    """
    total_kwh = sum(bill_entries)
    carbon_footprint = (total_kwh * EMISSION_FACTOR_HYDRO) / 1000  # in tonnes
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


class CarbonCalculations:
    def __init__(self, vehicle: Vehicles):
        """
        Initializer for the class , also decides if a vehicle is electric or not and calls the corresponding method
        :param vehicle: vehicle object has attributes name , year and transmission
        """
        self.name = vehicle.name
        self.year = vehicle.year
        self.transmission = vehicle.trany
        self.city_emissions = 0
        self.city_fuel_eff = 0
        self.highway_fuel_eff = 0
        self.is_electric = False

        if vehicle.cityE != 0:
            self.is_electric = True
            self.get_electric_vehicle_kwh()
        else:
            self.get_emission_efficiency()

    def get_emission_efficiency(self):
        """
        This method is called for the non electric vehicles and reads the database for the co2TailpipeGpm ,
        city08 and highway08
        co2TailpipeGpm: This is the emissions of co2 from each vehicle
        city08: Fuel efficiency of the vehicle in the city
        highway08: Fuel efficiency of the vehicle on the highway
        """
        required_rows = list(Vehicles.objects.all().filter(name=self.name, year=self.year,
                                                           trany=self.transmission).values())
        self.city_emissions = self._mean(required_rows, 'co2TailpipeGpm')
        self.city_fuel_eff = self._mean(required_rows, 'city08')
        self.highway_fuel_eff = self._mean(required_rows, 'highway08')

    def get_electric_vehicle_kwh(self):
        """
        This method is called for the  electric vehicles and reads the database for the cityE ,
        highwayE for a vehicle
        cityE: kwh of the vehicle in the city
        highwayE: kwh of the vehicle on the highway
        """
        required_rows = list(Vehicles.objects.all().filter(name=self.name, year=self.year,
                                                           trany=self.transmission).values())
        self.city_fuel_eff = self._mean(required_rows, 'cityE')
        self.highway_fuel_eff = self._mean(required_rows, 'highwayE')

    def calculate_footprint(self, distance, highway_percentage):
        """
        This method is called which checks if the vehicle is electric or not and calls the corresponding methods to
        calculate carbon footprint
        :param distance: It is the total distance of the commute
        :param highway_percentage: It is the percentage of the commute made via the highway
        """
        if self.is_electric:
            return self.electric_vehicles_footprint(distance, highway_percentage)
        else:
            return self.calculate_footprint_gasoline(distance, highway_percentage)

    @classmethod
    def _mean(cls, lst, key):
        """
        Find the mean of a particular property in a list of dicts
        :param lst: the list of dicts
        :param key: the property whose mean is needed
        """
        return float(sum(d[key] for d in lst)) / len(lst)

    def calculate_footprint_gasoline(self, distance, highway_percentage) -> double:
        # converting city  fuel efficiency to km per litres
        converted_city_fuel_eff = (self.city_fuel_eff * 1.609) / 3.785

        # calculating highway distance
        highway_distance = (highway_percentage / 100) * distance
        # calculating highway fuel
        highway_fuel = highway_distance / ((self.highway_fuel_eff * 1.609) / 3.785)
        # calculating city distance
        city_distance = distance - highway_distance
        # calculating city fuel
        city_fuel = city_distance / converted_city_fuel_eff
        # converting emissions to KGco2 per km
        common_emm = self.city_emissions / (1.60934 * 1000)
        # calculating footprint for  decomposition city
        fuel_decomposition_city = common_emm * city_distance
        # calculating footprint for  decomposition highway
        fuel_decomposition_highway = highway_distance * common_emm
        # calculating footprint for  fuel production city
        fuel_production_city = city_fuel * 0.43
        # calculating footprint for  fuel production city
        fuel_production_highway = highway_fuel * 0.43
        # calculating total footprint for the commute
        total_footprint = (fuel_decomposition_city + fuel_production_city + fuel_decomposition_highway
                           + fuel_production_highway) / 1000  # in tonnes
        return total_footprint

    def electric_vehicles_footprint(self, distance, highway_percentage):
        # converting the city and highway data into proper units
        converted_city_kwh = self.city_fuel_eff / 160.934
        converted_highway_kwh = self.highway_fuel_eff / 160.934

        # calculating highway distance
        highway_distance = (highway_percentage / 100) * distance
        # calculating city distance
        city_distance = distance - highway_distance
        # calculating city kwh
        total_city_kwh = converted_city_kwh * city_distance
        # calculating highway kwh
        total_highway_kwh = converted_highway_kwh * highway_distance
        total_kwh = total_city_kwh + total_highway_kwh
        emission_factor = 0.010670
        total_footprint = (total_kwh * emission_factor) / 1000  # tonnes
        return total_footprint
