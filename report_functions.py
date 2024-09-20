import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import folium
from IPython.display import IFrame, display

def get_database_connection(password, database_name="civitatis_airbnb"):
    """
    Create a database connection using SQLAlchemy.
    """
    connection_string = f'mysql+pymysql://root:{password}@localhost:3306/{database_name}'
    engine = create_engine(connection_string)
    return engine

def execute_query(engine, query):
    """
    Execute a SQL query and return the result as a DataFrame.
    """
    return pd.read_sql(query, con=engine)

def plot_capacity_classification(engine):
    """
    Plot the percentage of Airbnbs by accommodation capacity.
    """
    consulta_clasificacion = """
    SELECT
        CASE
            WHEN accommodates = 1 THEN '1'
            WHEN accommodates = 2 THEN '2'
            ELSE '>2'
        END AS capacity_classification,
        COUNT(*) AS total_listings,
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM listing)) AS percentage
    FROM listing
    GROUP BY capacity_classification
    """
    df_airbnb_capacity_percentage = execute_query(engine, consulta_clasificacion)
    plt.bar(df_airbnb_capacity_percentage['capacity_classification'], df_airbnb_capacity_percentage['percentage'], color=['red', 'blue', 'green'])
    plt.xlabel('Capacidad')
    plt.ylabel('Porcentaje (%)')
    plt.title('Porcentaje de Airbnbs según capacidad de alojamiento')
    for idx, value in enumerate(df_airbnb_capacity_percentage['percentage']):
        plt.text(idx, value + 1, f'{value:.2f}%', ha='center')
    plt.show()

def plot_capacity_map(engine):
    """
    Create and display a map showing Airbnb locations by capacity.
    """
    consulta_mapa = """
    SELECT
        latitude,
        longitude,
        CASE
            WHEN accommodates = 1 THEN '1'
            WHEN accommodates = 2 THEN '2'
            ELSE '>2'
        END AS capacity_classification
    FROM listing
    """
    df_airbnb_map_data = execute_query(engine, consulta_mapa)
    map_airbnb = folium.Map(location=[36.7213, -4.4216], zoom_start=12)
    color_dict = {'1': 'red', '2': 'blue', '>2': 'green'}
    for idx, row in df_airbnb_map_data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            color=color_dict[row['capacity_classification']],
            fill=True,
            fill_color=color_dict[row['capacity_classification']],
            fill_opacity=0.7
        ).add_to(map_airbnb)
    legend_html = '''
         <div style="position: fixed;
                     bottom: 50px; left: 50px; width: 250px; height: 110px;
                     background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                     ">&nbsp; <b>Capacidad de los alojamientos</b> <br>
                     &nbsp; <i class="fa fa-circle" style="color:red"></i>&nbsp; 1 persona <br>
                     &nbsp; <i class="fa fa-circle" style="color:blue"></i>&nbsp; 2 personas <br>
                     &nbsp; <i class="fa fa-circle" style="color:green"></i>&nbsp; >2 personas
         </div>
    '''
    map_airbnb.get_root().html.add_child(folium.Element(legend_html))
    map_file = 'airbnb_map.html'
    map_airbnb.save(map_file)

    # Display the map in the notebook
    display(IFrame(map_file, width=800, height=600))

def plot_hosts_by_listings(engine):
    """
    Plot the percentage of hosts by the number of listings they have.
    """
    consulta_hosts_anuncios = """
    SELECT
        CASE
            WHEN host_listings_count = 1 THEN '1'
            WHEN host_listings_count = 2 THEN '2'
            WHEN host_listings_count BETWEEN 3 AND 5 THEN '3-5'
            WHEN host_listings_count BETWEEN 6 AND 10 THEN '6-10'
            WHEN host_listings_count > 10 THEN '+10'
            ELSE 'Sin categoría'
        END AS host_category,
        COUNT(host_id) AS total_hosts,
        (COUNT(host_id) * 100 / (SELECT COUNT(*) FROM civitatis_airbnb.host)) AS percentage
    FROM civitatis_airbnb.host
    GROUP BY host_category;
    """
    df_hosts_category = execute_query(engine, consulta_hosts_anuncios)
    category_order = ['1', '2', '3-5', '6-10', '+10', 'Sin categoría']
    df_hosts_category['host_category'] = pd.Categorical(df_hosts_category['host_category'], categories=category_order, ordered=True)
    df_hosts_category = df_hosts_category.sort_values('host_category')
    plt.bar(df_hosts_category['host_category'], df_hosts_category['percentage'], color='purple')
    plt.xlabel('Categoría de Host')
    plt.ylabel('Porcentaje (%)')
    plt.title('Porcentaje de Hosts por Número de Anuncios')
    for idx, value in enumerate(df_hosts_category['percentage']):
        plt.text(idx, value + 1, f'{value:.2f}%', ha='center')
    plt.show()

def display_top_hosts(engine):
    """
    Display the top 10 hosts by the number of properties they manage.
    """
    consulta_top_hosts = """
    SELECT host_name, COUNT(listing.listing_id) AS total_listings
    FROM civitatis_airbnb.listing
    JOIN civitatis_airbnb.host ON listing.host_id = host.host_id
    GROUP BY host_name
    ORDER BY total_listings DESC
    LIMIT 10;
    """
    df_top_hosts = execute_query(engine, consulta_top_hosts)
    display(df_top_hosts)
