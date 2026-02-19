#!/usr/bin/env python3

import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os
import pandas as pd
from collections import defaultdict
import math

class AdvancedNetworkMapper:
    def __init__(self):
        self.graph = nx.Graph()
        self.node_data = {}
        self.edge_data = {}
        self.communities = {}
        
    def add_profile(self, username: str, platform: str, profile_data: Dict):
        """Add a profile as a node to the network"""
        node_id = f"{platform}:{username}"
        
        self.graph.add_node(node_id)
        self.node_data[node_id] = {
            "username": username,
            "platform": platform,
            "followers": profile_data.get("followers", 0),
            "following": profile_data.get("following", 0),
            "posts": profile_data.get("posts", 0),
            "verified": profile_data.get("verified", False),
            "bio": profile_data.get("bio", ""),
            "profile_url": profile_data.get("profile_url", ""),
            "risk_score": profile_data.get("risk_score", 0),
            "authenticity_score": profile_data.get("authenticity_score", 100)
        }
    
    def add_connection(self, user1: str, platform1: str, user2: str, platform2: str, 
                      connection_type: str = "follows", strength: float = 1.0):
        """Add connection between two profiles"""
        node1 = f"{platform1}:{user1}"
        node2 = f"{platform2}:{user2}"
        
        if node1 in self.graph.nodes and node2 in self.graph.nodes:
            self.graph.add_edge(node1, node2)
            edge_key = (node1, node2)
            self.edge_data[edge_key] = {
                "type": connection_type,
                "strength": strength,
                "discovered_at": datetime.now().isoformat()
            }
    
    def detect_communities(self) -> Dict:
        """Detect communities/clusters in the network"""
        try:
            communities = nx.community.greedy_modularity_communities(self.graph)
            self.communities = {}
            
            for i, community in enumerate(communities):
                self.communities[f"community_{i}"] = {
                    "members": list(community),
                    "size": len(community),
                    "platforms": list(set(node.split(':')[0] for node in community)),
                    "risk_level": self._calculate_community_risk(community)
                }
            
            return self.communities
        except:
            return {}
    
    def _calculate_community_risk(self, community: set) -> str:
        """Calculate risk level for a community"""
        total_risk = 0
        count = 0
        
        for node in community:
            if node in self.node_data:
                risk_score = self.node_data[node].get("risk_score", 0)
                auth_score = self.node_data[node].get("authenticity_score", 100)
                total_risk += risk_score + (100 - auth_score)
                count += 1
        
        if count == 0:
            return "Unknown"
        
        avg_risk = total_risk / count
        if avg_risk > 150:
            return "High"
        elif avg_risk > 100:
            return "Medium"
        else:
            return "Low"
    
    def analyze_network_metrics(self) -> Dict:
        """Analyze various network metrics"""
        if len(self.graph.nodes) == 0:
            return {"error": "No nodes in network"}
        
        metrics = {
            "basic_stats": {
                "total_nodes": len(self.graph.nodes),
                "total_edges": len(self.graph.edges),
                "density": nx.density(self.graph),
                "is_connected": nx.is_connected(self.graph)
            },
            "centrality_measures": self._calculate_centrality(),
            "platform_distribution": self._analyze_platform_distribution(),
            "risk_analysis": self._analyze_network_risks(),
            "influence_scores": self._calculate_influence_scores()
        }
        
        if len(self.graph.nodes) > 1:
            metrics["clustering"] = {
                "average_clustering": nx.average_clustering(self.graph),
                "transitivity": nx.transitivity(self.graph)
            }
        
        return metrics
    
    def _calculate_centrality(self) -> Dict:
        """Calculate various centrality measures"""
        centrality = {}
        
        if len(self.graph.nodes) > 1:
            centrality["degree"] = nx.degree_centrality(self.graph)
            centrality["betweenness"] = nx.betweenness_centrality(self.graph)
            centrality["closeness"] = nx.closeness_centrality(self.graph)
            centrality["eigenvector"] = nx.eigenvector_centrality(self.graph, max_iter=1000)
        
        return centrality
    
    def _analyze_platform_distribution(self) -> Dict:
        """Analyze distribution across platforms"""
        platform_counts = defaultdict(int)
        platform_followers = defaultdict(int)
        
        for node_id, data in self.node_data.items():
            platform = data["platform"]
            platform_counts[platform] += 1
            platform_followers[platform] += data.get("followers", 0)
        
        return {
            "platform_counts": dict(platform_counts),
            "platform_followers": dict(platform_followers),
            "dominant_platform": max(platform_counts.items(), key=lambda x: x[1])[0] if platform_counts else None
        }
    
    def _analyze_network_risks(self) -> Dict:
        """Analyze risks in the network"""
        high_risk_nodes = []
        suspicious_connections = []
        
        for node_id, data in self.node_data.items():
            risk_score = data.get("risk_score", 0)
            auth_score = data.get("authenticity_score", 100)
            
            if risk_score > 70 or auth_score < 50:
                high_risk_nodes.append({
                    "node": node_id,
                    "risk_score": risk_score,
                    "authenticity_score": auth_score
                })
        
        # Check for suspicious connection patterns
        for edge, edge_data in self.edge_data.items():
            if edge_data.get("strength", 1.0) > 0.9:  # Very strong connections might be suspicious
                suspicious_connections.append({
                    "connection": edge,
                    "type": edge_data.get("type", "unknown"),
                    "strength": edge_data.get("strength", 1.0)
                })
        
        return {
            "high_risk_nodes": high_risk_nodes,
            "suspicious_connections": suspicious_connections,
            "overall_risk_level": self._calculate_overall_risk(high_risk_nodes)
        }
    
    def _calculate_influence_scores(self) -> Dict:
        """Calculate influence scores for nodes"""
        influence_scores = {}
        
        for node_id, data in self.node_data.items():
            followers = data.get("followers", 0)
            degree = self.graph.degree(node_id) if node_id in self.graph else 0
            verified = data.get("verified", False)
            
            # Calculate influence based on followers, connections, and verification
            base_score = math.log10(max(1, followers)) * 10
            connection_bonus = degree * 5
            verification_bonus = 20 if verified else 0
            
            influence_scores[node_id] = min(100, base_score + connection_bonus + verification_bonus)
        
        return influence_scores
    
    def _calculate_overall_risk(self, high_risk_nodes: List) -> str:
        """Calculate overall network risk level"""
        if not self.node_data:
            return "Unknown"
        
        risk_ratio = len(high_risk_nodes) / len(self.node_data)
        
        if risk_ratio > 0.3:
            return "High"
        elif risk_ratio > 0.1:
            return "Medium"
        else:
            return "Low"
    
    def generate_interactive_visualization(self, output_path: str = None) -> str:
        """Generate interactive network visualization using Plotly"""
        if len(self.graph.nodes) == 0:
            return "No data to visualize"
        
        # Calculate layout
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # Prepare node data
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        
        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            data = self.node_data.get(node, {})
            platform = data.get("platform", "unknown")
            username = data.get("username", "unknown")
            followers = data.get("followers", 0)
            risk_score = data.get("risk_score", 0)
            
            node_text.append(f"{platform}: {username}<br>Followers: {followers:,}<br>Risk: {risk_score}")
            
            # Color by platform
            platform_colors = {
                "instagram": "red",
                "twitter": "blue", 
                "youtube": "orange",
                "tiktok": "purple",
                "linkedin": "green"
            }
            node_color.append(platform_colors.get(platform, "gray"))
            
            # Size by followers (log scale)
            size = max(10, min(50, math.log10(max(1, followers)) * 5))
            node_size.append(size)
        
        # Prepare edge data
        edge_x = []
        edge_y = []
        
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create the plot
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='lightgray'),
            hoverinfo='none',
            mode='lines',
            name='Connections'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=node_text,
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            name='Profiles'
        ))
        
        fig.update_layout(
            title="Social Media Network Analysis",
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Interactive Network Visualization",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color="gray", size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        # Save the plot
        if output_path is None:
            output_path = f"/home/kali/Desktop/tools/osint-eye/reports/network_viz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        fig.write_html(output_path)
        return output_path
    
    def generate_static_visualization(self, output_path: str = None) -> str:
        """Generate static network visualization using matplotlib"""
        if len(self.graph.nodes) == 0:
            return "No data to visualize"
        
        plt.figure(figsize=(12, 8))
        
        # Calculate layout
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # Prepare node colors and sizes
        node_colors = []
        node_sizes = []
        
        platform_color_map = {
            "instagram": "red",
            "twitter": "blue",
            "youtube": "orange", 
            "tiktok": "purple",
            "linkedin": "green"
        }
        
        for node in self.graph.nodes():
            data = self.node_data.get(node, {})
            platform = data.get("platform", "unknown")
            followers = data.get("followers", 0)
            
            node_colors.append(platform_color_map.get(platform, "gray"))
            size = max(100, min(1000, math.log10(max(1, followers)) * 100))
            node_sizes.append(size)
        
        # Draw the network
        nx.draw_networkx_edges(self.graph, pos, alpha=0.5, edge_color='lightgray')
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, 
                              node_size=node_sizes, alpha=0.8)
        
        # Add labels
        labels = {}
        for node in self.graph.nodes():
            data = self.node_data.get(node, {})
            username = data.get("username", "unknown")
            labels[node] = username
        
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)
        
        plt.title("Social Media Network Analysis", size=16)
        plt.axis('off')
        
        # Add legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                    markerfacecolor=color, markersize=10, label=platform.title())
                          for platform, color in platform_color_map.items()]
        plt.legend(handles=legend_elements, loc='upper right')
        
        # Save the plot
        if output_path is None:
            output_path = f"/home/kali/Desktop/tools/osint-eye/reports/network_static_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def export_network_data(self, output_path: str = None) -> str:
        """Export network data to various formats"""
        if output_path is None:
            output_path = f"/home/kali/Desktop/tools/osint-eye/data/network_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Export as JSON
        network_data = {
            "nodes": self.node_data,
            "edges": {f"{edge[0]}-{edge[1]}": data for edge, data in self.edge_data.items()},
            "communities": self.communities,
            "metrics": self.analyze_network_metrics(),
            "exported_at": datetime.now().isoformat()
        }
        
        json_path = f"{output_path}.json"
        with open(json_path, 'w') as f:
            json.dump(network_data, f, indent=2)
        
        # Export as CSV (nodes)
        if self.node_data:
            df_nodes = pd.DataFrame.from_dict(self.node_data, orient='index')
            df_nodes.to_csv(f"{output_path}_nodes.csv")
        
        # Export as GraphML for other tools
        nx.write_graphml(self.graph, f"{output_path}.graphml")
        
        return json_path
    
    def find_shortest_path(self, source: str, target: str) -> Dict:
        """Find shortest path between two nodes"""
        try:
            path = nx.shortest_path(self.graph, source, target)
            path_length = len(path) - 1
            
            return {
                "path": path,
                "length": path_length,
                "exists": True,
                "path_details": [self.node_data.get(node, {}) for node in path]
            }
        except nx.NetworkXNoPath:
            return {"exists": False, "reason": "No path found"}
        except nx.NodeNotFound as e:
            return {"exists": False, "reason": f"Node not found: {str(e)}"}
    
    def identify_key_influencers(self, top_n: int = 5) -> List[Dict]:
        """Identify key influencers in the network"""
        influence_scores = self._calculate_influence_scores()
        centrality = self._calculate_centrality()
        
        influencers = []
        for node_id in self.graph.nodes():
            data = self.node_data.get(node_id, {})
            
            influencer_data = {
                "node_id": node_id,
                "username": data.get("username", "unknown"),
                "platform": data.get("platform", "unknown"),
                "followers": data.get("followers", 0),
                "influence_score": influence_scores.get(node_id, 0),
                "degree_centrality": centrality.get("degree", {}).get(node_id, 0),
                "betweenness_centrality": centrality.get("betweenness", {}).get(node_id, 0),
                "verified": data.get("verified", False)
            }
            influencers.append(influencer_data)
        
        # Sort by influence score
        influencers.sort(key=lambda x: x["influence_score"], reverse=True)
        
        return influencers[:top_n]