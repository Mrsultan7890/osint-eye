#!/usr/bin/env python3

import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import sqlite3
import yaml
from pathlib import Path
import re

class AdvancedExporter:
    def __init__(self):
        self.supported_formats = [
            "json", "csv", "xml", "xlsx", "yaml", 
            "sqlite", "html", "markdown", "txt"
        ]
        
    def export_data(self, data: Dict, format_type: str, output_path: str = None, 
                   include_metadata: bool = True) -> str:
        """Export data in specified format"""
        
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"/home/kali/Desktop/tools/osint-eye/exports/export_{timestamp}.{format_type}"
        
        # Ensure export directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Add metadata if requested
        if include_metadata:
            data = self._add_export_metadata(data)
        
        # Export based on format
        if format_type == "json":
            return self._export_json(data, output_path)
        elif format_type == "csv":
            return self._export_csv(data, output_path)
        elif format_type == "xml":
            return self._export_xml(data, output_path)
        elif format_type == "xlsx":
            return self._export_xlsx(data, output_path)
        elif format_type == "yaml":
            return self._export_yaml(data, output_path)
        elif format_type == "sqlite":
            return self._export_sqlite(data, output_path)
        elif format_type == "html":
            return self._export_html(data, output_path)
        elif format_type == "markdown":
            return self._export_markdown(data, output_path)
        elif format_type == "txt":
            return self._export_txt(data, output_path)
    
    def _add_export_metadata(self, data: Dict) -> Dict:
        """Add export metadata to data"""
        metadata = {
            "export_timestamp": datetime.now().isoformat(),
            "export_version": "1.0",
            "exported_by": "OSINT-Eye Advanced Exporter",
            "data_structure_version": "2.0"
        }
        
        if isinstance(data, dict):
            data["_export_metadata"] = metadata
        else:
            data = {
                "_export_metadata": metadata,
                "data": data
            }
        
        return data
    
    def _export_json(self, data: Dict, output_path: str) -> str:
        """Export data as JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return output_path
    
    def _export_csv(self, data: Dict, output_path: str) -> str:
        """Export data as CSV"""
        # Flatten nested data for CSV export
        flattened_data = self._flatten_data_for_csv(data)
        
        if not flattened_data:
            # Create empty CSV with headers
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["No data available"])
            return output_path
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if isinstance(flattened_data, list) and flattened_data:
                fieldnames = flattened_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_data)
            else:
                writer = csv.writer(f)
                for key, value in flattened_data.items():
                    writer.writerow([key, str(value)])
        
        return output_path
    
    def _export_xml(self, data: Dict, output_path: str) -> str:
        """Export data as XML"""
        root = ET.Element("osint_data")
        self._dict_to_xml(data, root)
        
        # Pretty print XML
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        return output_path
    
    def _export_xlsx(self, data: Dict, output_path: str) -> str:
        """Export data as Excel file"""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Handle different data structures
            if isinstance(data, dict):
                for sheet_name, sheet_data in data.items():
                    if isinstance(sheet_data, (list, dict)):
                        df = self._convert_to_dataframe(sheet_data)
                        safe_sheet_name = str(sheet_name)[:31]  # Excel sheet name limit
                        df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                    else:
                        # Single value data
                        df = pd.DataFrame([{sheet_name: sheet_data}])
                        df.to_excel(writer, sheet_name="Data", index=False)
            else:
                df = self._convert_to_dataframe(data)
                df.to_excel(writer, sheet_name="Data", index=False)
        
        return output_path
    
    def _export_yaml(self, data: Dict, output_path: str) -> str:
        """Export data as YAML"""
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        return output_path
    
    def _export_sqlite(self, data: Dict, output_path: str) -> str:
        """Export data to SQLite database"""
        conn = sqlite3.connect(output_path)
        cursor = conn.cursor()
        
        try:
            # Create tables based on data structure
            self._create_sqlite_tables(data, cursor)
            
            # Insert data
            self._insert_sqlite_data(data, cursor)
            
            conn.commit()
        finally:
            conn.close()
        
        return output_path
    
    def _export_html(self, data: Dict, output_path: str) -> str:
        """Export data as HTML report"""
        html_content = self._generate_html_report(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _export_markdown(self, data: Dict, output_path: str) -> str:
        """Export data as Markdown"""
        markdown_content = self._generate_markdown_report(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return output_path
    
    def _export_txt(self, data: Dict, output_path: str) -> str:
        """Export data as plain text"""
        text_content = self._generate_text_report(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return output_path
    
    def _flatten_data_for_csv(self, data: Any, parent_key: str = '', sep: str = '_') -> List[Dict]:
        """Flatten nested data structure for CSV export"""
        if isinstance(data, dict):
            items = []
            for k, v in data.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(self._flatten_dict(v, new_key, sep).items())
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        if isinstance(item, dict):
                            items.extend(self._flatten_dict(item, f"{new_key}{sep}{i}", sep).items())
                        else:
                            items.append((f"{new_key}{sep}{i}", str(item)))
                else:
                    items.append((new_key, str(v)))
            return [dict(items)]
        elif isinstance(data, list):
            result = []
            for item in data:
                if isinstance(item, dict):
                    result.append(self._flatten_dict(item, '', sep))
                else:
                    result.append({"value": str(item)})
            return result
        else:
            return [{"value": str(data)}]
    
    def _flatten_dict(self, data: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten a nested dictionary"""
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(self._flatten_dict(item, f"{new_key}{sep}{i}", sep).items())
                    else:
                        items.append((f"{new_key}{sep}{i}", str(item)))
            else:
                items.append((new_key, str(v)))
        return dict(items)
    
    def _dict_to_xml(self, data: Any, parent: ET.Element):
        """Convert dictionary to XML elements"""
        if isinstance(data, dict):
            for key, value in data.items():
                # Clean key name for XML
                clean_key = re.sub(r'[^a-zA-Z0-9_]', '_', str(key))
                element = ET.SubElement(parent, clean_key)
                self._dict_to_xml(value, element)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                element = ET.SubElement(parent, f"item_{i}")
                self._dict_to_xml(item, element)
        else:
            parent.text = str(data)
    
    def _convert_to_dataframe(self, data: Any) -> pd.DataFrame:
        """Convert data to pandas DataFrame"""
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                return pd.DataFrame(data)
            else:
                return pd.DataFrame({"values": data})
        elif isinstance(data, dict):
            # Try to create DataFrame from dict
            try:
                return pd.DataFrame([data])
            except:
                # If that fails, create key-value pairs
                return pd.DataFrame(list(data.items()), columns=["key", "value"])
        else:
            return pd.DataFrame([{"value": str(data)}])
    
    def _create_sqlite_tables(self, data: Dict, cursor: sqlite3.Cursor):
        """Create SQLite tables based on data structure"""
        # Create main profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                platform TEXT,
                followers INTEGER,
                following INTEGER,
                posts INTEGER,
                verified BOOLEAN,
                bio TEXT,
                profile_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create analysis results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                analysis_type TEXT,
                score REAL,
                confidence REAL,
                results TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES profiles (id)
            )
        ''')
        
        # Create threat intelligence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                threat_type TEXT,
                severity TEXT,
                confidence REAL,
                indicators TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES profiles (id)
            )
        ''')
    
    def _insert_sqlite_data(self, data: Dict, cursor: sqlite3.Cursor):
        """Insert data into SQLite tables"""
        # This is a simplified implementation
        # In practice, you'd parse the specific data structure
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) and "username" in value:
                    # Insert profile data
                    cursor.execute('''
                        INSERT INTO profiles (username, platform, followers, following, posts, verified, bio, profile_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        value.get("username", ""),
                        value.get("platform", ""),
                        value.get("followers", 0),
                        value.get("following", 0),
                        value.get("posts", 0),
                        value.get("verified", False),
                        value.get("bio", ""),
                        value.get("profile_url", "")
                    ))
    
    def _generate_html_report(self, data: Dict) -> str:
        """Generate HTML report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OSINT-Eye Export Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .data-table {{ width: 100%; border-collapse: collapse; }}
                .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .data-table th {{ background-color: #f2f2f2; }}
                .threat-high {{ color: red; font-weight: bold; }}
                .threat-medium {{ color: orange; font-weight: bold; }}
                .threat-low {{ color: green; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>OSINT-Eye Export Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        """
        
        # Add data sections
        for key, value in data.items():
            if key.startswith('_'):
                continue  # Skip metadata
            
            html += f'<div class="section"><h2>{key.replace("_", " ").title()}</h2>'
            
            if isinstance(value, dict):
                html += '<table class="data-table"><tr><th>Property</th><th>Value</th></tr>'
                for k, v in value.items():
                    html += f'<tr><td>{k}</td><td>{str(v)}</td></tr>'
                html += '</table>'
            elif isinstance(value, list):
                html += '<ul>'
                for item in value:
                    html += f'<li>{str(item)}</li>'
                html += '</ul>'
            else:
                html += f'<p>{str(value)}</p>'
            
            html += '</div>'
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _generate_markdown_report(self, data: Dict) -> str:
        """Generate Markdown report"""
        markdown = f"""# OSINT-Eye Export Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
        
        for key, value in data.items():
            if key.startswith('_'):
                continue  # Skip metadata
            
            markdown += f"## {key.replace('_', ' ').title()}\n\n"
            
            if isinstance(value, dict):
                for k, v in value.items():
                    markdown += f"- **{k}:** {str(v)}\n"
            elif isinstance(value, list):
                for item in value:
                    markdown += f"- {str(item)}\n"
            else:
                markdown += f"{str(value)}\n"
            
            markdown += "\n---\n\n"
        
        return markdown
    
    def _generate_text_report(self, data: Dict) -> str:
        """Generate plain text report"""
        text = f"OSINT-Eye Export Report\n"
        text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += "=" * 50 + "\n\n"
        
        def format_data(obj, indent=0):
            result = ""
            spaces = "  " * indent
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.startswith('_'):
                        continue
                    result += f"{spaces}{key}:\n"
                    result += format_data(value, indent + 1)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    result += f"{spaces}[{i}] "
                    result += format_data(item, indent + 1)
            else:
                result += f"{spaces}{str(obj)}\n"
            
            return result
        
        text += format_data(data)
        return text
    
    def batch_export(self, data: Dict, formats: List[str], 
                    base_path: str = None) -> Dict[str, str]:
        """Export data in multiple formats"""
        if base_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_path = f"/home/kali/Desktop/tools/osint-eye/exports/batch_export_{timestamp}"
        
        results = {}
        
        for format_type in formats:
            try:
                output_path = f"{base_path}.{format_type}"
                exported_path = self.export_data(data, format_type, output_path)
                results[format_type] = exported_path
            except Exception as e:
                results[format_type] = f"Error: {str(e)}"
        
        return results
    
    def create_api_endpoint_data(self, data: Dict) -> Dict:
        """Format data for API endpoint consumption"""
        api_data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "data": data,
            "metadata": {
                "total_records": self._count_records(data),
                "data_types": self._identify_data_types(data),
                "export_format": "api_json"
            }
        }
        
        return api_data
    
    def _count_records(self, data: Any) -> int:
        """Count total records in data"""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            count = 0
            for value in data.values():
                if isinstance(value, (list, dict)):
                    count += self._count_records(value)
                else:
                    count += 1
            return count
        else:
            return 1
    
    def _identify_data_types(self, data: Any) -> List[str]:
        """Identify data types present in the data"""
        types = set()
        
        if isinstance(data, dict):
            for key, value in data.items():
                if "profile" in key.lower():
                    types.add("profile_data")
                elif "analysis" in key.lower():
                    types.add("analysis_results")
                elif "threat" in key.lower():
                    types.add("threat_intelligence")
                elif "network" in key.lower():
                    types.add("network_data")
                else:
                    types.add("general_data")
        
        return list(types)