import osmnx as ox
import numpy as np
import matplotlib.pyplot as plt

def get_cycleways(city_name: str):
    """
    Returns all cycleways in a city (networkx.MultiDiGraph).
    """
    useful_tags = ox.settings.useful_tags_way + ['cycleway']
    ox.config(use_cache=True, log_console=True, useful_tags_way=useful_tags)
    cycleways = ox.graph_from_place(query = city_name, network_type='bike', simplify=False)
    non_cycleways = [(u, v, k) for u, v, k, d in cycleways.edges(keys=True, data=True) if not ('cycleway' in d or d['highway']=='cycleway')]
    cycleways.remove_edges_from(non_cycleways)
    cycleways = ox.utils_graph.remove_isolated_nodes(cycleways)
    return cycleways

def get_city(city_name: str):
    """
    Returns cycleways and road info (networkx.MultiDiGraph) and city area (geopandas.geodataframe.GeoDataFrame).
    """
    # get cycleways 
    cycleways = get_cycleways(city_name)
    # get city area
    city_area = ox.geocode_to_gdf(city_name)
    # get roads
    roads = ox.graph_from_place(city_name,network_type='drive')

    return cycleways,roads,city_area

def plot_cycleways(city_name: str, cycleways, roads, city_area):
    """
    Plots cycleways overlaid city area. Returns matplotlib fig,ax.
    cycleways: (networkx.MultiDiGraph) cycleways info from get_city func, or osmnx.graph_from_place
    roads: (networkx.MultiDiGraph) road info from get_city func, or ox.graph_from_place
    city_area: (geopandas.geodataframe.GeoDataFrame) city area from get_city func, or osmnx.geocode_to_gdf
    """
    fig, ax = plt.subplots(figsize=(4,4))
    ax.set_title(city_name,fontsize=12)

    city_area.plot(ax=ax, facecolor='gainsboro')
    ox.plot_graph(roads,ax=ax,node_size=0,edge_linewidth=.25,edge_color='dimgrey')
    ox.plot_graph(cycleways,ax=ax,node_size=0,edge_linewidth=.65,edge_color='dodgerblue')
    
    fig.text(s="By William Thyer\nData from OpenStreetMap", 
            x=1, y=-.01, transform = ax.transAxes,
            horizontalalignment='right',verticalalignment='top',
            color='k',fontsize=5
            )  
    ax.axis('off')
    plt.tight_layout()

    return fig, ax

def calc_road_cycleway_ratio(cycleways, roads):
    """
    Returns ratio of roads to cycleways. Uses osmnx.basic_stats.
    cycleways: (networkx.MultiDiGraph) cycleways info from get_city func, or osmnx.graph_from_place
    roads: (networkx.MultiDiGraph) road info from get_city func, or ox.graph_from_place
    """
    c = ox.basic_stats(cycleways)
    r = ox.basic_stats(roads)
    rc_ratio = r['edge_length_total']/c['edge_length_total']
    return rc_ratio

