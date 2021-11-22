import csv
import json
import datetime as dt

from argparse import ArgumentParser


class TripFinder:
    def __init__(self) -> None:

        # Datetime format
        self._datetime_format = '%Y-%m-%dT%H:%M:%S'

        # Read command line arguments
        cmd_line_args = self._command_line_argumnet_parser()
        self.csv_file_name = cmd_line_args['csv_file_name']
        self.trip_origin = cmd_line_args['trip_origin']
        self.trip_destination = cmd_line_args['trip_destination']
        self.bags = cmd_line_args['bags']
        self.stops = cmd_line_args['stops']
        self.return_trip = cmd_line_args['return_trip']

        # Read csv file with flights
        self.flights = self._csv_input_reader()

        # Store (semi)results
        self.trips = []
        self.results = []

    def __call__(self) -> list:

        # Find trips "to" destination
        self._find_available_trips(self.trip_origin, self.trip_destination)

        # Return trip
        if self.return_trip:
            # Save trips "to" destination
            trips_to = self.trips.copy()
            self.trips.clear()

            # Find trips "from" destination
            self._find_available_trips(self.trip_destination, self.trip_origin)

            # Save trips "from" destination
            trips_back = self.trips.copy()
            self.trips.clear()

            # Find valid return trips
            self.trips = self._match_return_trips(trips_to, trips_back)

        # Return formated results
        return self._format_results()

    def _match_return_trips(self, trips_to: list, trips_back: list) -> list:
        """
        Match `trips_to` and `trips_back` to create valid return trips.
        """

        valid_return_trips = []

        for trip_to in trips_to:
            for trip_back in trips_back:
                # Trip back must be after trip to
                if trip_to[-1]['arrival'] <= trip_back[0]['departure']:
                    valid_return_trips.append(trip_to + trip_back)

        return valid_return_trips

    def _command_line_argumnet_parser(self) -> dict:
        """
        Parse command line arguments.

        Example:
        --------
        python -m solution example/example0.csv RFZ WIW --bags=1 --stops=1 --return
        """

        parser = ArgumentParser(description='Process command line params')
        parser.add_argument('csv_file_name', help='Name of the input csv file')
        parser.add_argument('trip_origin', help='Trip origin')
        parser.add_argument('trip_destination', help='Trip destination')
        parser.add_argument(
            '--bags',
            type=int,
            default=0,
            required=False,
            help='Number of bags',
        )
        parser.add_argument(
            '--stops',
            type=int,
            default=0,
            required=False,
            help='Number of stops',
        )
        parser.add_argument(
            '--return',
            action='store_true',
            required=False,
            help='Return trip',
            dest='return_trip',
        )
        args = parser.parse_args()
        return vars(args)

    def _csv_input_reader(self) -> list:
        """
        Read csv input file and store it in list `flights`.
        """

        flights = []
        with open(self.csv_file_name, 'r') as csv_file:
            # Set reader
            csv_reader = csv.reader(csv_file)

            # Loop over the header line
            next(csv_reader)

            # Loop over the file
            for row in csv_reader:
                flight_no = row[0]
                origin = row[1]
                destination = row[2]
                departure = dt.datetime.strptime(row[3], self._datetime_format)
                arrival = dt.datetime.strptime(row[4], self._datetime_format)
                base_price = float(row[5])
                bag_price = float(row[6])
                bags_allowed = int(row[7])

                flights.append(
                    {
                        'flight_no': flight_no,
                        'origin': origin,
                        'destination': destination,
                        'departure': departure,
                        'arrival': arrival,
                        'base_price': base_price,
                        'bag_price': bag_price,
                        'bags_allowed': bags_allowed,
                    }
                )

        return flights

    def _find_available_trips(
        self, trip_from: str, trip_to: str, trip: list = []
    ) -> None:
        """
        Find all available trips from `trip_from` to `trip_to`.
        """

        LAYOVER_LIMIT_SECONDS_MIN = 60 * 60
        LAYOVER_LIMIT_SECONDS_MAX = 6 * 60 * 60

        for flight in self.flights:
            # Trip itinerary is empty
            if trip == []:
                # Flight origin equals trip origin
                if flight['origin'] == trip_from:
                    # Save the flight and continue searching
                    self._find_available_trips(trip_from, trip_to, [flight])

            # Previous flight destination equals trip destination
            elif trip[-1]['destination'] == trip_to:
                # Save the trip and stop searching
                self.trips.append(trip.copy())
                break

            # Connecting flight after valid layover (stop)
            elif (
                len(trip) - 1 < self.stops
                and trip[-1]['destination'] == flight['origin']
                and LAYOVER_LIMIT_SECONDS_MIN
                <= (flight['departure'] - trip[-1]['arrival']).total_seconds()
                <= LAYOVER_LIMIT_SECONDS_MAX
                and flight['destination'] != trip_from
            ):
                # Save the flight and continue searching
                self._find_available_trips(trip_from, trip_to, trip + [flight])

    def _format_results(self) -> json:
        """
        Compute summary statistics, format result in predefined form
        and sort results on `total_price`.
        """

        for trip in self.trips:

            # Compute summary statistics
            total_base_price = 0
            total_bag_price = 0
            max_bags_allowed = 99
            total_travel_time = str(trip[-1]['arrival'] - trip[0]['departure'])

            for flight in trip:
                total_base_price += flight['base_price']
                total_bag_price += flight['bag_price']
                max_bags_allowed = (
                    flight['bags_allowed']
                    if flight['bags_allowed'] < max_bags_allowed
                    else max_bags_allowed
                )

            total_price = total_base_price + self.bags * total_bag_price

            # Format result
            result = {
                'flights': trip,
                'bags_allowed': max_bags_allowed,
                'bags_count': self.bags,
                'destination': self.trip_destination,
                'origin': self.trip_origin,
                'total_price': total_price,
                'travel_time': total_travel_time,
            }

            # Check number of allowed bags
            if self.bags <= max_bags_allowed:
                self.results.append(result)

        #  Sort results by `total_price`
        self.results = sorted(
            self.results, key=lambda result: result['total_price']
        )

        def _my_datetime_converter(datetime_object: dt.datetime) -> str:
            """
            Format datetime object into string '%Y-%m-%dT%H:%M:%S'.
            """

            if isinstance(datetime_object, dt.datetime):
                return datetime_object.strftime(self._datetime_format)

        return json.dumps(
            self.results, indent=4, default=_my_datetime_converter
        )


if __name__ == '__main__':
    tf = TripFinder()
    trips = tf()
    print(trips)
