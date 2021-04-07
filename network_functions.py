import osmnx as ox
import numpy as np
import matplotlib.pyplot as plt

def get_cycleways(city_name: str):
    """
    get all cycleways in a city
    """
    useful_tags = ox.settings.useful_tags_way + ['cycleway']
    ox.config(use_cache=True, log_console=True, useful_tags_way=useful_tags)
    G = ox.graph_from_place(query = city_name, network_type='bike', simplify=False)
    non_cycleways = [(u, v, k) for u, v, k, d in G.edges(keys=True, data=True) if not ('cycleway' in d or d['highway']=='cycleway')]
    G.remove_edges_from(non_cycleways)
    G = ox.utils_graph.remove_isolated_nodes(G)
    return G

def get_city(city_name: str):
    # get cycleways 
    cycleways = get_cycleways(city_name)
    # get city area
    city_area = ox.geocode_to_gdf(city_name)
    # get roads
    roads = ox.graph_from_place(city_name,network_type='drive')

    return cycleways,roads,city_area

def plot_cycleways(city_name: str,cycleways, roads, city_area):
    """
    plot cycleways overlaid city area
    """
    fig, ax = plt.subplots(figsize=(4,4))
    ax.set_title(city_name,fontsize=9)

    city_area.plot(ax=ax, facecolor='gainsboro')
    ox.plot_graph(roads,ax=ax,node_size=0,edge_linewidth=.25,edge_color='dimgrey')
    ox.plot_graph(cycleways,ax=ax,node_size=0,edge_linewidth=.65,edge_color='dodgerblue')

    ax.axis('off')

    return fig

