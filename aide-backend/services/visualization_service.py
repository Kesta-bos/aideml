"""
Visualization Service

Generates tree visualizations for AIDE experiments using the existing visualization code.
"""

import json
import logging
import textwrap
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np

logger = logging.getLogger("aide")

# Import AIDE utilities if available
try:
    import sys
    aide_path = Path(__file__).parent.parent.parent / "aide"
    sys.path.insert(0, str(aide_path))
    from utils.tree_export import cfg_to_tree_struct, generate_html
    AIDE_AVAILABLE = True
except ImportError:
    logger.warning("AIDE tree export utilities not available")
    AIDE_AVAILABLE = False


class VisualizationService:
    """Service for generating experiment visualizations."""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent.parent / "aide" / "utils" / "viz_templates"
        
    def _mock_journal_node(self, step: int, plan: str, code: str, term_out: str = "", analysis: str = ""):
        """Create a mock journal node for testing purposes."""
        class MockNode:
            def __init__(self, step, plan, code, term_out="", analysis=""):
                self.step = step
                self.plan = plan
                self.code = code
                self.term_out = term_out
                self.analysis = analysis
                self.children = []
                
        return MockNode(step, plan, code, term_out, analysis)
    
    def _create_mock_tree_structure(self) -> Dict[str, Any]:
        """Create a mock tree structure for demonstration."""
        # Simple tree: root -> plan1 -> plan2
        #                   -> plan3
        edges = [(0, 1), (1, 2), (0, 3)]
        layout = [
            [0.5, 1.0],  # root
            [0.3, 0.6],  # plan1
            [0.3, 0.2],  # plan2
            [0.7, 0.6],  # plan3
        ]
        
        plans = [
            "Initial data exploration and understanding",
            "Try basic linear regression model",
            "Improve model with feature engineering",
            "Try ensemble methods (Random Forest)"
        ]
        
        codes = [
            "# Data exploration\nimport pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())",
            "# Linear regression\nfrom sklearn.linear_model import LinearRegression\nmodel = LinearRegression()\nmodel.fit(X_train, y_train)",
            "# Feature engineering\nX_engineered = create_polynomial_features(X)\nmodel.fit(X_engineered, y_train)",
            "# Random Forest\nfrom sklearn.ensemble import RandomForestRegressor\nrf = RandomForestRegressor(n_estimators=100)\nrf.fit(X_train, y_train)"
        ]
        
        term_outs = [
            "Data loaded successfully. Shape: (1000, 10)",
            "Model trained. R² score: 0.65",
            "Improved model. R² score: 0.78",
            "Random Forest trained. R² score: 0.82"
        ]
        
        analyses = [
            "Data looks clean with some missing values in column 'age'",
            "Baseline model shows decent performance but could be improved",
            "Feature engineering significantly improved model performance",
            "Random Forest achieved best performance so far"
        ]
        
        return {
            "edges": edges,
            "layout": layout,
            "plan": plans,
            "code": codes,
            "term_out": term_outs,
            "analysis": analyses,
            "exp_name": "Sample ML Experiment",
            "metrics": [0.0, 0.65, 0.78, 0.82]
        }
    
    def generate_tree_visualization_html(self, experiment_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate HTML for tree visualization.
        
        Args:
            experiment_data: Experiment data structure or None for mock data
            
        Returns:
            HTML string for the visualization
        """
        try:
            # Use provided data or create mock data
            if experiment_data:
                tree_data = experiment_data
            else:
                tree_data = self._create_mock_tree_structure()
            
            # Generate the HTML
            tree_graph_str = json.dumps(tree_data)
            
            if AIDE_AVAILABLE and self.template_dir.exists():
                # Use the actual AIDE template
                return self._generate_html_from_template(tree_graph_str)
            else:
                # Use embedded template as fallback
                return self._generate_embedded_html(tree_graph_str)
                
        except Exception as e:
            logger.error(f"Error generating tree visualization: {e}")
            return self._generate_error_html(str(e))
    
    def _generate_html_from_template(self, tree_graph_str: str) -> str:
        """Generate HTML using the AIDE template files."""
        try:
            # Read template files
            with open(self.template_dir / "template.js") as f:
                js = f.read()
                js = js.replace("<placeholder>", tree_graph_str)

            with open(self.template_dir / "template.html") as f:
                html = f.read()
                html = html.replace("<!-- placeholder -->", js)

            return html
        except Exception as e:
            logger.error(f"Error reading template files: {e}")
            return self._generate_embedded_html(tree_graph_str)
    
    def _generate_embedded_html(self, tree_graph_str: str) -> str:
        """Generate HTML with embedded template (fallback)."""
        return f"""
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
    <title>AIDE Tree Visualization</title>
    <style>
        body, * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background-color: #f2f0e7;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }}
        .container {{
            display: flex;
            height: 100vh;
        }}
        .tree-canvas {{
            flex: 1;
            background-color: #f2f0e7;
            border-right: 2px solid #282c34;
        }}
        .details-panel {{
            flex: 1;
            background-color: #282c34;
            color: #f2f0e7;
            overflow-y: auto;
            padding: 20px;
        }}
        .node-details {{
            margin-bottom: 20px;
        }}
        .node-details h3 {{
            color: #fd4578;
            margin-bottom: 10px;
        }}
        .code-block {{
            background-color: #1e2227;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 10px 0;
        }}
        .tree-node {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .tree-node:hover {{
            opacity: 0.8;
        }}
        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-size: 18px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div id="tree-canvas" class="tree-canvas"></div>
        <div class="details-panel">
            <div id="node-details">
                <h2>AIDE Experiment Tree</h2>
                <p>Click on a node to view details</p>
                <div class="node-details">
                    <h3>Instructions:</h3>
                    <ul>
                        <li>Each circle represents a step in the ML experiment</li>
                        <li>Lines show the progression between steps</li>
                        <li>Click on any node to see the plan, code, and results</li>
                        <li>Hover over nodes to highlight them</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Tree data
        const treeData = {tree_graph_str};
        
        let selectedNode = 0;
        let canvas;
        
        function setup() {{
            canvas = createCanvas(document.getElementById('tree-canvas').offsetWidth, window.innerHeight);
            canvas.parent('tree-canvas');
            
            // Display first node by default
            displayNodeDetails(0);
        }}
        
        function draw() {{
            background('#f2f0e7');
            
            if (!treeData || !treeData.layout) return;
            
            const nodes = treeData.layout;
            const edges = treeData.edges || [];
            
            // Draw edges
            stroke('#666');
            strokeWeight(2);
            for (let edge of edges) {{
                const from = nodes[edge[0]];
                const to = nodes[edge[1]];
                line(
                    from[0] * width, from[1] * height,
                    to[0] * width, to[1] * height
                );
            }}
            
            // Draw nodes
            for (let i = 0; i < nodes.length; i++) {{
                const node = nodes[i];
                const x = node[0] * width;
                const y = node[1] * height;
                
                // Highlight selected node
                if (i === selectedNode) {{
                    fill('#fd4578');
                    stroke('#fff');
                    strokeWeight(3);
                }} else {{
                    fill('#282c34');
                    stroke('#fff');
                    strokeWeight(2);
                }}
                
                circle(x, y, 40);
                
                // Node number
                fill('#fff');
                noStroke();
                textAlign(CENTER, CENTER);
                textSize(16);
                text(i, x, y);
            }}
        }}
        
        function mousePressed() {{
            if (!treeData || !treeData.layout) return;
            
            const nodes = treeData.layout;
            for (let i = 0; i < nodes.length; i++) {{
                const node = nodes[i];
                const x = node[0] * width;
                const y = node[1] * height;
                
                if (dist(mouseX, mouseY, x, y) < 20) {{
                    selectedNode = i;
                    displayNodeDetails(i);
                    break;
                }}
            }}
        }}
        
        function displayNodeDetails(nodeIndex) {{
            const details = document.getElementById('node-details');
            const plan = treeData.plan[nodeIndex] || 'No plan available';
            const code = treeData.code[nodeIndex] || 'No code available';
            const termOut = treeData.term_out[nodeIndex] || 'No output available';
            const analysis = treeData.analysis[nodeIndex] || 'No analysis available';
            
            details.innerHTML = `
                <h2>Node ${{nodeIndex}}: Step Details</h2>
                
                <div class="node-details">
                    <h3>Plan:</h3>
                    <div class="code-block">${{plan}}</div>
                </div>
                
                <div class="node-details">
                    <h3>Code:</h3>
                    <div class="code-block"><pre><code class="language-python">${{code}}</code></pre></div>
                </div>
                
                <div class="node-details">
                    <h3>Output:</h3>
                    <div class="code-block">${{termOut}}</div>
                </div>
                
                <div class="node-details">
                    <h3>Analysis:</h3>
                    <div class="code-block">${{analysis}}</div>
                </div>
            `;
            
            // Re-highlight code
            hljs.highlightAll();
        }}
        
        function windowResized() {{
            resizeCanvas(document.getElementById('tree-canvas').offsetWidth, window.innerHeight);
        }}
        
        // Initialize highlighting
        hljs.highlightAll();
    </script>
</body>
</html>
"""
    
    def _generate_error_html(self, error_message: str) -> str:
        """Generate error HTML when visualization fails."""
        return f"""
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Visualization Error</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f5f5f5;
        }}
        .error-container {{
            text-align: center;
            padding: 40px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 500px;
        }}
        .error-title {{
            color: #e74c3c;
            margin-bottom: 20px;
        }}
        .error-message {{
            color: #666;
            font-size: 14px;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #e74c3c;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <h2 class="error-title">Visualization Error</h2>
        <p>Sorry, we couldn't generate the tree visualization.</p>
        <div class="error-message">
            Error: {error_message}
        </div>
    </div>
</body>
</html>
"""

    async def get_experiment_tree_html(self, experiment_id: str) -> str:
        """
        Get tree visualization HTML for a specific experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            HTML string for the visualization
        """
        try:
            # TODO: Load actual experiment data from the experiment service
            # For now, return mock visualization
            logger.info(f"Generating tree visualization for experiment {experiment_id}")
            return self.generate_tree_visualization_html()
            
        except Exception as e:
            logger.error(f"Error generating tree visualization for experiment {experiment_id}: {e}")
            return self._generate_error_html(str(e))