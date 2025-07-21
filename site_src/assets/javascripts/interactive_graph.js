// Interactive Graph JavaScript for D&D Campaign Relationships

document.addEventListener('DOMContentLoaded', function() {
    // Initialize interactive graph functionality
    
    function draw_graph_sidebar(chartContainer, global = false) {
        if (!chartContainer) return;
        
        const myChart = echarts.init(chartContainer);
        
        // D&D Campaign Graph Data
        const graphData = {
            nodes: [
                {id: 'house-talzar', name: 'House T\'alzar', category: 'faction', symbolSize: 50},
                {id: 'valandor', name: 'Valandor T\'alzar', category: 'character', symbolSize: 40},
                {id: 'bentham', name: 'Bentham', category: 'character', symbolSize: 35},
                {id: 'malagar', name: 'Malagar', category: 'character', symbolSize: 35},
                {id: 'haribo', name: 'Haribo', category: 'character', symbolSize: 35},
                {id: 'clank', name: 'Clank', category: 'character', symbolSize: 35},
                {id: 'ravithar', name: 'Rav\'ithar', category: 'character', symbolSize: 35},
                {id: 'zyntra', name: 'Zyntra', category: 'character', symbolSize: 35},
                {id: 'cinderfork', name: 'Cinderfork Foundry', category: 'location', symbolSize: 45},
                {id: 'black-mithril', name: 'Black Mithril', category: 'item', symbolSize: 30},
                {id: 'glutthraz', name: 'House Glutthraz', category: 'faction', symbolSize: 40}
            ],
            links: [
                {source: 'house-talzar', target: 'valandor', relation: 'family'},
                {source: 'house-talzar', target: 'bentham', relation: 'servant'},
                {source: 'house-talzar', target: 'malagar', relation: 'family'},
                {source: 'house-talzar', target: 'haribo', relation: 'ally'},
                {source: 'house-talzar', target: 'clank', relation: 'employee'},
                {source: 'house-talzar', target: 'ravithar', relation: 'member'},
                {source: 'house-talzar', target: 'zyntra', relation: 'member'},
                {source: 'valandor', target: 'cinderfork', relation: 'imprisoned'},
                {source: 'cinderfork', target: 'black-mithril', relation: 'produces'},
                {source: 'glutthraz', target: 'cinderfork', relation: 'controls'},
                {source: 'house-talzar', target: 'glutthraz', relation: 'enemy'}
            ]
        };
        
        const categories = [
            {name: 'character', itemStyle: {color: '#9c27b0'}},
            {name: 'location', itemStyle: {color: '#4ecdc4'}},
            {name: 'faction', itemStyle: {color: '#ff6b6b'}},
            {name: 'item', itemStyle: {color: '#ffa726'}}
        ];
        
        const option = {
            tooltip: {
                formatter: function(params) {
                    if (params.dataType === 'node') {
                        return `<strong>${params.data.name}</strong><br/>Category: ${params.data.category}`;
                    } else if (params.dataType === 'edge') {
                        return `${params.data.source} → ${params.data.target}<br/>Relation: ${params.data.relation}`;
                    }
                }
            },
            legend: {
                data: categories.map(c => c.name),
                bottom: 10
            },
            series: [{
                type: 'graph',
                layout: 'force',
                data: graphData.nodes,
                links: graphData.links,
                categories: categories,
                roam: true,
                focusNodeAdjacency: true,
                itemStyle: {
                    borderColor: '#fff',
                    borderWidth: 1,
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.3)'
                },
                label: {
                    show: true,
                    position: 'bottom',
                    formatter: '{b}'
                },
                lineStyle: {
                    color: 'source',
                    curveness: 0.3,
                    opacity: 0.6
                },
                emphasis: {
                    focus: 'adjacency',
                    lineStyle: {
                        width: 10
                    }
                },
                force: {
                    repulsion: 1000,
                    gravity: 0.1,
                    edgeLength: 100,
                    layoutAnimation: true
                }
            }]
        };
        
        myChart.setOption(option);
        
        // Handle resize
        window.addEventListener('resize', function() {
            myChart.resize();
        });
    }
    
    // Initialize sidebar graphs
    const sidebarGraphs = document.querySelectorAll('.graph-sidebar');
    sidebarGraphs.forEach(graph => {
        draw_graph_sidebar(graph, false);
    });
    
    // Initialize full-size graphs
    const containerGraphs = document.querySelectorAll('.graph-container');
    containerGraphs.forEach(graph => {
        draw_graph_sidebar(graph, true);
    });
    
    // Modal functionality for full-screen graph view
    const graphButtons = document.querySelectorAll('.graph-button');
    graphButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            openGraphModal();
        });
    });
    
    function openGraphModal() {
        const modal = document.getElementById('graph-modal');
        if (!modal) {
            createGraphModal();
        } else {
            modal.style.display = 'block';
        }
    }
    
    function createGraphModal() {
        const modal = document.createElement('div');
        modal.id = 'graph-modal';
        modal.className = 'graph-modal';
        modal.innerHTML = `
            <div class="graph-modal-content">
                <span class="graph-close">&times;</span>
                <div id="full-graph" style="width: 100%; height: calc(100% - 40px);"></div>
            </div>
        `;
        document.body.appendChild(modal);
        
        const closeBtn = modal.querySelector('.graph-close');
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
        
        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
        
        modal.style.display = 'block';
        
        // Initialize the full graph
        const fullGraph = document.getElementById('full-graph');
        draw_graph_sidebar(fullGraph, true);
    }
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { draw_graph_sidebar };
} 