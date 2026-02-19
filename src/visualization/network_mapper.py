import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.offline as pyo
from typing import Dict, List, Any, Tuple
import json
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger()

class NetworkMapper:
    def __init__(self):
        self.graph = nx.Graph()
        self.node_colors = {
            'instagram': '#E4405F',
            'twitter': '#1DA1F2', 
            'youtube': '#FF0000',
            'tiktok': '#000000',
            'linkedin': '#0077B5'
        }
    
    def build_network_from_data(self, profiles_data: List[Dict[str, Any]]) -> nx.Graph:
        """Build network graph from profile data"""
        self.graph.clear()
        
        for profile_data in profiles_data:
            platform = profile_data.get('platform', 'unknown')
            username = profile_data.get('username', '')
            
            if not username:
                continue
            
            # Add main profile node
            node_id = f"{platform}:{username}"
            self.graph.add_node(node_id, 
                               platform=platform,
                               username=username,
                               display_name=profile_data.get('display_name', username),
                               followers=profile_data.get('followers', 0),
                               node_type='profile')
            
            # Add connections from mentions and interactions
            posts = profile_data.get('posts', [])
            for post in posts:
                mentions = post.get('mentions', [])
                for mention in mentions:
                    mention_id = f"{platform}:{mention}"
                    
                    # Add mentioned user as node
                    if not self.graph.has_node(mention_id):
                        self.graph.add_node(mention_id,
                                          platform=platform,
                                          username=mention,
                                          display_name=mention,
                                          node_type='mention')
                    
                    # Add edge between main profile and mentioned user
                    if self.graph.has_edge(node_id, mention_id):
                        self.graph[node_id][mention_id]['weight'] += 1
                    else:
                        self.graph.add_edge(node_id, mention_id, weight=1, relation_type='mention')
        
        return self.graph
    
    def add_cross_platform_connections(self, cross_platform_data: Dict[str, List[str]]):
        """Add connections between same users across platforms"""
        for username, platforms in cross_platform_data.items():
            platform_nodes = [f"{platform}:{username}" for platform in platforms]
            
            # Connect all platform nodes for the same user
            for i, node1 in enumerate(platform_nodes):
                for node2 in platform_nodes[i+1:]:
                    if self.graph.has_node(node1) and self.graph.has_node(node2):
                        self.graph.add_edge(node1, node2, weight=5, relation_type='same_user')
    
    def calculate_centrality_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate various centrality metrics"""
        if len(self.graph) == 0:
            return {}
        
        metrics = {}
        
        try:
            # Degree centrality
            degree_centrality = nx.degree_centrality(self.graph)
            
            # Betweenness centrality
            betweenness_centrality = nx.betweenness_centrality(self.graph)
            
            # Closeness centrality
            closeness_centrality = nx.closeness_centrality(self.graph)
            
            # PageRank
            pagerank = nx.pagerank(self.graph)
            
            # Combine all metrics
            for node in self.graph.nodes():
                metrics[node] = {
                    'degree_centrality': degree_centrality.get(node, 0),
                    'betweenness_centrality': betweenness_centrality.get(node, 0),
                    'closeness_centrality': closeness_centrality.get(node, 0),
                    'pagerank': pagerank.get(node, 0)
                }
        
        except Exception as e:
            logger.error(f"Centrality calculation error: {e}")
        
        return metrics
    
    def detect_communities(self) -> Dict[int, List[str]]:
        """Detect communities in the network"""
        communities = {}
        
        try:
            if len(self.graph) > 1:
                # Use Louvain community detection
                import networkx.algorithms.community as nx_comm
                community_generator = nx_comm.greedy_modularity_communities(self.graph)
                
                for i, community in enumerate(community_generator):
                    communities[i] = list(community)
        
        except Exception as e:
            logger.error(f"Community detection error: {e}")
        
        return communities
    
    def generate_matplotlib_visualization(self, output_path: str = "reports/network_graph.png"):
        """Generate static network visualization using matplotlib"""
        if len(self.graph) == 0:
            logger.warning("No graph data to visualize")
            return None
        
        try:
            plt.figure(figsize=(15, 10))
            
            # Calculate layout
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
            
            # Separate nodes by type
            profile_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'profile']
            mention_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'mention']
            
            # Draw profile nodes (larger)
            if profile_nodes:
                profile_colors = [self.node_colors.get(self.graph.nodes[n].get('platform', 'unknown'), '#gray') for n in profile_nodes]
                nx.draw_networkx_nodes(self.graph, pos, nodelist=profile_nodes, 
                                     node_color=profile_colors, node_size=1000, alpha=0.8)
            
            # Draw mention nodes (smaller)
            if mention_nodes:
                mention_colors = [self.node_colors.get(self.graph.nodes[n].get('platform', 'unknown'), '#lightgray') for n in mention_nodes]
                nx.draw_networkx_nodes(self.graph, pos, nodelist=mention_nodes,
                                     node_color=mention_colors, node_size=300, alpha=0.6)
            
            # Draw edges
            nx.draw_networkx_edges(self.graph, pos, alpha=0.5, width=0.5)
            
            # Draw labels for important nodes only
            important_nodes = {n: self.graph.nodes[n].get('username', n) 
                             for n in self.graph.nodes() 
                             if self.graph.degree(n) > 1}
            nx.draw_networkx_labels(self.graph, pos, labels=important_nodes, font_size=8)
            
            plt.title("Social Media Network Analysis", size=16)
            plt.axis('off')
            
            # Add legend
            legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=color, markersize=10, label=platform.title())
                             for platform, color in self.node_colors.items()]
            plt.legend(handles=legend_elements, loc='upper right')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Matplotlib visualization error: {e}")
            return None
    
    def generate_interactive_visualization(self, output_path: str = "reports/interactive_network.html"):
        """Generate interactive network visualization using Plotly"""
        if len(self.graph) == 0:
            logger.warning("No graph data to visualize")
            return None
        
        try:
            # Calculate layout
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
            
            # Prepare edge traces
            edge_x = []
            edge_y = []
            for edge in self.graph.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(x=edge_x, y=edge_y,
                                  line=dict(width=0.5, color='#888'),
                                  hoverinfo='none',
                                  mode='lines')
            
            # Prepare node traces
            node_x = []
            node_y = []
            node_text = []
            node_colors = []
            node_sizes = []
            
            for node in self.graph.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                # Node info
                node_data = self.graph.nodes[node]
                platform = node_data.get('platform', 'unknown')
                username = node_data.get('username', node)
                display_name = node_data.get('display_name', username)
                followers = node_data.get('followers', 0)
                degree = self.graph.degree(node)
                
                node_text.append(f"{display_name}<br>Platform: {platform}<br>Followers: {followers}<br>Connections: {degree}")
                node_colors.append(self.node_colors.get(platform, '#gray'))
                
                # Size based on degree and followers
                size = max(10, min(50, degree * 5 + (followers / 10000)))
                node_sizes.append(size)
            
            node_trace = go.Scatter(x=node_x, y=node_y,
                                  mode='markers',
                                  hoverinfo='text',
                                  text=node_text,
                                  marker=dict(size=node_sizes,
                                            color=node_colors,
                                            line=dict(width=2, color='white')))
            
            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               title='Interactive Social Media Network',
                               titlefont_size=16,
                               showlegend=False,
                               hovermode='closest',
                               margin=dict(b=20,l=5,r=5,t=40),
                               annotations=[ dict(
                                   text="Network visualization of social media connections",
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002,
                                   xanchor='left', yanchor='bottom',
                                   font=dict(color='gray', size=12)
                               )],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
            
            # Save to HTML
            pyo.plot(fig, filename=output_path, auto_open=False)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Interactive visualization error: {e}")
            return None
    
    def export_network_data(self, output_path: str = "reports/network_data.json"):
        """Export network data to JSON"""
        try:
            network_data = {
                'nodes': [],
                'edges': [],
                'statistics': {
                    'total_nodes': len(self.graph.nodes()),
                    'total_edges': len(self.graph.edges()),
                    'density': nx.density(self.graph),
                    'connected_components': nx.number_connected_components(self.graph)
                }
            }
            
            # Export nodes
            for node in self.graph.nodes(data=True):
                node_data = {
                    'id': node[0],
                    'attributes': node[1],
                    'degree': self.graph.degree(node[0])
                }
                network_data['nodes'].append(node_data)
            
            # Export edges
            for edge in self.graph.edges(data=True):
                edge_data = {
                    'source': edge[0],
                    'target': edge[1],
                    'attributes': edge[2]
                }
                network_data['edges'].append(edge_data)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(network_data, f, indent=2, ensure_ascii=False)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Network export error: {e}")
            return None