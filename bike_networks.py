import osmnx as ox
import numpy as np
import matplotlib.pyplot as plt

class BikeNetworkMapper:

    def __init__(
        self,
        city_name: str,
        city_limits: bool = False,
        plt_params_dict: dict = None):

        self.city_name = city_name
        self.city_limits = city_limits

        self.buildings = None
        self.cycleways = None
        self.roads = None
        self.city_area = None
        self.water = None
        self.green = None
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

        if self.city_limits is True:
            cycleways = ox.graph_from_place(query = self.city_name, network_type='bike', simplify=False)
        else:
            cycleways = ox.graph_from_bbox(self.north, self.south, self.east, self.west, network_type='bike', simplify=False)

        non_cycleways = [(u, v, k) for u, v, k, d in cycleways.edges(keys=True, data=True) if not ('cycleway' in d or d['highway']=='cycleway')]
        cycleways.remove_edges_from(non_cycleways)
        self.cycleways = ox.utils_graph.remove_isolated_nodes(cycleways)


    def get_city(
        self, 
        city_elements: dict = {}):
        """
        Creates info for plotting.
        cycleways (networkx.MultiDiGraph)
        roads (networkx.MultiDiGraph) 
        city_area (geopandas.geodataframe.GeoDataFrame)
        green
        water
        buildings
        """
        print(f"Loading data for {self.city_name}. May take a few minutes.")

        city_dict = {
            'buildings': True,
            'roads': True,
            'cycleways': True,
            'water': True,
            'green': True}

        city_dict.update(city_elements)

        self.city_area = ox.geocode_to_gdf(self.city_name)
        self.west, self.south, self.east, self.north = self.city_area.total_bounds

        if city_dict['cycleways'] is True:
            self.get_cycleways()

        green_tags = {
            'landuse':['village_green','grass','forest','cemetary','greenfield','meadow','orchard','vineyard'], 
            'leisure':['park','garden','golf_course','nature_reserve'], 
            'natural':['shrubbery','scrub','fell','grassland','wood'],
            'tourism': 'camp_site',
            'amenity': 'grave_yard'}

        if self.city_limits is True:
            if city_dict['roads'] is True:
                self.roads = ox.graph_from_place(self.city_name, network_type='drive')
            if city_dict['water'] is True:
                self.water = ox.geometries_from_polygon(self.city_area.unary_union, tags={'water':['river','lake'],"natural":["water"]})
            if city_dict['green'] is True:
                self.green = ox.geometries_from_polygon(self.city_area.unary_union, tags=green_tags)
            if city_dict['buildings'] is True:
                self.buildings = ox.geometries_from_place(self.city_name, tags = {"building": True, 'landuse': 'construction'})
        
        else:
            if city_dict['roads'] is True:
                self.roads = ox.graph_from_bbox(self.north, self.south, self.east, self.west, network_type='drive')
            if city_dict['water'] is True:
                self.water = ox.geometries.geometries_from_bbox(self.north, self.south, self.east, self.west, tags={'water':['river','lake'],"natural":["water"]})
            if city_dict['green'] is True:
                self.green = ox.geometries.geometries_from_bbox(self.north, self.south, self.east, self.west, tags=green_tags)
            if city_dict['buildings'] is True:
                self.buildings = ox.geometries.geometries_from_bbox(self.north, self.south, self.east, self.west, tags={"building": True, 'landuse': 'construction'})


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
        colors: dict = {},
        signature:bool = True,
        save_figure:bool = True,
        extension:list = ['png','pdf']):
        """
        Plots cycleways overlaid city area. Returns matplotlib fig,ax.
        cycleways: (networkx.MultiDiGraph) cycleways info from get_city func, or osmnx.graph_from_place
        roads: (networkx.MultiDiGraph) road info from get_city func, or ox.graph_from_place
        city_area: (geopandas.geodataframe.GeoDataFrame) city area from get_city func, or osmnx.geocode_to_gdf
        road_cycleway_ratio: (float) ratio of roads to cycleways in the city
        signature: (bool) set to false to remove signature.
        """
        fig, ax = plt.subplots(figsize=(6,6))

        if road_cycleway_ratio_subtitle is False:
            ax.set_title(self.city_name,fontsize=12)

        elif road_cycleway_ratio_subtitle is True:

            if self.rc_ratio is None:
                self.calc_road_cycleway_ratio()

            rc_ratio_round = round(self.rc_ratio)

            plt.title(f'Road to Cycleway Ratio is {rc_ratio_round}:1',fontsize=8)
            plt.suptitle(self.city_name,fontsize=14, y=.955)

        colors_dict = {
            'city_area': 'gainsboro',
            'buildings': 'dimgrey',
            'roads': 'dimgrey',
            'cycleways': 'limegreen',
            'water': 'dodgerblue',
            'green': 'olivedrab'}

        colors_dict.update(colors)

        if (colors_dict['city_area'] is not None) & (self.city_area is not None):
            self.city_area.plot(
                ax=ax, 
                facecolor=colors_dict['city_area'])

        if (colors_dict['green'] is not None) & (self.green is not None):
            print('y')
            ox.plot_footprints(
                self.green, ax=ax,
                color=colors_dict['green'], 
                bgcolor='white',
                show=False, close=False)

        if (colors_dict['water'] is not None) & (self.water is not None):
            ox.plot_footprints(
                self.water, ax=ax,
                color=colors_dict['water'], 
                bgcolor='white',
                show=False, close=False)
        
        if (colors_dict['buildings'] is not None) & (self.buildings is not None):
            ox.plot_footprints(
                self.buildings, ax=ax,
                color=colors_dict['buildings'],
                show=False, close=False)

        if (colors_dict['roads'] is not None) & (self.roads is not None):
            ox.plot_graph(
                self.roads,ax=ax,
                node_size=0,
                edge_linewidth=.25,
                edge_color=colors_dict['roads'],
                show=False, close=False)

        if (colors_dict['cycleways'] is not None) & (self.cycleways is not None):
            ox.plot_graph(
                self.cycleways,ax=ax,
                node_size=0,
                edge_linewidth=.9,
                edge_color='white',
                show=False, close=False)
            
            ox.plot_graph(
                self.cycleways,ax=ax,
                node_size=0,
                edge_linewidth=.6,
                edge_color=colors_dict['cycleways'],
                show=False, close=False)
        
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


    def savefig(self, fig, extension=['png']):
        if not isinstance(extension, list):
            extension = [extension]
        for ext in extension:
            filename = f'examples/{ext}/{self.city_name}.{ext}'
            fig.savefig(filename,dpi=1000,facecolor='w',transparent=False,bbox_inches='tight')