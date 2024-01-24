
test_group = [74020587, 74013270, 74020449, 74021433, 74021788, 74020871, 74020660, 74021978, 74020896,
              74012184, 74020851, 74020828, 74021003, 74021914, 74021880, 74021975, 74321670, 74321666,
              74215106, 74021329, 74021678, 74021302, 74021639]

# Data Aggregation
class Aggregation:
    @staticmethod
    def drop_outliers(data, aggregator, lower_bound, upper_bound):
        lb = data[aggregator].quantile(lower_bound)
        ub = data[aggregator].quantile(upper_bound)
        return data[(data[aggregator] >= lb) & (data[aggregator] <= ub)]

    @staticmethod
    def aggregate(data, slice_type, aggregator, aggregation_type, parameter):
        filtered_data = data.query(parameter) if parameter != 'none' else data
        if slice_type and aggregator:
            return round(filtered_data.groupby(slice_type.split(', '), as_index=False).aggregate({aggregator: aggregation_type}), 2)
        else:
            return filtered_data