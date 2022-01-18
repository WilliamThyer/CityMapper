import osmnx as ox
import numpy as np
import matplotlib.pyplot as plt

class CityMapper:

    def __init__(self):

        self.buildings = None
        self.cycleways = None
        self.roads = None
        self.city_area = None
        self.water = None
        self.green = None
        self.rc_ratio = None

        self.colors_dict = {
            'city_area': 'gainsboro',
            'buildings': 'dimgrey',
            'roads': 'dimgrey',
            'cycleways': 'limegreen',
            'water': 'dodgerblue',
            'green': 'olivedrab'}

        self.green_tags = {
            'landuse':['village_green','grass','forest','cemetary','greenfield','meadow','orchard','vineyard'], 
            'leisure':['park','garden','golf_course','nature_reserve'], 
            'natural':['shrubbery','scrub','fell','grassland','wood'],
            'tourism': 'camp_site',
            'amenity': 'grave_yard'}
        
        self.water_tags = {
            'water': True,
            'natural': ['water', 'bay', 'spring', 'strait', 'wetland'],
            'place': ['sea', 'ocean'],
            'waterway': ['river', 'riverbank', 'stream', 'tidal_channel', 'canal', 'drain', 'ditch', 'fairway']
        }

        self.city_dict = {
            'buildings': False,
            'roads': True,
            'cycleways': True,
            'water': True,
            'green': False}

        plt_params_dict = {
            "figure.facecolor":  (1.0, 1.0, 1.0, 1.0),
            "font.family": "serif"}
        plt.rcParams.update(plt_params_dict)


    def load_city(
        self,
        city_name: str,
        city_elements: dict = None,
        city_limits: bool = True):

        """
        Creates info for plotting.
        cycleways: (networkx.MultiDiGraph) cycleways info from get_city func, or osmnx.graph_from_place
        roads: (networkx.MultiDiGraph) road info from get_city func, or ox.graph_from_place
        city_area: (geopandas.geodataframe.GeoDataFrame) city area from get_city func, or osmnx.geocode_to_gdf
        green
        water
        buildings
        """
        print(f"Loading data for {city_name}. May take a few minutes.")

        self.city_name = city_name
        self.city_limits = city_limits

        if city_elements is None:
            city_elements = {}
        self.city_dict.update(city_elements)

        self.city_area = ox.geocode_to_gdf(self.city_name)
        self.west, self.south, self.east, self.north = self.city_area.total_bounds

        if self.city_limits is True:
            self._get_city_data_within_city_limits()
        else:
            self._get_city_data_within_rectangle()

    def _get_city_data_within_city_limits(self):

        if self.city_dict['cycleways'] is True:
            self.cycleways = self._get_cycleways()
        if self.city_dict['roads'] is True:
            self.roads = ox.graph_from_place(self.city_name, network_type='drive')
        if self.city_dict['water'] is True:
            self.water = ox.geometries_from_polygon(self.city_area.unary_union, tags=self.water_tags) #{'water':['river','lake'],"natural":["water"]}
        if self.city_dict['green'] is True:
            self.green = ox.geometries_from_polygon(self.city_area.unary_union, tags=self.green_tags)
        if self.city_dict['buildings'] is True:
            self.buildings = ox.geometries_from_place(self.city_name, tags = {"building": True, 'landuse': 'construction'})
    
    def _get_city_data_within_rectangle(self):
        
        if self.city_dict['cycleways'] is True:
            self.cycleways = self._get_cycleways()
        if self.city_dict['roads'] is True:
            self.roads = ox.graph_from_bbox(self.north, self.south, self.east, self.west, network_type='drive')
        if self.city_dict['water'] is True:
            self.water = ox.geometries.geometries_from_bbox(self.north, self.south, self.east, self.west, tags=self.water_tags)
        if self.city_dict['green'] is True:
            self.green = ox.geometries.geometries_from_bbox(self.north, self.south, self.east, self.west, tags=self.green_tags)
        if self.city_dict['buildings'] is True:
            self.buildings = ox.geometries.geometries_from_bbox(self.north, self.south, self.east, self.west, tags={"building": True, 'landuse': 'construction'})

    def _get_cycleways(self):
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
        cycleways = ox.utils_graph.remove_isolated_nodes(cycleways)
        
        return cycleways

    def plot_city(
        self,
        road_cycleway_ratio_subtitle: bool = False,
        colors: dict = None,
        plt_params_dict: dict = None,
        ):

        """
        Plots cycleways overlaid city area. Returns matplotlib fig, ax.        
        
        """
        fig, ax = plt.subplots(figsize=(6,6))

        if plt_params_dict is not None:
            plt.rcParams.update(plt_params_dict)

        self._set_title(ax, road_cycleway_ratio_subtitle)

        if colors is None:
            colors = {}
        self.colors_dict.update(colors)

        self._plot_city_area(ax)
        self._plot_buildings(ax)
        self._plot_green(ax)
        self._plot_water(ax)
        self._plot_roads(ax)
        self._plot_cycleways(ax)
        
        fig.text(s="William Thyer\nOpenStreetMap", 
            x=1, y=-.01, transform = ax.transAxes,
            horizontalalignment='right',verticalalignment='top',
            color='k',fontsize=5)

        ax.axis('off')
        plt.tight_layout()

        return fig

    def _plot_city_area(self, ax):

        if (self.colors_dict['city_area'] is not None) & (self.city_area is not None):
            self.city_area.plot(
                ax=ax, 
                facecolor=self.colors_dict['city_area'])

    def _plot_green(self, ax):

        if (self.colors_dict['green'] is not None) & (self.green is not None):
            ox.plot_footprints(
                self.green, ax=ax,
                color=self.colors_dict['green'], 
                bgcolor='white',
                show=False, close=False)

    def _plot_water(self, ax):

        if (self.colors_dict['water'] is not None) & (self.water is not None):
            ox.plot_footprints(
                self.water, ax=ax,
                color=self.colors_dict['water'], 
                bgcolor='white',
                show=False, close=False)
    
    def _plot_roads(self, ax):

        if (self.colors_dict['roads'] is not None) & (self.roads is not None):
        
            ox.plot_graph(
                self.roads, ax=ax,
                node_size=0,
                edge_linewidth=.25,
                edge_color=self.colors_dict['roads'],
                show=False, close=False)
    
    def _plot_buildings(self, ax):

        if (self.colors_dict['buildings'] is not None) & (self.buildings is not None):
            ox.plot_footprints(
                self.buildings, ax=ax,
                color=self.colors_dict['buildings'],
                show=False, close=False)
    
    def _plot_cycleways(self, ax):

        if (self.colors_dict['cycleways'] is not None) & (self.cycleways is not None):
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
                    edge_color=self.colors_dict['cycleways'],
                    show=False, close=False)

    def _set_title(self, ax, road_cycleway_ratio_subtitle):
        
        if road_cycleway_ratio_subtitle is False:
            ax.set_title(self.city_name,fontsize=12)

        else:
            if (self.roads is None) or (self.cycleways is None):
                print('Roads and cycleways must be loaded. Ratio not included.')
                ax.set_title(self.city_name,fontsize=12)
                return

            self.calc_road_cycleway_ratio()

            rc_ratio_round = round(self.rc_ratio)
            
            plt.suptitle(self.city_name, fontsize=14, y=.955)
            ax.set_title(f'Road to Cycleway Ratio is {rc_ratio_round}:1',fontsize=8)


    def calc_road_cycleway_ratio(self):
        """
        Calculates ratio of cycleways to roads. Uses osmnx.basic_stats.
        cycleways: (networkx.MultiDiGraph) cycleways info from get_city func, or osmnx.graph_from_place
        roads: (networkx.MultiDiGraph) road info from get_city func, or ox.graph_from_place
        rc_ratio: (float) ratio of roads to cycleways in the city
        """
        
        c = ox.basic_stats(self.cycleways)
        r = ox.basic_stats(self.roads)
        self.rc_ratio = r['edge_length_total']/c['edge_length_total']

    def savefig(self, fig, extension=['png','pdf']):
        if not isinstance(extension, list):
            extension = [extension]
        for ext in extension:
            filename = f'examples/{ext}/{self.city_name}.{ext}'
            fig.savefig(filename,dpi=1000,facecolor='w',transparent=False,bbox_inches='tight')