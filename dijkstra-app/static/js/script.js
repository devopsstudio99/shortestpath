document.addEventListener('DOMContentLoaded', function() {
    const findPathBtn = document.getElementById('findPathBtn');
    const newGraphBtn = document.getElementById('newGraphBtn');
    const startNodeSelect = document.getElementById('startNode');
    const endNodeSelect = document.getElementById('endNode');
    const resultDiv = document.getElementById('result');
    const graphImage = document.getElementById('graph-image');
    
    findPathBtn.addEventListener('click', async function() {
        const startNode = startNodeSelect.value;
        const endNode = endNodeSelect.value;
        
        if (startNode === endNode) {
            resultDiv.innerHTML = '<div class="alert alert-warning">Start and end nodes must be different!</div>';
            return;
        }
        
        // แสดงการโหลด
        resultDiv.innerHTML = '<p class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></p>';
        graphImage.classList.add('loading');
        
        try {
            const response = await fetch('/find_path', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    start: startNode,
                    end: endNode
                })
            });
            
            const data = await response.json();
            
            if (data.length === -1) {
                resultDiv.innerHTML = '<div class="alert alert-danger">No path exists between these nodes!</div>';
            } else {
                const pathString = data.path.map(node => `Node \${node}`).join(' → ');
                resultDiv.innerHTML = `
                    <p class="result-path">\${pathString}</p>
                    <p>Total distance: <span class="result-length">\${data.length}</span></p>
                `;
                
                // อัปเดตรูปภาพกราฟ
                graphImage.src = "data:image/png;base64," + data.graph_image;
            }
        } catch (error) {
            resultDiv.innerHTML = `<div class="alert alert-danger">Error: \${error.message}</div>`;
        } finally {
            graphImage.classList.remove('loading');
        }
    });
    
    newGraphBtn.addEventListener('click', async function() {
        // แสดงการโหลด
        resultDiv.innerHTML = '<p class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></p>';
        graphImage.classList.add('loading');
        
        try {
            const response = await fetch('/new_graph', {
                method: 'POST',
            });
            
            const data = await response.json();
            
            // อัปเดตรูปภาพกราฟ
            graphImage.src = "data:image/png;base64," + data.graph_image;
            
            // รีเซ็ตผลลัพธ์
            resultDiv.innerHTML = '<p>Select start and end nodes, then click "Find Shortest Path".</p>';
            
        } catch (error) {
            resultDiv.innerHTML = `<div class="alert alert-danger">Error: \${error.message}</div>`;
        } finally {
            graphImage.classList.remove('loading');
        }
    });
});
