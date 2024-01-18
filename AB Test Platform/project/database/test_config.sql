CREATE TABLE ABTests (
    test_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    data_collect_start_date DATE,
    data_collect_end_date DATE,
    lower_bound NUMERIC,
    upper_bound NUMERIC,
    status VARCHAR(50)
);

CREATE TABLE configurations (
    id SERIAL PRIMARY KEY,
    slice_type VARCHAR(255),
    aggregator VARCHAR(255),
    aggregation_type VARCHAR(255),
    parameter TEXT,
    test VARCHAR(255),
    AA_alpha NUMERIC,
    bootstrap_cycles INT,
    distribution VARCHAR(255)
);

CREATE TABLE ABTestResults (
    result_id SERIAL PRIMARY KEY,
    test_id INT NOT NULL,
    metric VARCHAR(255),
    type VARCHAR(255),
    channel VARCHAR(255),
    comparison_count INT,
    unique_restaurant_ratio NUMERIC,
    metric_before_test_group NUMERIC,
    metric_before_control_group NUMERIC,
    metric_after_test_group NUMERIC,
    metric_after_control_group NUMERIC,
    test_group_growth NUMERIC,
    control_group_growth NUMERIC,
    test_type VARCHAR(255),
    ab_p_value NUMERIC,
    ab_p_value_std NUMERIC,
    aa_p_value NUMERIC,
    FOREIGN KEY (test_id) REFERENCES ABTests (test_id) ON DELETE CASCADE
);
