import osmnx as ox
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update()

class BikeNetworkMapper:

    def __init__(
        self,
        city_name: str,
        plt_params_dict: dict = None):

        self.city_name = city_name
        self.cycleways = None
        self.roads = None
        self.city_area = None
        self.rc_ratio = None

        if plt_params_dict is None:
            plt_params_dict = {
                "figure.facecolor":  (1.0, 1.0, 1.0, 1.0),
                "font.family": "serif"}
        plt.rcParams.update(plt_params_dict)


    def get_cycleways(self):
        """
        Creates all cycleways in a city (networkx.MultiDiGraph).
        """
        useful_tags = ox.settings.useful_tags_way + ['cycleway']
        ox.config(use_cache=True, log_console=True, useful_tags_way=useful_tags)
        cycleways = ox.graph_from_place(query = self.city_name, network_type='bike', simplify=False)
        non_cycleways = [(u, v, k) for u, v, k, d in cycleways.edges(keys=True, data=True) if not ('cycleway' in d or d['highway']=='cycleway')]
        cycleways.remove_edges_from(non_cycleways)
        self.cycleways = ox.utils_graph.remove_isolated_nodes(cycleways)


    def get_footprints(self):
        """
        UNSTABLE
        Returns footprints of buildings. Seems to timeout for larger cities.
        """
        tags = {"building": True}
        footprints = ox.geometries_from_place(self.city_name, tags)
        # ox.plot_footprints(footprints, ax=ax,color='dimgrey')

        return footprints


    def get_city(self):
        """
        Creates cycleways and road info (networkx.MultiDiGraph) and city area (geopandas.geodataframe.GeoDataFrame).
        """
        print(f"Loading data for {self.city_name}. May take a few minutes.")

        # get cycleways 
        self.get_cycleways()
        # get city area
        self.city_area = ox.geocode_to_gdf(self.city_name)
        # get roads
        self.roads = ox.graph_from_place(self.city_name, network_type='drive')


    def calc_road_cycleway_ratio(self):
        """
        Calculates ratio of cycleways to roads. Uses osmnx.basic_stats.
        cycleways: (networkx.MultiDiGraph) cycleways info from get_city func, or osmnx.graph_from_place
        roads: (networkx.MultiDiGraph) road info from get_city func, or ox.graph_from_place
        """

        if self.cycleways is None:
            self.cycleways = self.get_cycleways()
        if self.roads is None:
            self.roads = ox.graph_from_place(self.city_name, network_type='drive')        
        
        c = ox.basic_stats(self.cycleways)
        r = ox.basic_stats(self.roads)
        self.rc_ratio = r['edge_length_total']/c['edge_length_total']


    def plot_cycleways(
        self,
        road_cycleway_ratio_subtitle: bool = True, 
        signature: bool = True,
        save_figure = True,
        extension = '.png'):
        """
        Plots cycleways overlaid city area. Returns matplotlib fig,ax.
        cycleways: (networkx.MultiDiGraph) cycleways info from get_city func, or osmnx.graph_from_place
        roads: (networkx.MultiDiGraph) road info from get_city func, or ox.graph_from_place
        city_area: (geopandas.geodataframe.GeoDataFrame) city area from get_city func, or osmnx.geocode_to_gdf
        road_cycleway_ratio: (float) ratio of roads to cycleways in the city
        signature: (bool) set to false to remove signature.
        """
        fig, ax = plt.subplots(figsize=(4,4))

        if road_cycleway_ratio_subtitle is False:
            ax.set_title(self.city_name,fontsize=12)

        elif road_cycleway_ratio_subtitle is True:
            # make subtitle in hacky way
            if self.rc_ratio is None:
                self.calc_road_cycleway_ratio()

            rc_ratio_round = round(self.rc_ratio)
            fig.text(s=f'Road to Cycleway Ratio is {rc_ratio_round}:1',
                    x=.5, y=1.01, transform = ax.transAxes,
                    horizontalalignment='center',verticalalignment='bottom',
                    color='k',fontsize=6
                    )

            fig.text(s=self.city_name,
                    x=.5, y=1.05, transform = ax.transAxes,
                    horizontalalignment='center',verticalalignment='bottom',
                    color='k',fontsize=12
                    )
        
        if self.city_area is not None:
            self.city_area.plot(ax=ax, facecolor='gainsboro')
        if self.roads is not None:
            ox.plot_graph(self.roads,ax=ax,node_size=0,edge_linewidth=.25,edge_color='dimgrey')
        if self.cycleways is not None:
            ox.plot_graph(self.cycleways,ax=ax,node_size=0,edge_linewidth=.85,edge_color='limegreen')
        
        if signature is True:
            fig.text(s="@WThyer\nOpenStreetMap", 
                    x=1, y=-.01, transform = ax.transAxes,
                    horizontalalignment='right',verticalalignment='top',
                    color='k',fontsize=5
                    )

        ax.axis('off')
        plt.tight_layout()
        
        if save_figure is True:
            self.savefig(fig=fig,extension=extension)

        return fig, ax


    def savefig(self, fig, extension='.png'):
        filename = f'examples/{extension[1:]}/{self.city_name}{extension}'
        fig.savefig(filename,dpi=1000,facecolor='w',transparent=False)