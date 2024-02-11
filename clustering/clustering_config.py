cluster_config = [
    {
        'cluster': ['Room Type','Price Group'],
        'model': 'kmean',
        'normalization': False,
        'eps / n_clusters': 1,
        'min_samples': 'none',
    },   
    {
        'cluster': ['action_order_success', 'action_order_success_std'],
        'model': 'dbscan',
        'normalization': True,
        'eps / n_clusters': 0.0036,
        'min_samples': 8,
    },  
]
cluster_config_copy = [
    {
        'cluster': 'Room Type',
        'model': 'kmean',
        'normalization': False,
        'eps / n_clusters': 5,
        'min_samples': 'none',
    },    
    {
        'cluster': 'Price Group',
        'model': 'kmean',
        'normalization': False,
        'eps / n_clusters': 5,
        'min_samples': 'none',
    },
    {
        'cluster': ['latitude', 'longitude'],
        'model': 'dbscan',
        'normalization': False,
        'eps / n_clusters': 1,
        'min_samples': 5,
    },
    {
        'cluster': ['action_order_success'],
        'model': 'dbscan',
        'normalization': False,
        'eps / n_clusters': 100,
        'min_samples': 3,
    },
    
]

# Исходный словарь цветов
colors = {
    0: 'gray', 1: 'darkred', 2: 'blue', 3: 'cadetblue', 4: 'black',
    5: 'lightgreen', 6: 'beige', 7: 'pink', 8: 'green', 9: 'darkpurple',
    10: 'lightgray', 11: 'darkblue', 12: 'orange', 13: 'red', 14: 'lightblue',
    15: 'lightred', 16: 'darkgreen', 17: 'white', 18: 'purple',
    19: 'gray', 20: 'darkred', 21: 'blue', 22: 'cadetblue', 23: 'black',
    24: 'lightgreen', 25: 'beige', 26: 'pink', 27: 'green', 28: 'darkpurple',
    29: 'lightgray', 30: 'darkblue', 31: 'orange', 32: 'red', 33: 'lightblue',
    34: 'lightred', 35: 'darkgreen', 36: 'white', 37: 'purple',
    38: 'gray', 39: 'darkred', 40: 'blue', 41: 'cadetblue', 42: 'black',
    43: 'lightgreen', 44: 'beige', 45: 'pink', 46: 'green', 47: 'darkpurple',
    48: 'lightgray', 49: 'darkblue', 50: 'orange', 51: 'red', 52: 'lightblue',
    53: 'lightred', 54: 'darkgreen', 55: 'white', 56: 'purple'
}