// This script will handle rendering of Jupyter notebooks
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on a page with a notebook
    const notebookContainer = document.querySelector('.notebook-container');
    if (!notebookContainer) return;
    
    // Function to fetch and render a notebook
    const renderNotebook = async (notebookPath) => {
        try {
            const response = await fetch(notebookPath);
            if (!response.ok) {
                throw new Error(`Failed to load notebook: ${response.status} ${response.statusText}`);
            }
            
            const notebook = await response.json();
            
            // Clear the container
            notebookContainer.innerHTML = '';
            
            // Render each cell
            notebook.cells.forEach((cell, index) => {
                const cellElement = document.createElement('div');
                cellElement.classList.add('notebook-cell');
                
                // Different rendering based on cell type
                if (cell.cell_type === 'markdown') {
                    cellElement.classList.add('markdown-cell');
                    // Use a markdown library like marked.js here
                    // For now, just add the raw markdown
                    cellElement.innerHTML = `<div class="cell-content">${cell.source.join('')}</div>`;
                } 
                else if (cell.cell_type === 'code') {
                    cellElement.classList.add('code-cell');
                    
                    // Code source
                    const codeElement = document.createElement('div');
                    codeElement.classList.add('cell-input');
                    codeElement.innerHTML = `<pre><code>${cell.source.join('')}</code></pre>`;
                    cellElement.appendChild(codeElement);
                    
                    // Code output (if any)
                    if (cell.outputs && cell.outputs.length > 0) {
                        const outputElement = document.createElement('div');
                        outputElement.classList.add('cell-output');
                        
                        cell.outputs.forEach(output => {
                            if (output.output_type === 'execute_result' || output.output_type === 'display_data') {
                                // Handle different mimetypes
                                if (output.data && output.data['text/html']) {
                                    outputElement.innerHTML += output.data['text/html'].join('');
                                } 
                                else if (output.data && output.data['image/png']) {
                                    outputElement.innerHTML += `<img src="data:image/png;base64,${output.data['image/png']}" />`;
                                }
                                else if (output.data && output.data['text/plain']) {
                                    outputElement.innerHTML += `<pre>${output.data['text/plain'].join('')}</pre>`;
                                }
                            } 
                            else if (output.output_type === 'stream') {
                                outputElement.innerHTML += `<pre>${output.text.join('')}</pre>`;
                            }
                        });
                        
                        cellElement.appendChild(outputElement);
                    }
                }
                
                notebookContainer.appendChild(cellElement);
            });
            
        } catch (error) {
            console.error('Error rendering notebook:', error);
            notebookContainer.innerHTML = `<div class="error">Failed to load notebook: ${error.message}</div>`;
        }
    };
    
    // Get the notebook path from the container's data attribute
    const notebookPath = notebookContainer.getAttribute('data-notebook-path');
    if (notebookPath) {
        renderNotebook(notebookPath);
    } else {
        notebookContainer.innerHTML = `<div class="error">No notebook path specified</div>`;
    }
});