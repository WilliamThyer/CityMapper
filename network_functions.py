import osmnx as ox
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "serif"

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

def get_footprints(city_name):
    """
    UNSTABLE
    Returns footprints of buildings. Seems to timeout for larger cities.
    """
    tags = {"building": True}
    footprints = ox.geometries_from_place(city_name, tags)
    # ox.plot_footprints(footprints, ax=ax,color='dimgrey')

    return footprints

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

def plot_cycleways(
    city_name: str, 
    cycleways, 
    roads=None, 
    city_area=None, 
    road_cycleway_ratio: float=None, 
    signature: bool=True,
    save_figure=True,
    extension='.png'):
    """
    Plots cycleways overlaid city area. Returns matplotlib fig,ax.
    cycleways: (networkx.MultiDiGraph) cycleways info from get_city func, or osmnx.graph_from_place
    roads: (networkx.MultiDiGraph) road info from get_city func, or ox.graph_from_place
    city_area: (geopandas.geodataframe.GeoDataFrame) city area from get_city func, or osmnx.geocode_to_gdf
    road_cycleway_ratio: (float) ratio of roads to cycleways in the city
    signature: (bool) set to false to remove signature.
    """
    fig, ax = plt.subplots(figsize=(4,4))

    if road_cycleway_ratio is None:
        ax.set_title(city_name,fontsize=12)

    elif road_cycleway_ratio is not None:
        # make subtitle in hacky way
        rc_ratio_round = round(road_cycleway_ratio)
        fig.text(s=f'Road to Cycleway Ratio is {rc_ratio_round}:1',
                x=.5, y=1.01, transform = ax.transAxes,
                horizontalalignment='center',verticalalignment='bottom',
                color='k',fontsize=6
                )

        fig.text(s=city_name,
                x=.5, y=1.04, transform = ax.transAxes,
                horizontalalignment='center',verticalalignment='bottom',
                color='k',fontsize=12
                )

    if city_area is not None:
        city_area.plot(ax=ax, facecolor='gainsboro')
    if roads is not None:
        ox.plot_graph(roads,ax=ax,node_size=0,edge_linewidth=.25,edge_color='dimgrey')
    ox.plot_graph(cycleways,ax=ax,node_size=0,edge_linewidth=.85,edge_color='limegreen')
    
    if signature is True:
        fig.text(s="@WThyer\nOpenStreetMap", 
                x=1, y=-.01, transform = ax.transAxes,
                horizontalalignment='right',verticalalignment='top',
                color='k',fontsize=5
                )

    ax.axis('off')
    plt.tight_layout()
    
    if save_figure is True:
        savefig(city_name=city_name,fig=fig,extension=extension)

    return fig, ax

def calc_road_cycleway_ratio(cycleways, roads):
    """
    Returns ratio of cycleways to roads. Uses osmnx.basic_stats.
    cycleways: (networkx.MultiDiGraph) cycleways info from get_city func, or osmnx.graph_from_place
    roads: (networkx.MultiDiGraph) road info from get_city func, or ox.graph_from_place
    """
    c = ox.basic_stats(cycleways)
    r = ox.basic_stats(roads)
    rc_ratio = r['edge_length_total']/c['edge_length_total']
    return rc_ratio

def savefig(city_name,fig,extension='.png'):
    filename = f'examples/{extension[1:]}/{city_name}{extension}'
    fig.savefig(filename,dpi=1000,facecolor='w',transparent=False)