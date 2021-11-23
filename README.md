# Trip Finder

**Python module searching for available trips**

It provides customizable searching method.
## Command line arguments
### Required arguments

You have to define following required arguments:

| Argument name | Type   | Description                      | Notes |
|---------------|--------|----------------------------------|-------|
| `csv_file`    | string | Path to csv file with flights    |       |
| `origin`      | string | Airport code of trip origin      |       |
| `destination` | string | Airport code of trip destination |       |

### Optional arguments
You may use following optional search parameters:

| Argument name | Type                  | Description                 | Notes             |
|---------------|-----------------------|-----------------------------|-------------------|
| `bags`        | non-negative integer  | Number of requested bags    | Defaults to 0     |
| `stops`       | non-negative integer  | Maximum number of stopovers | Defaults to 0     |
| `return`      | boolean               | Is it a return flight?      | Defaults to false |
### Input csv file

The input csv file containing all flights must respect following format:
- `flight_no`: Flight number.
- `origin`, `destination`: Airport codes.
- `departure`, `arrival`: Dates and times of the departures/arrivals.
- `base_price`, `bag_price`: Prices of the ticket and one piece of baggage.
- `bags_allowed`: Number of allowed pieces of baggage for the flight.
### Notes

Mind there is no validation for input. It expacts correct data types of both required and optional arguments. Moreover, it is crutial to input correct `csv_file` path. Also `csv_file` must be in predefined format.
## Example

Run following example from command line

```bash
python -m trip_finder example/example2.csv RFZ WIW --bags=1 --stops=1 --return
```

This will load available flights from the file `example/example2.csv`, seach for all valid return trips between aiports `RFZ` and `WIW` with maximum one stopover, and with one required bag.

Results will be sorted ascending based on total trip price.

